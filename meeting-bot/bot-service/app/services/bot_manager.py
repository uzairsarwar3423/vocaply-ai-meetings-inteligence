"""
Bot Manager
High-level bot orchestration and webhook delivery
"""

import asyncio
import httpx
from typing import Optional
from datetime import datetime

from app.config import settings
from app.services.instance_pool import InstancePool
from shared.models.bot_status import BotPlatform, BotEvent
from shared.utils.redis_client import RedisClient
from shared.utils.logger import logger


class BotManager:
    """
    Top-level bot orchestration.
    Coordinates pool, webhooks, and lifecycle.
    """

    def __init__(self, redis: RedisClient):
        self.redis = redis
        self.pool = InstancePool(redis)
        self.http_client: Optional[httpx.AsyncClient] = None

    async def start(self):
        """Initialize manager"""
        logger.info("Starting Bot Manager")
        
        # HTTP client for webhooks
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {settings.BACKEND_API_KEY}"},
        )
        
        # Start pool
        await self.pool.start()
        
        logger.info("Bot Manager started")

    async def stop(self):
        """Shutdown manager"""
        logger.info("Stopping Bot Manager")
        
        await self.pool.stop()
        
        if self.http_client:
            await self.http_client.aclose()
        
        logger.info("Bot Manager stopped")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # BOT OPERATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def create_bot_for_meeting(
        self,
        meeting_url: str,
        meeting_id: str,
        company_id: str,
        platform: str,
    ) -> dict:
        """
        Main entry point: Create and assign bot to meeting.
        
        Flow:
        1. Assign bot from pool
        2. Join meeting
        3. Start recording
        4. Send webhook notifications
        """
        platform_enum = BotPlatform(platform.lower())
        
        # Assign bot
        bot = await self.pool.assign_bot(meeting_url, meeting_id, company_id, platform_enum)
        
        if not bot:
            raise RuntimeError("No available bots in pool")
        
        # Start join process in background
        asyncio.create_task(self._join_and_record(bot.bot_id))
        
        return {
            "bot_id": bot.bot_id,
            "status": bot.data.status,
            "meeting_id": meeting_id,
            "created_at": bot.data.created_at.isoformat(),
        }

    async def _join_and_record(self, bot_id: str):
        """Background task: Join meeting and start recording"""
        bot = self.pool.bots.get(bot_id)
        if not bot:
            return
        
        try:
            # Join meeting
            await bot.join()
            await self._send_webhook("bot.joined", bot)
            
            # Start recording
            await bot.start_recording()
            await self._send_webhook("bot.recording.started", bot)
            
            # Update Redis
            await self.redis.set_bot(bot_id, bot.data.dict())
            
        except Exception as e:
            logger.error(f"Bot {bot_id} join/record failed: {e}", exc_info=True)
            bot.data.error = str(e)
            await self._send_webhook("bot.error", bot)
            await self.pool.release_bot(bot_id)

    async def stop_bot(self, bot_id: str):
        """Manually stop a bot"""
        bot = self.pool.bots.get(bot_id)
        if not bot:
            raise ValueError(f"Bot {bot_id} not found")
        
        try:
            await bot.leave()
            await self._send_webhook("bot.left", bot)
        finally:
            await self.pool.release_bot(bot_id)

    async def get_bot_status(self, bot_id: str) -> dict:
        """Get current bot status"""
        bot = self.pool.bots.get(bot_id)
        if not bot:
            # Try Redis
            data = await self.redis.get_bot(bot_id)
            if data:
                return data
            raise ValueError(f"Bot {bot_id} not found")
        
        return bot.data.dict()

    async def get_active_bots(self, company_id: Optional[str] = None) -> list:
        """Get all active bots, optionally filtered by company"""
        if company_id:
            bot_ids = await self.redis.get_company_bots(company_id)
            bots = [self.pool.bots.get(bid) for bid in bot_ids if bid in self.pool.bots]
        else:
            bots = list(self.pool.bots.values())
        
        return [bot.data.dict() for bot in bots if bot]

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WEBHOOKS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _send_webhook(self, event_type: str, bot):
        """Send event to backend API"""
        if not bot.data.meeting_id or not bot.data.company_id:
            return
        
        event = BotEvent(
            event_type=event_type,
            bot_id=bot.bot_id,
            meeting_id=bot.data.meeting_id,
            company_id=bot.data.company_id,
            timestamp=datetime.utcnow(),
            data={
                "status": bot.data.status,
                "platform": bot.data.platform,
                "participant_count": bot.data.participant_count,
                "recording_path": bot.data.recording_path,
                "error": bot.data.error,
            },
        )
        
        url = f"{settings.BACKEND_API_URL}/api/v1/webhooks/bot-events"
        
        try:
            response = await self.http_client.post(
                url,
                json=event.dict(),
                timeout=10.0,
            )
            response.raise_for_status()
            logger.info(f"Webhook sent: {event_type} for bot {bot.bot_id}")
            
        except httpx.HTTPError as e:
            logger.error(f"Webhook delivery failed: {e}", exc_info=True)
            # Retry logic could go here