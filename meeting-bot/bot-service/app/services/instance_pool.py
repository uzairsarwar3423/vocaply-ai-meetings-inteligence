"""
Bot Instance Pool
Vocaply AI Meeting Intelligence - Day 15

Maintains a pool of pre-warmed bot containers to minimize join latency.
"""

import asyncio
import uuid
from typing import List, Dict
from app.config import settings
from app.models.bot_instance import BotInstance
from shared.utils.logger import get_logger
from .redis_state import state_service

logger = get_logger("instance-pool")

class InstancePool:
    def __init__(self):
        self._instances: Dict[str, BotInstance] = {}
        self._lock = asyncio.Lock()

    async def start(self):
        """Initialize the pool with pre-warmed instances."""
        logger.info(f"Initializing bot pool with {settings.BOT_POOL_SIZE} instances")
        await self._refill_pool()

    async def _refill_pool(self):
        """Spawn instances until we hit the target pool size."""
        async with self._lock:
            current_count = len(self._instances)
            needed = settings.BOT_POOL_SIZE - current_count
            
            if needed <= 0:
                return

            logger.info(f"Spawning {needed} new instances to refill pool")
            for _ in range(needed):
                bot_id = f"bot-{uuid.uuid4().hex[:8]}"
                # In a real setup, this would trigger a Docker/K8s pod creation
                # For this infra scaffold, we'll mock the instance registration
                instance = BotInstance(
                    id=bot_id,
                    container_id=f"cont-{bot_id}",
                    ip_address="127.0.0.1", # placeholder
                    status="idle"
                )
                self._instances[bot_id] = instance
                await state_service.add_to_pool(bot_id)
                logger.debug(f"Provisioned instance {bot_id}")

    async def acquire_instance(self) -> str:
        """Get an available instance ID from the pool."""
        bot_id = await state_service.claim_from_pool()
        if not bot_id:
            # Scale on demand if pool is empty
            logger.warning("Pool exhausted, scaling on demand")
            bot_id = f"bot-od-{uuid.uuid4().hex[:8]}"
            await state_service.save_bot_info({
                "bot_id": bot_id,
                "status": "idle"
            })
            return bot_id
        
        # Trigger background refill
        asyncio.create_task(self._refill_pool())
        return bot_id

    async def release_instance(self, bot_id: str):
        """Return an instance to the available pool or terminate it."""
        logger.info(f"Releasing instance {bot_id}")
        await state_service.release_to_pool(bot_id)
        
    async def get_status(self) -> Dict:
        return {
            "total_slots": settings.BOT_POOL_SIZE,
            "active_instances": len(self._instances),
            "available_in_redis": await state_service.get_all_active_bot_ids() # This is actually in_use in redis service
        }

instance_pool = InstancePool()
