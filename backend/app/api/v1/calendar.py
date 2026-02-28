"""
Calendar API Endpoints
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_async_db
from app.core.security import get_current_user
from app.services.calendar import CalendarSyncService, AutoJoinScheduler
from app.models.calendar_event import CalendarEvent
from sqlalchemy import select, and_


router = APIRouter(prefix="/calendar", tags=["Calendar"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SyncCalendarRequest(BaseModel):
    provider: str  # 'google' or 'outlook'
    access_token: str
    days_ahead: int = 7


class EnableAutoJoinRequest(BaseModel):
    event_id: uuid.UUID
    enabled: bool


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post(
    "/sync",
    status_code=status.HTTP_200_OK,
    summary="Sync calendar",
    description="Syncs calendar events from Google or Outlook",
)
async def sync_calendar(
    request: SyncCalendarRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Sync calendar from external provider"""
    sync_service = CalendarSyncService(db)

    if request.provider == 'google':
        count = await sync_service.sync_google_calendar(
            user_id=str(current_user.id),
            access_token=request.access_token,
            days_ahead=request.days_ahead,
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider: {request.provider}"
        )

    return {
        "synced_count": count,
        "provider": request.provider,
    }


@router.get(
    "/events",
    summary="Get calendar events",
    description="Returns synced calendar events",
)
async def get_calendar_events(
    days_ahead: int = Query(7, ge=1, le=90),
    has_meeting_url: Optional[bool] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Get calendar events"""
    from datetime import datetime, timedelta

    now = datetime.utcnow()
    end_time = now + timedelta(days=days_ahead)

    # Build query
    filters = [
        CalendarEvent.user_id == current_user.id,
        CalendarEvent.start_time >= now,
        CalendarEvent.start_time <= end_time,
    ]

    if has_meeting_url is not None:
        filters.append(CalendarEvent.has_meeting_url == has_meeting_url)

    stmt = select(CalendarEvent).where(and_(*filters)).order_by(CalendarEvent.start_time)

    result = await db.execute(stmt)
    events = result.scalars().all()

    return {
        "events": [
            {
                "id": str(event.id),
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "has_meeting_url": event.has_meeting_url,
                "meeting_url": event.meeting_url,
                "meeting_platform": event.meeting_platform,
                "auto_join_enabled": event.auto_join_enabled,
                "auto_join_scheduled": event.auto_join_scheduled,
            }
            for event in events
        ],
        "count": len(events),
    }


@router.post(
    "/enable-auto-join",
    status_code=status.HTTP_200_OK,
    summary="Enable/disable auto-join",
    description="Enable or disable auto-join for a calendar event",
)
async def enable_auto_join(
    request: EnableAutoJoinRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Enable/disable auto-join for an event"""
    # Get event
    stmt = select(CalendarEvent).where(
        and_(
            CalendarEvent.id == request.event_id,
            CalendarEvent.user_id == current_user.id,
        )
    )
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")

    if not event.has_meeting_url:
        raise HTTPException(
            status_code=400,
            detail="Cannot enable auto-join: Event has no meeting URL"
        )

    # Update auto-join setting
    event.auto_join_enabled = request.enabled

    await db.commit()

    return {
        "event_id": str(event.id),
        "auto_join_enabled": event.auto_join_enabled,
    }


@router.get(
    "/scheduled",
    summary="Get scheduled auto-joins",
    description="Returns events with auto-join scheduled",
)
async def get_scheduled_auto_joins(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Get scheduled auto-joins"""
    scheduler = AutoJoinScheduler(db)
    events = await scheduler.get_scheduled_events(str(current_user.id))

    return {
        "events": [
            {
                "id": str(event.id),
                "title": event.title,
                "start_time": event.start_time.isoformat(),
                "meeting_url": event.meeting_url,
                "auto_join_scheduled_at": event.auto_join_scheduled_at.isoformat(),
            }
            for event in events
        ],
        "count": len(events),
    }