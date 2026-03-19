"""
Zoom Integration API Endpoints
"""

import uuid
import secrets
from typing import Optional
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.config import settings
from app.db.session import get_async_db
from app.api.deps import get_current_user_async as get_current_user
from app.models.platform_connection import PlatformConnection
from app.models.meeting import Meeting
from app.services.platforms.zoom.zoom_oauth import ZoomOAuth
from app.services.platforms.zoom.zoom_api import ZoomAPI
from app.services.platforms.zoom.zoom_webhooks import ZoomWebhooksHandler


router = APIRouter(prefix="/zoom", tags=["Zoom Integration"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CreateMeetingRequest(BaseModel):
    topic: str
    start_time: datetime
    duration_minutes: int
    timezone: str = "UTC"
    password: Optional[str] = None
    agenda: Optional[str] = None


class ImportMeetingRequest(BaseModel):
    zoom_meeting_id: str


class ZoomSettingsUpdate(BaseModel):
    autoImportMeetings: bool
    autoJoinMeetings: bool
    autoRecordMeetings: bool
    syncCalendar: bool


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OAUTH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/connect",
    summary="Connect Zoom account",
    description="Initiates OAuth flow to connect Zoom account",
)
async def connect_zoom(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Redirect to Zoom OAuth authorization"""
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state in session/cache (simplified here)
    # In production, store in Redis with expiration
    
    # Generate OAuth URL
    zoom_oauth = ZoomOAuth()
    redirect_uri = settings.ZOOM_REDIRECT_URI or "http://localhost:3000/integrations/zoom/callback"
    auth_url = zoom_oauth.get_oauth_url(state=state, redirect_uri=redirect_uri)
    
    return {"authorization_url": auth_url, "state": state}


@router.get(
    "/callback",
    summary="OAuth callback",
    description="Handles OAuth callback from Zoom",
)
async def oauth_callback(
    code: str,
    state: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Handle Zoom OAuth callback"""
    # Verify state (CSRF protection)
    # In production, verify against stored state
    
    # Exchange code for tokens
    zoom_oauth = ZoomOAuth()
    redirect_uri = settings.ZOOM_REDIRECT_URI or "http://localhost:3000/integrations/zoom/callback"
    
    try:
        token_data = await zoom_oauth.exchange_code_for_token(code, redirect_uri)
    except Exception as e:
        import httpx
        if isinstance(e, httpx.HTTPStatusError):
            # Pass the Zoom API Error text to the frontend so it can display why authorization failed.
            raise HTTPException(
                status_code=400,
                detail=f"Zoom OAuth Error: {e.response.text}"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to exchange Zoom token: {str(e)}"
        )
        
    
    # Get user info
    # Define a simple class for the temporary connection
    class TempConnection:
        def __init__(self, token):
            self.token = token
            self.is_token_expired = False
        def get_access_token(self, *args, **kwargs):
            return self.token
        def get_refresh_token(self, *args, **kwargs):
            return None

    zoom_oauth.connection = TempConnection(token_data["access_token"])
    
    user_info = await zoom_oauth.get_user_info()
    
    # Check if connection already exists
    stmt = select(PlatformConnection).where(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.platform == "zoom"
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if connection:
        # Update existing
        connection.set_access_token(token_data["access_token"])
        connection.set_refresh_token(token_data.get("refresh_token"))
        connection.token_expires_at = datetime.now(timezone.utc).replace(
            microsecond=0
        ) + timedelta(seconds=token_data.get("expires_in", 3600))
        connection.platform_user_id = user_info.get("id")
        connection.platform_email = user_info.get("email")
        connection.is_active = True
    else:
        # Create new
        connection = PlatformConnection(
            user_id=current_user.id,
            company_id=current_user.company_id,
            platform="zoom",
            platform_user_id=user_info.get("id"),
            platform_email=user_info.get("email"),
            scopes=ZoomOAuth.SCOPES,
            platform_metadata=user_info,
        )
        connection.set_access_token(token_data["access_token"])
        connection.set_refresh_token(token_data.get("refresh_token"))
        connection.token_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=token_data.get("expires_in", 3600)
        )
        
        db.add(connection)
    
    await db.commit()
    
    return {
        "success": True,
        "platform": "zoom",
        "user_email": user_info.get("email"),
    }


@router.post(
    "/disconnect",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disconnect Zoom account",
)
async def disconnect_zoom(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Disconnect Zoom account"""
    stmt = select(PlatformConnection).where(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.platform == "zoom"
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if connection:
        connection.is_active = False
        await db.commit()
    
    return None


@router.get(
    "/settings",
    summary="Get Zoom settings",
)
async def get_zoom_settings(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Get user's Zoom integration settings"""
    connection = await _get_zoom_connection(current_user.id, db)
    
    return connection.platform_metadata.get("settings", {
        "autoImportMeetings": True,
        "autoJoinMeetings": False,
        "autoRecordMeetings": True,
        "syncCalendar": True,
    })


@router.put(
    "/settings",
    summary="Update Zoom settings",
)
async def update_zoom_settings(
    settings_data: ZoomSettingsUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Update user's Zoom integration settings"""
    connection = await _get_zoom_connection(current_user.id, db)
    
    # Update metadata
    if not connection.platform_metadata:
        connection.platform_metadata = {}
    
    # Ensure it's a dict to avoid issues with JSONB mutability tracking
    new_metadata = dict(connection.platform_metadata)
    new_metadata["settings"] = settings_data.dict()
    
    connection.platform_metadata = new_metadata
    await db.commit()
    
    return {"success": True}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MEETINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def _get_zoom_connection(user_id: str, db: AsyncSession) -> PlatformConnection:
    """Get user's Zoom connection"""
    stmt = select(PlatformConnection).where(
        PlatformConnection.user_id == user_id,
        PlatformConnection.platform == "zoom",
        PlatformConnection.is_active == True,
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=400,
            detail="Zoom account not connected"
        )
    
    return connection


@router.get(
    "/meetings",
    summary="List Zoom meetings",
)
async def list_zoom_meetings(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """List user's upcoming Zoom meetings"""
    connection = await _get_zoom_connection(current_user.id, db)
    
    zoom_api = ZoomAPI(connection)
    try:
        meetings = await zoom_api.list_upcoming_meetings()
    except Exception as e:
        import httpx
        if isinstance(e, httpx.HTTPStatusError):
            raise HTTPException(
                status_code=400,
                detail=f"Zoom API Error: {e.response.text}"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Zoom meetings: {str(e)}"
        )
    
    return {
        "meetings": meetings,
        "count": len(meetings),
    }


@router.post(
    "/create-meeting",
    summary="Create Zoom meeting",
)
async def create_zoom_meeting(
    request: CreateMeetingRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new Zoom meeting"""
    connection = await _get_zoom_connection(current_user.id, db)
    
    zoom_api = ZoomAPI(connection)
    
    try:
        zoom_meeting = await zoom_api.schedule_meeting(
            topic=request.topic,
            start_time=request.start_time,
            duration_minutes=request.duration_minutes,
            timezone=request.timezone,
            password=request.password,
            agenda=request.agenda,
        )
    except Exception as e:
        import httpx
        if isinstance(e, httpx.HTTPStatusError):
            raise HTTPException(
                status_code=400,
                detail=f"Zoom API Error: {e.response.text}"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Zoom meeting: {str(e)}"
        )
    
    # Create meeting in our database
    meeting = Meeting(
        title=request.topic,
        description=request.agenda,
        meeting_url=zoom_meeting["join_url"],
        scheduled_start=request.start_time,
        duration_minutes=request.duration_minutes,
        company_id=current_user.company_id,
        created_by=current_user.id,
        platform="zoom",
        platform_meeting_id=str(zoom_meeting["id"]),
        meta_data=zoom_meeting,
    )
    
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    
    return {
        "meeting_id": str(meeting.id),
        "zoom_meeting_id": zoom_meeting["id"],
        "join_url": zoom_meeting["join_url"],
        "start_time": zoom_meeting["start_time"],
    }


@router.post(
    "/import-meeting",
    summary="Import Zoom meeting",
)
async def import_zoom_meeting(
    request: ImportMeetingRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Import existing Zoom meeting to platform"""
    connection = await _get_zoom_connection(current_user.id, db)
    
    zoom_api = ZoomAPI(connection)
    
    try:
        zoom_meeting = await zoom_api.get_meeting_details(request.zoom_meeting_id)
    except Exception as e:
        import httpx
        if isinstance(e, httpx.HTTPStatusError):
            raise HTTPException(
                status_code=400,
                detail=f"Zoom API Error: {e.response.text}"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Zoom meeting details: {str(e)}"
        )
    
    # Create meeting in our database
    start_time = datetime.fromisoformat(
        zoom_meeting["start_time"].replace("Z", "+00:00")
    )
    
    meeting = Meeting(
        title=zoom_meeting["topic"],
        description=zoom_meeting.get("agenda"),
        meeting_url=zoom_meeting["join_url"],
        scheduled_start=start_time,
        duration_minutes=zoom_meeting["duration"],
        company_id=current_user.company_id,
        created_by=current_user.id,
        platform="zoom",
        platform_meeting_id=request.zoom_meeting_id,
        meta_data=zoom_meeting,
    )
    
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    
    return {
        "meeting_id": str(meeting.id),
        "title": meeting.title,
        "join_url": meeting.meeting_url,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WEBHOOKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post(
    "/webhook",
    summary="Zoom webhook",
    description="Receives webhook events from Zoom",
)
async def zoom_webhook(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
):
    """Handle Zoom webhook events"""
    # Get raw body for signature verification
    body = await request.body()
    signature = request.headers.get("x-zm-signature", "")
    
    # Verify webhook signature
    zoom_oauth = ZoomOAuth()
    if not zoom_oauth.verify_webhook(body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse event
    event_data = await request.json()
    
    # Handle event
    webhook_handler = ZoomWebhooksHandler(db)
    await webhook_handler.handle_event(event_data)
    
    return {"received": True}