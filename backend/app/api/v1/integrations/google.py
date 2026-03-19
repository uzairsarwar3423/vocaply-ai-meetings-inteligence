"""
Google Integration API Endpoints
Handles Google OAuth, Calendar, and Meet operations
"""

import uuid
import secrets
from typing import Optional
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.config import settings
from app.db.session import get_async_db
from app.api.deps import get_current_user_async as get_current_user
from app.models.platform_connection import PlatformConnection
from app.models.meeting import Meeting
from app.models.calendar_event import CalendarEvent
from app.models.user import User
from app.services.platforms.google.google_oauth import GoogleOAuth
from app.services.platforms.google.google_calendar import GoogleCalendar
from app.services.platforms.google.google_meet import GoogleMeet


router = APIRouter(prefix="/google", tags=["Google Integration"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CreateMeetingRequest(BaseModel):
    topic: str
    start_time: datetime
    duration_minutes: int
    description: Optional[str] = None
    attendees: Optional[list[str]] = None


class SyncCalendarRequest(BaseModel):
    days_ahead: int = 7


class ImportEventRequest(BaseModel):
    event_id: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OAUTH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/connect",
    summary="Connect Google account",
    description="Initiates OAuth flow to connect Google account",
)
async def connect_google(
    current_user=Depends(get_current_user),
):
    """Redirect to Google OAuth authorization"""
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state (in production, use Redis with expiration)
    # For now, client will verify via session
    
    google_oauth = GoogleOAuth()
    redirect_uri = settings.GOOGLE_REDIRECT_URI or "http://localhost:3000/integrations/google/callback"
    
    auth_url = google_oauth.get_oauth_url(state=state, redirect_uri=redirect_uri)
    
    return {"authorization_url": auth_url, "state": state}


@router.get(
    "/callback",
    summary="OAuth callback",
    description="Handles OAuth callback from Google",
)
async def oauth_callback(
    code: str,
    state: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Handle Google OAuth callback"""
    # Verify state (CSRF protection)
    # In production, verify against stored state in Redis
    
    google_oauth = GoogleOAuth()
    redirect_uri = settings.GOOGLE_REDIRECT_URI or "http://localhost:3000/integrations/google/callback"
    
    # Exchange code for tokens
    token_data = await google_oauth.exchange_code_for_token(code, redirect_uri)
    
    # Create temporary connection for user info request
    class TempConnection:
        def __init__(self, token):
            self.token = token
            self.is_token_expired = False
        def get_access_token(self, *args, **kwargs):
            return self.token
        def get_refresh_token(self, *args, **kwargs):
            return None

    google_oauth.connection = TempConnection(token_data["access_token"])
    
    # Get user info
    user_info = await google_oauth.get_user_info()
    
    # Check if connection exists
    stmt = select(PlatformConnection).where(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.platform == "google"
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if connection:
        # Update existing
        connection.set_access_token(token_data["access_token"])
        if token_data.get("refresh_token"):
            connection.set_refresh_token(token_data["refresh_token"])
        connection.token_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=token_data.get("expires_in", 3600)
        )
        connection.platform_user_id = user_info.get("id")
        connection.platform_email = user_info.get("email")
        connection.is_active = True
    else:
        # Create new
        connection = PlatformConnection(
            user_id=current_user.id,
            company_id=current_user.company_id,
            platform="google",
            platform_user_id=user_info.get("id"),
            platform_email=user_info.get("email"),
            scopes=GoogleOAuth.SCOPES,
            platform_metadata=user_info,
        )
        connection.set_access_token(token_data["access_token"])
        if token_data.get("refresh_token"):
            connection.set_refresh_token(token_data["refresh_token"])
        connection.token_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=token_data.get("expires_in", 3600)
        )
        
        db.add(connection)
    
    await db.commit()
    
    return {
        "success": True,
        "platform": "google",
        "user_email": user_info.get("email"),
    }


@router.post(
    "/disconnect",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disconnect Google account",
)
async def disconnect_google(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Disconnect Google account"""
    stmt = select(PlatformConnection).where(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.platform == "google"
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if connection:
        connection.is_active = False
        await db.commit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def _get_google_connection(
    current_user: User,
    db: AsyncSession
) -> PlatformConnection:
    """Get user's Google connection"""
    stmt = select(PlatformConnection).where(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.platform == "google",
        PlatformConnection.is_active == True,
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=400,
            detail="Google account not connected"
        )
    
    return connection


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CALENDAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/calendar/events",
    summary="List calendar events",
)
async def list_calendar_events(
    days_ahead: int = 7,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """List Google Calendar events"""
    connection = await _get_google_connection(current_user, db)
    
    calendar = GoogleCalendar(connection)
    
    now = datetime.now(timezone.utc)
    end_time = now + timedelta(days=days_ahead)
    
    events = await calendar.list_events(
        start_time=now,
        end_time=end_time,
    )
    
    return {
        "events": events,
        "count": len(events),
        "has_meet_links": sum(1 for e in events if e.get("has_meet_link")),
    }


@router.post(
    "/sync",
    summary="Sync calendar",
    description="Sync Google Calendar events to platform",
)
async def sync_calendar(
    request: SyncCalendarRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Sync Google Calendar to platform"""
    connection = await _get_google_connection(current_user, db)
    
    calendar = GoogleCalendar(connection)
    
    now = datetime.now(timezone.utc)
    end_time = now + timedelta(days=request.days_ahead)
    
    # Fetch events
    events = await calendar.list_events(
        start_time=now,
        end_time=end_time,
    )
    
    synced_count = 0
    meet_count = 0
    
    for event in events:
        try:
            # Parse start time
            start = event["start"].get("dateTime") or event["start"].get("date")
            end = event["end"].get("dateTime") or event["end"].get("date")
            
            start_time = datetime.fromisoformat(start.replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(end.replace("Z", "+00:00"))
            
            # Check if already exists
            stmt = select(CalendarEvent).where(
                CalendarEvent.user_id == current_user.id,
                CalendarEvent.external_event_id == event["id"],
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update
                existing.title = event.get("summary", "Untitled")
                existing.description = event.get("description")
                existing.start_time = start_time
                existing.end_time = end_time
                existing.has_meeting_url = event.get("has_meet_link", False)
                existing.meeting_url = event.get("meet_url")
                existing.meeting_platform = "google_meet" if event.get("has_meet_link") else None
            else:
                # Create
                calendar_event = CalendarEvent(
                    user_id=current_user.id,
                    company_id=current_user.company_id,
                    calendar_provider="google",
                    external_event_id=event["id"],
                    title=event.get("summary", "Untitled"),
                    description=event.get("description"),
                    start_time=start_time,
                    end_time=end_time,
                    has_meeting_url=event.get("has_meet_link", False),
                    meeting_url=event.get("meet_url"),
                    meeting_platform="google_meet" if event.get("has_meet_link") else None,
                    raw_event_data=event,
                )
                db.add(calendar_event)
            
            synced_count += 1
            if event.get("has_meet_link"):
                meet_count += 1
        except Exception as e:
            print(f"[GoogleSync] Error syncing event {event.get('id')}: {e}")
            continue
    
    await db.commit()
    
    # Update connection last_synced_at
    connection.last_synced_at = datetime.now(timezone.utc)
    await db.commit()
    
    return {
        "synced_count": synced_count,
        "meet_count": meet_count,
        "days_ahead": request.days_ahead,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MEET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/meet/meetings",
    summary="List Google Meet meetings",
)
async def list_meet_meetings(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """List upcoming Google Meet meetings"""
    connection = await _get_google_connection(current_user, db)
    
    meet = GoogleMeet(connection)
    meetings = await meet.list_upcoming_meetings()
    
    return {
        "meetings": meetings,
        "count": len(meetings),
    }


@router.post(
    "/meet/create",
    summary="Create Google Meet meeting",
)
async def create_meet_meeting(
    request: CreateMeetingRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new Google Meet meeting"""
    connection = await _get_google_connection(current_user, db)
    
    meet = GoogleMeet(connection)
    
    meet_data = await meet.create_meeting(
        topic=request.topic,
        start_time=request.start_time,
        duration_minutes=request.duration_minutes,
        description=request.description,
        attendees=request.attendees,
    )
    
    # Create meeting in our database
    duration = (
        datetime.fromisoformat(meet_data["end_time"].replace("Z", "+00:00")) -
        datetime.fromisoformat(meet_data["start_time"].replace("Z", "+00:00"))
    )
    
    meeting = Meeting(
        title=request.topic,
        description=request.description,
        meeting_url=meet_data["meet_url"],
        scheduled_start=request.start_time,
        duration_minutes=int(duration.total_seconds() / 60),
        company_id=current_user.company_id,
        created_by=current_user.id,
        platform="google_meet",
        platform_meeting_id=meet_data["event_id"],
        meta_data=meet_data["raw_event"],
    )
    
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    
    return {
        "meeting_id": str(meeting.id),
        "event_id": meet_data["event_id"],
        "meet_url": meet_data["meet_url"],
        "start_time": meet_data["start_time"],
    }


@router.post(
    "/meet/import",
    summary="Import Google Meet meeting",
)
async def import_meet_meeting(
    request: ImportEventRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Import existing Google Meet meeting to platform"""
    connection = await _get_google_connection(current_user, db)
    
    meet = GoogleMeet(connection)
    meet_data = await meet.get_meeting(request.event_id)
    
    if not meet_data.get("meet_url"):
        raise HTTPException(
            status_code=400,
            detail="Event does not have a Google Meet link"
        )
    
    # Create meeting in our database
    start_time = datetime.fromisoformat(
        meet_data["start_time"].replace("Z", "+00:00")
    )
    end_time = datetime.fromisoformat(
        meet_data["end_time"].replace("Z", "+00:00")
    )
    duration = int((end_time - start_time).total_seconds() / 60)
    
    meeting = Meeting(
        title=meet_data["topic"],
        description=meet_data.get("description"),
        meeting_url=meet_data["meet_url"],
        scheduled_time=start_time,
        duration_minutes=duration,
        company_id=current_user.company_id,
        created_by_id=current_user.id,
        platform="google_meet",
        external_meeting_id=request.event_id,
        platform_metadata=meet_data["raw_event"],
    )
    
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    
    return {
        "meeting_id": str(meeting.id),
        "title": meeting.title,
        "meet_url": meeting.meeting_url,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WEBHOOKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post(
    "/webhook",
    summary="Google Calendar webhook",
    description="Receives push notifications from Google Calendar",
)
async def calendar_webhook(
    request: Request,
    x_goog_channel_id: str = Header(None),
    x_goog_resource_state: str = Header(None),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Handle Google Calendar push notification.
    
    When calendar changes, Google sends notification to this endpoint.
    We then sync the calendar to get latest events.
    """
    print(f"[Google] Webhook: channel={x_goog_channel_id}, state={x_goog_resource_state}")
    
    if x_goog_resource_state == "sync":
        # Initial sync confirmation
        return {"received": True}
    
    # Trigger calendar sync for affected user
    # In production, look up user by channel_id and trigger sync
    
    return {"received": True}