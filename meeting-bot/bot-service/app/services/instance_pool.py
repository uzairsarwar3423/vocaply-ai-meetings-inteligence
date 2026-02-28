"""
Instance Pool Manager
Maintains pool of pre-warmed bots ready for assignment
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from app.config import settings
from app.models.bot_instance import BotInstance
from shared.models.bot_status import BotStatus, BotPlatform
from shared.utils.redis_client import RedisClient
from shared.utils.logger import logger


class InstancePool:
    """
    Manages pool of bot instances.
    
    Lifecycle:
    1. Pre-warm N bots on startup
    2. Assign available bots to meetings
    3. Refill pool when available < threshold
    4. Scale down idle bots after timeout
    """

    def __init__(self, redis: RedisClient):
        self.redis = redis
        self.bots: Dict[str, BotInstance] = {}  # bot_id → BotInstance
        self._refill_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start(self):
        """Initialize pool"""
        logger.info(f"Starting bot pool (pre-warm: {settings.POOL_PRE_WARM})")
        
        # Cleanup stale bots from Redis (shared across service restarts)
        await self._cleanup_redis_state()
        
        # Pre-warm bots
        await self._create_bots(settings.POOL_PRE_WARM)
        
        # Start background tasks
        self._refill_task = asyncio.create_task(self._auto_refill())
        self._monitor_task = asyncio.create_task(self._monitor_health())
        
        logger.info(f"Bot pool started with {len(self.bots)} bots")

    async def stop(self):
        """Shutdown pool"""
        logger.info("Stopping bot pool")
        
        # Cancel background tasks
        if self._refill_task:
            self._refill_task.cancel()
        if self._monitor_task:
            self._monitor_task.cancel()
        
        # Terminate all bots
        tasks = [bot.terminate() for bot in self.bots.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.bots.clear()
        logger.info("Bot pool stopped")

    async def _cleanup_redis_state(self):
        """Clear existing bot registry in Redis for fresh start"""
        logger.info("Cleaning up stale bot registry in Redis")
        await self.redis.client.delete("bot:pool:available")
        await self.redis.client.delete("bot:pool:in_use")
        
        # Cleanup any individual bot keys (optional, but keep Redis clean)
        keys = await self.redis.client.keys("bot:*")
        if keys:
            await self.redis.client.delete(*keys)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # BOT MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def create_bot(self) -> BotInstance:
        """Create a single bot and add to pool"""
        if len(self.bots) >= settings.POOL_MAX_SIZE:
            raise RuntimeError(f"Pool at max size ({settings.POOL_MAX_SIZE})")
        
        bot = BotInstance()
        
        try:
            await bot.initialize()
            self.bots[bot.bot_id] = bot
            
            # Add to Redis
            await self.redis.set_bot(bot.bot_id, bot.data.dict())
            await self.redis.add_to_pool(bot.bot_id, available=True)
            
            logger.info(f"Created bot {bot.bot_id}")
            return bot
            
        except Exception as e:
            logger.error(f"Failed to create bot: {e}", exc_info=True)
            # Cleanup failed bot
            if bot.bot_id in self.bots:
                del self.bots[bot.bot_id]
            await bot.terminate()
            raise

    async def _create_bots(self, count: int):
        """Create multiple bots concurrently"""
        tasks = [self.create_bot() for _ in range(count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log failures
        failures = [r for r in results if isinstance(r, Exception)]
        if failures:
            logger.warning(f"Failed to create {len(failures)} bots")

    async def assign_bot(
        self,
        meeting_url: str,
        meeting_id: str,
        company_id: str,
        platform: BotPlatform,
    ) -> Optional[BotInstance]:
        """Assign an available bot to a meeting"""
        # Get available bot from pool
        available = await self.redis.get_available_bots()
        if not available:
            logger.warning("No available bots in pool")
            return None
        
        bot_id = available[0]
        bot = self.bots.get(bot_id)
        
        if not bot:
            logger.error(f"Bot {bot_id} in Redis but not in memory")
            await self.redis.remove_from_pool(bot_id)
            return None
        
        try:
            # Assign bot
            await bot.assign(meeting_url, meeting_id, company_id, platform)
            
            # Update Redis
            await self.redis.move_to_in_use(bot_id)
            await self.redis.add_company_bot(company_id, bot_id)
            await self.redis.set_bot(bot_id, bot.data.dict())
            
            logger.info(f"Assigned bot {bot_id} to meeting {meeting_id}")
            return bot
            
        except Exception as e:
            logger.error(f"Failed to assign bot {bot_id}: {e}", exc_info=True)
            return None

    async def release_bot(self, bot_id: str):
        """Return bot to available pool"""
        bot = self.bots.get(bot_id)
        if not bot:
            return
        
        # Terminate and recreate (fresh state)
        await bot.terminate()
        del self.bots[bot_id]
        
        await self.redis.remove_from_pool(bot_id)
        await self.redis.delete_bot(bot_id)
        
        if bot.data.company_id:
            await self.redis.remove_company_bot(bot.data.company_id, bot_id)
        
        # Create new bot to replace it
        try:
            await self.create_bot()
        except Exception as e:
            logger.error(f"Failed to recreate bot: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # POOL OPERATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def get_pool_status(self) -> Dict:
        """Get current pool metrics"""
        available, in_use = await self.redis.pool_size()
        
        return {
            "total": len(self.bots),
            "available": available,
            "in_use": in_use,
            "max_size": settings.POOL_MAX_SIZE,
            "min_size": settings.POOL_MIN_SIZE,
            "bots": [
                {
                    "bot_id": bot.bot_id,
                    "status": bot.data.status,
                    "meeting_id": bot.data.meeting_id,
                    "platform": bot.data.platform,
                    "created_at": bot.data.created_at.isoformat(),
                }
                for bot in self.bots.values()
            ],
        }

    async def _auto_refill(self):
        """Background task: refill pool when depleted"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                available, in_use = await self.redis.pool_size()
                
                # Refill if below threshold
                if available < settings.POOL_REFILL_THRESHOLD:
                    needed = settings.POOL_MIN_SIZE - available
                    needed = min(needed, settings.POOL_MAX_SIZE - len(self.bots))
                    
                    if needed > 0:
                        logger.info(f"Refilling pool with {needed} bots")
                        await self._create_bots(needed)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-refill error: {e}", exc_info=True)

    async def _monitor_health(self):
        """Background task: monitor bot health"""
        while True:
            try:
                await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
                
                for bot in list(self.bots.values()):
                    # Check if bot is stuck
                    if bot.data.status == BotStatus.JOINING:
                        elapsed = (datetime.utcnow() - bot.data.assigned_at).total_seconds()
                        if elapsed > settings.BOT_JOIN_TIMEOUT:
                            logger.warning(f"Bot {bot.bot_id} stuck joining, terminating")
                            await self.release_bot(bot.bot_id)
                    
                    # Check participant count
                    if bot.data.status in (BotStatus.IN_MEETING, BotStatus.RECORDING):
                        await bot.check_participants()
                        
                        if bot.should_leave():
                            logger.info(f"Bot {bot.bot_id} should leave, initiating cleanup")
                            asyncio.create_task(self._cleanup_bot(bot.bot_id))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}", exc_info=True)

    async def _cleanup_bot(self, bot_id: str):
        """Leave meeting and release bot"""
        bot = self.bots.get(bot_id)
        if not bot:
            return
        
        try:
            await bot.leave()
        except Exception as e:
            logger.error(f"Error leaving meeting: {e}")
        
        await self.release_bot(bot_id)