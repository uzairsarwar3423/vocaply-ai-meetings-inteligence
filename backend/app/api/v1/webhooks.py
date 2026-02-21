"""
Bot Interaction Webhooks
Vocaply Platform - Day 15

Receives and processes events from the Bot Orchestrator:
- bot_joined
- bot_left
- bot_error
- transcript_chunk (live)
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.repositories.meeting_repository import MeetingRepository
from app.services.realtime.broadcast_service import (
    broadcast_bot_status_changed,
    broadcast_transcript_chunk
)
from app.schemas.bot import BotEvent, BotStatus
from app.core.logging import logger

router = APIRouter()

@router.post("/bot-events")
async def handle_bot_event(
    event: BotEvent,
    x_internal_key: str = Header(None),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Callback from Bot Orchestrator.
    """
    # Simple internal security check
    # if x_internal_key != settings.INTERNAL_API_KEY:
    #     raise HTTPException(status_code=403)

    logger.info(f"Received bot event: {event.event_type} for meeting {event.meeting_id}")

    # 1. Update Database Status
    if event.meeting_id:
        repo = MeetingRepository(db)
        # Use meeting_id for both meeting_id and company_id if company_id is missing in event, 
        # but get_by_id expects UUID. Let's try to get it first.
        meeting = await repo.get_by_id(
            meeting_id=event.meeting_id, 
            company_id=event.company_id
        )
        if meeting:
            # The repository has a patch method that we can use
            from app.schemas.meeting import MeetingPatch
            patch_data = MeetingPatch(
                bot_status=event.status.value,
                participant_count=event.data.get("participant_count", 0) if event.data else meeting.participant_count
            )
            await repo.patch(meeting, patch_data)

    # 2. Broadcast to connected clients over WebSocket
    if event.company_id and event.meeting_id:
        await broadcast_bot_status_changed(
            company_id=event.company_id,
            meeting_id=event.meeting_id,
            status=event.status.value,
            detail=event.data.get("reason") if event.data else None
        )

        # Handle specific event logic (e.g. transcript chunks)
        if event.event_type == "transcript_chunk" and event.data:
            await broadcast_transcript_chunk(
                company_id=event.company_id,
                meeting_id=event.meeting_id,
                chunk=event.data
            )

    return {"status": "ok"}
