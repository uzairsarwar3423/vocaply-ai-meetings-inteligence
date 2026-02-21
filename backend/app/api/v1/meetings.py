"""
Meetings API Router
Vocaply Platform - Day 4

All meeting-related HTTP endpoints.
"""

import uuid
from typing import List, Optional

from fastapi import (
    APIRouter, Depends, HTTPException, Query,
    UploadFile, File, Form, status, BackgroundTasks
)
from fastapi.responses import JSONResponse

from app.models.meeting import MeetingStatus, MeetingPlatform
from app.schemas.meeting import (
    MeetingCreate, MeetingUpdate, MeetingPatch,
    MeetingResponse, MeetingListItem,
    MeetingFilters, MeetingStatusUpdate,
    AddAttendeeRequest, RemoveAttendeeRequest,
    UploadRecordingResponse,
)
from app.schemas.pagination import (
    PaginationParams, CursorPaginationParams,
    PaginatedResponse, CursorPaginatedResponse
)
from app.services.meeting import MeetingService
from app.repositories.meeting_repository import MeetingRepository
from app.db.session import get_db, get_async_db
from app.api.deps import get_current_user

from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(tags=["Meetings"])


# ============================================
# DEPENDENCY INJECTION
# ============================================

async def get_meeting_service(db: AsyncSession = Depends(get_async_db)) -> MeetingService:
    """Provide MeetingService with its dependencies"""
    repo = MeetingRepository(db)
    return MeetingService(repo)


# ============================================
# HELPER: Build filters from query params
# ============================================

def build_filters(
    status: Optional[List[MeetingStatus]] = Query(None, description="Filter by status"),
    platform: Optional[List[str]]          = Query(None, description="Filter by platform"),
    date_from: Optional[str]               = Query(None, description="Filter from date (ISO 8601)"),
    date_to: Optional[str]                 = Query(None, description="Filter to date (ISO 8601)"),
    bot_enabled: Optional[bool]            = Query(None, description="Filter by bot enabled"),
    has_recording: Optional[bool]          = Query(None, description="Filter by recording presence"),
    has_transcript: Optional[bool]         = Query(None, description="Filter by transcript presence"),
    created_by: Optional[uuid.UUID]        = Query(None, description="Filter by creator"),
    tags: Optional[List[str]]              = Query(None, description="Filter by tags"),
) -> Optional[MeetingFilters]:
    """Build a MeetingFilters object from query parameters"""
    from datetime import datetime

    filters = MeetingFilters(
        status=status,
        platform=platform,
        date_from=datetime.fromisoformat(date_from) if date_from else None,
        date_to=datetime.fromisoformat(date_to) if date_to else None,
        bot_enabled=bot_enabled,
        has_recording=has_recording,
        has_transcript=has_transcript,
        created_by=created_by,
        tags=tags,
    )

    # Return None if no filters applied (cleaner code downstream)
    has_any = any([
        filters.status, filters.platform, filters.date_from,
        filters.date_to, filters.bot_enabled is not None,
        filters.has_recording is not None, filters.has_transcript is not None,
        filters.created_by, filters.tags,
    ])
    return filters if has_any else None


# ============================================
# ENDPOINTS
# ============================================

# ─── POST /meetings ───────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new meeting",
    description="Create a new meeting record. Bot auto-join can be enabled via bot_enabled flag.",
)
async def create_meeting(
    data: MeetingCreate,
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    meeting = await service.create_meeting(
        company_id=current_user.company_id,
        user_id=current_user.id,
        data=data,
    )
    return MeetingResponse.from_orm(meeting)


# ─── GET /meetings ────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=PaginatedResponse[MeetingListItem],
    summary="List all meetings",
    description="Get a paginated list of meetings with optional filtering and sorting.",
)
async def list_meetings(
    # Pagination
    page:     int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    # Sorting
    sort_by:  str = Query(default="created_at", description="Field to sort by"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    # Filters
    filters:  Optional[MeetingFilters] = Depends(build_filters),
    # Auth
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    pagination = PaginationParams(page=page, per_page=per_page)
    return await service.list_meetings(
        company_id=current_user.company_id,
        pagination=pagination,
        filters=filters,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


# ─── GET /meetings/search ─────────────────────────────────────────────────────

@router.get(
    "/search",
    response_model=PaginatedResponse[MeetingListItem],
    summary="Search meetings",
    description="Full-text search across meeting titles and descriptions.",
)
async def search_meetings(
    q:        str = Query(..., min_length=2, description="Search query"),
    page:     int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    filters:  Optional[MeetingFilters] = Depends(build_filters),
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    pagination = PaginationParams(page=page, per_page=per_page)
    return await service.search_meetings(
        company_id=current_user.company_id,
        query=q,
        pagination=pagination,
        filters=filters,
    )


# ─── GET /meetings/upcoming ───────────────────────────────────────────────────

@router.get(
    "/upcoming",
    response_model=List[MeetingListItem],
    summary="Get upcoming meetings",
    description="Get the next N upcoming scheduled meetings.",
)
async def get_upcoming_meetings(
    limit:       int = Query(default=5, ge=1, le=20),
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    meetings = await service.get_upcoming(
        company_id=current_user.company_id,
        limit=limit,
    )
    return [MeetingListItem.from_orm(m) for m in meetings]


# ─── GET /meetings/stats ──────────────────────────────────────────────────────

@router.get(
    "/stats",
    summary="Get meeting statistics",
    description="Get aggregated meeting statistics for the current company.",
)
async def get_meeting_stats(
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    return await service.get_stats(current_user.company_id)


# ─── GET /meetings/{id} ───────────────────────────────────────────────────────

@router.get(
    "/{meeting_id}",
    response_model=MeetingResponse,
    summary="Get a meeting by ID",
)
async def get_meeting(
    meeting_id:  uuid.UUID,
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    meeting = await service.get_meeting(
        meeting_id=meeting_id,
        company_id=current_user.company_id,
    )
    return MeetingResponse.from_orm(meeting)


# ─── PUT /meetings/{id} ───────────────────────────────────────────────────────

@router.put(
    "/{meeting_id}",
    response_model=MeetingResponse,
    summary="Full update of a meeting (PUT)",
    description="Replace all meeting fields. Use PATCH for partial updates.",
)
async def update_meeting(
    meeting_id:  uuid.UUID,
    data:        MeetingUpdate,
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    meeting = await service.update_meeting(
        meeting_id=meeting_id,
        company_id=current_user.company_id,
        data=data,
    )
    return MeetingResponse.from_orm(meeting)


# ─── PATCH /meetings/{id} ─────────────────────────────────────────────────────

@router.patch(
    "/{meeting_id}",
    response_model=MeetingResponse,
    summary="Partial update of a meeting (PATCH)",
    description="Update only the fields provided in the request body.",
)
async def patch_meeting(
    meeting_id:  uuid.UUID,
    data:        MeetingPatch,
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    meeting = await service.patch_meeting(
        meeting_id=meeting_id,
        company_id=current_user.company_id,
        data=data,
    )
    return MeetingResponse.from_orm(meeting)


# ─── DELETE /meetings/{id} ────────────────────────────────────────────────────

@router.delete(
    "/{meeting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a meeting (soft delete)",
    description="Soft-deletes the meeting. Data is retained but hidden from all list views.",
)
async def delete_meeting(
    meeting_id:  uuid.UUID,
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    await service.delete_meeting(
        meeting_id=meeting_id,
        company_id=current_user.company_id,
        deleted_by_id=current_user.id,
    )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# ─── PATCH /meetings/{id}/status ─────────────────────────────────────────────

@router.patch(
    "/{meeting_id}/status",
    response_model=MeetingResponse,
    summary="Update meeting status",
    description=(
        "Transition the meeting to a new status. "
        "Valid transitions: scheduled→in_progress→transcribing→analyzing→completed. "
        "Any status can transition to cancelled."
    ),
)
async def update_meeting_status(
    meeting_id:  uuid.UUID,
    payload:     MeetingStatusUpdate,
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    meeting = await service.transition_status(
        meeting_id=meeting_id,
        company_id=current_user.company_id,
        payload=payload,
    )
    return MeetingResponse.from_orm(meeting)


# ─── POST /meetings/{id}/attendees ───────────────────────────────────────────

@router.post(
    "/{meeting_id}/attendees",
    response_model=MeetingResponse,
    summary="Add attendee to a meeting",
)
async def add_attendee(
    meeting_id:  uuid.UUID,
    data:        AddAttendeeRequest,
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    meeting = await service.add_attendee(
        meeting_id=meeting_id,
        company_id=current_user.company_id,
        name=data.name,
        email=data.email,
        role=data.role,
    )
    return MeetingResponse.from_orm(meeting)


# ─── DELETE /meetings/{id}/attendees ─────────────────────────────────────────

@router.delete(
    "/{meeting_id}/attendees",
    response_model=MeetingResponse,
    summary="Remove attendee from a meeting",
)
async def remove_attendee(
    meeting_id:  uuid.UUID,
    data:        RemoveAttendeeRequest,
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    meeting = await service.remove_attendee(
        meeting_id=meeting_id,
        company_id=current_user.company_id,
        email=data.email,
    )
    return MeetingResponse.from_orm(meeting)


# ─── POST /meetings/{id}/upload-recording ────────────────────────────────────

@router.post(
    "/{meeting_id}/upload-recording",
    response_model=UploadRecordingResponse,
    summary="Get presigned URL for recording upload",
    description=(
        "Returns a presigned URL for direct browser-to-storage upload. "
        "After upload completes, call the confirm endpoint to update the meeting record."
    ),
)
async def get_recording_upload_url(
    meeting_id:   uuid.UUID,
    file_name:    str  = Query(..., description="Original file name with extension"),
    file_size:    int  = Query(..., gt=0, description="File size in bytes"),
    content_type: str  = Query(..., description="MIME type e.g. audio/mp4"),
    current_user  = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    return await service.get_upload_url(
        meeting_id=meeting_id,
        company_id=current_user.company_id,
        file_name=file_name,
        file_size=file_size,
        content_type=content_type,
    )


# ─── POST /meetings/{id}/upload-recording/confirm ────────────────────────────

@router.post(
    "/{meeting_id}/upload-recording/confirm",
    response_model=MeetingResponse,
    summary="Confirm recording upload complete",
    description=(
        "Call this after the browser has finished uploading the recording. "
        "This updates the meeting record and triggers transcription."
    ),
)
async def confirm_recording_upload(
    meeting_id:       uuid.UUID,
    s3_key:           str           = Form(...),
    recording_url:    str           = Form(...),
    size_bytes:       Optional[int] = Form(None),
    duration_seconds: Optional[int] = Form(None),
    format:           Optional[str] = Form(None),
    current_user = Depends(get_current_user),
    service: MeetingService = Depends(get_meeting_service),
):
    meeting = await service.confirm_recording_upload(
        meeting_id=meeting_id,
        company_id=current_user.company_id,
        s3_key=s3_key,
        recording_url=recording_url,
        size_bytes=size_bytes,
        duration_seconds=duration_seconds,
        format=format,
    )
    return MeetingResponse.from_orm(meeting)