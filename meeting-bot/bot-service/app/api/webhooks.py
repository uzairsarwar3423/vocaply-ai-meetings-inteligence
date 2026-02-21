"""
Bot Webhooks API
Vocaply AI Meeting Intelligence - Day 15

Receives events from the individual bot containers/processes.
"""

from fastapi import APIRouter, Header, HTTPException
from shared.models.bot_status import BotEvent, BotStatus
from app.services.bot_manager import bot_manager
from app.services.redis_state import state_service
from shared.utils.logger import get_logger

logger = get_logger("webhooks")
router = APIRouter(prefix="/webhooks", tags=["Internal Webhooks"])

@router.post("/bot-events")
async def handle_bot_event(event: BotEvent):
    """
    Called by individual bot instances to report progress.
    """
    logger.info(f"Received event {event.event_type} from bot {event.bot_id}")
    
    # 1. Update state in Redis
    info = await state_service.get_bot_info(event.bot_id)
    if info:
        info.status = event.status
        if event.data:
            if "participant_count" in event.data:
                info.participant_count = event.data["participant_count"]
        
        await state_service.save_bot_info(info)

    # 2. Forward to main backend
    await bot_manager.notify_backend(event)
    
    # 3. If bot left or failed, release from manager (which handles pool management)
    if event.status in [BotStatus.LEFT, BotStatus.FAILED, BotStatus.TERMINATED]:
        await bot_manager.stop_bot(event.bot_id, reason=f"bot_reported_{event.status}")

    return {"status": "accepted"}
