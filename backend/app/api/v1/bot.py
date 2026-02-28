"""
Bot API Endpoints
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.core.security import get_current_user
from app.services.bot import BotScheduler, BotServiceError
from app.models.bot_session import BotSession


router = APIRouter(prefix="/meetings/{meeting_id}/bot", tags=["Bot"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post(
    "/start",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start bot for meeting",
    description="Creates and assigns a bot to join the meeting",
)
async def start_bot(
    meeting_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Start bot for meeting.
    
    Returns immediately with bot session info.
    Bot will join meeting asynchronously.
    """
    scheduler = BotScheduler(db)
    
    try:
        bot_session = await scheduler.start_bot_for_meeting(
            meeting_id=str(meeting_id),
            company_id=str(current_user.company_id),
        )
        
        return {
            "bot_session_id": str(bot_session.id),
            "bot_id": bot_session.bot_instance_id,
            "status": bot_session.status,
            "platform": bot_session.bot_platform,
            "created_at": bot_session.created_at.isoformat(),
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BotServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.post(
    "/stop",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Stop bot",
    description="Stops the bot and makes it leave the meeting",
)
async def stop_bot(
    meeting_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Stop bot for meeting"""
    scheduler = BotScheduler(db)
    
    success = await scheduler.stop_bot_for_meeting(str(meeting_id))
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="No active bot found for meeting",
        )
    
    return None


@router.get(
    "/status",
    summary="Get bot status",
    description="Returns current bot status for the meeting",
)
async def get_bot_status(
    meeting_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Get bot status"""
    from sqlalchemy import select
    
    stmt = select(BotSession).where(BotSession.meeting_id == meeting_id)
    result = await db.execute(stmt)
    bot_session = result.scalar_one_or_none()
    
    if not bot_session:
        raise HTTPException(status_code=404, detail="Bot session not found")
    
    return {
        "bot_session_id": str(bot_session.id),
        "bot_id": bot_session.bot_instance_id,
        "status": bot_session.status,
        "platform": bot_session.bot_platform,
        "joined_at": bot_session.joined_at.isoformat() if bot_session.joined_at else None,
        "left_at": bot_session.left_at.isoformat() if bot_session.left_at else None,
        "participant_count": bot_session.participant_count,
        "is_alone": bot_session.is_alone,
        "recording_url": bot_session.recording_url,
        "recording_duration": bot_session.recording_duration,
        "error": bot_session.error,
    }