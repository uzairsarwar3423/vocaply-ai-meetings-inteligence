"""
Bot Manager
Vocaply AI Meeting Intelligence - Day 15

Central orchestration logic for bot lifecycle:
- Create new bots for meetings
- Stop running bots
- Manage state transitions
"""

import httpx
from datetime import datetime
from typing import List, Optional, Dict
from app.config import settings
from app.services.redis_state import state_service
from app.services.instance_pool import instance_pool
from shared.models.bot_status import CreateBotRequest, BotInfo, BotStatus, BotEvent
from shared.utils.logger import get_logger

logger = get_logger("bot-manager")

class BotManager:
    async def create_bot(self, request: CreateBotRequest) -> BotInfo:
        """
        Assign an instance to a meeting and command it to join.
        """
        logger.info(f"Creating bot for meeting {request.meeting_id} ({request.platform})")
        
        # 1. Acquire instance from pool
        bot_id = await instance_pool.acquire_instance()
        
        # 2. Update state in Redis
        info = BotInfo(
            bot_id=bot_id,
            status=BotStatus.INITIALIZING,
            platform=request.platform,
            meeting_id=request.meeting_id,
            meeting_url=request.meeting_url,
            company_id=request.company_id,
            user_id=request.user_id
        )
        await state_service.save_bot_info(info)
        await state_service.register_active_bot(request.company_id, bot_id)
        
        # 3. Command the bot instance (mocking the HTTP call to the Playwright container)
        logger.info(f"Commanding bot {bot_id} to join {request.meeting_url}")
        # await self._send_command_to_bot(bot_id, "join", request.model_dump())
        
        # 4. Notify main backend via webhook
        await self.notify_backend(BotEvent(
            event_type="bot_created",
            bot_id=bot_id,
            meeting_id=request.meeting_id,
            company_id=request.company_id,
            status=BotStatus.INITIALIZING,
            platform=request.platform
        ))
        
        return info

    async def stop_bot(self, bot_id: str, reason: str = "stopped"):
        """Gracefully shutdown a bot."""
        info = await state_service.get_bot_info(bot_id)
        if not info:
            logger.warning(f"Attempted to stop unknown bot {bot_id}")
            return

        logger.info(f"Stopping bot {bot_id} (Reason: {reason})")
        
        # 1. Command bot to leave
        # await self._send_command_to_bot(bot_id, "leave")
        
        # 2. Clean up state
        if info.company_id:
            await state_service.unregister_active_bot(info.company_id, bot_id)
        
        info.status = BotStatus.LEFT
        await state_service.save_bot_info(info)
        
        # 3. Notify backend
        await self.notify_backend(BotEvent(
            event_type="bot_left",
            bot_id=bot_id,
            meeting_id=info.meeting_id,
            company_id=info.company_id,
            status=BotStatus.LEFT,
            data={"reason": reason}
        ))
        
        # 4. Return to pool
        await instance_pool.release_instance(bot_id)

    async def notify_backend(self, event: BotEvent):
        """Send a webhook event to the main platform backend."""
        logger.debug(f"Sending webhook to backend: {event.event_type}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.BACKEND_URL}/webhooks/bot-events",
                    json=event.model_dump(),
                    headers={"X-Internal-Key": settings.BACKEND_API_KEY},
                    timeout=5.0
                )
                response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to notify main backend: {e}")

bot_manager = BotManager()
