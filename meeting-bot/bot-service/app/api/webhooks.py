"""
Webhooks API
Receives events from bots and external services
"""

from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel
from typing import Any, Dict

from app.config import settings
from shared.utils.logger import logger


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


class WebhookEvent(BaseModel):
    """Generic webhook event"""
    event_type: str
    bot_id:     str
    data:       Dict[str, Any]


@router.post(
    "/bot-events",
    status_code=status.HTTP_200_OK,
    summary="Receive bot events from external platforms",
    description="Webhook endpoint for Zoom/Meet/Teams to notify us of bot events",
)
async def receive_bot_event(
    event: WebhookEvent,
    authorization: str = Header(None),
):
    """
    Handle external bot events.
    
    Example events:
    - bot.kicked_from_meeting
    - bot.recording_stopped
    - bot.connection_lost
    """
    # Verify webhook signature
    if not authorization or authorization != f"Bearer {settings.BACKEND_API_KEY}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization"
        )
    
    logger.info(f"Received webhook: {event.event_type} for bot {event.bot_id}")
    
    # TODO: Handle different event types
    # For now, just log
    
    return {"received": True}