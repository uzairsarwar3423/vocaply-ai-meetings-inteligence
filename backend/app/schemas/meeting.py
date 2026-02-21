"""
Meeting Schemas (Pydantic)
Vocaply Platform - Day 4
File: backend/app/schemas/meeting.py
"""
from __future__ import annotations
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator, HttpUrl
from app.models.meeting import MeetingStatus, MeetingPlatform


# ============================================
# ATTENDEE SCHEMA
# ============================================

class AttendeeSchema(BaseModel):
    email:     str            = Field(..., description="Attendee email address")
    name:      Optional[str]  = Field(default=None, description="Display name")
    role:      str            = Field(default="attendee", description="organizer or attendee")
    user_id:   Optional[UUID] = Field(default=None, description="Vocaply user ID if matched")
    joined_at: Optional[datetime] = None
    left_at:   Optional[datetime] = None

    @validator("role")
    def validate_role(cls, v):
        if v not in ("organizer", "attendee"):
            raise ValueError("role must be 'organizer' or 'attendee'")
        return v

    class Config:
        from_attributes = True


# ============================================
# CREATE MEETING
# ============================================

class MeetingCreate(BaseModel):
    title:            str                    = Field(..., min_length=1, max_length=500, description="Meeting title")
    description:      Optional[str]          = Field(default=None, max_length=5000)
    meeting_url:      Optional[str]          = Field(default=None, description="Meeting join URL")
    meeting_password: Optional[str]          = Field(default=None, max_length=100)
    notes:            Optional[str]          = Field(default=None)

    # Platform
    platform:            Optional[MeetingPlatform] = Field(default=None)
    platform_meeting_id: Optional[str]             = Field(default=None, max_length=255)
    platform_join_url:   Optional[str]             = Field(default=None)

    # Scheduling
    scheduled_start: Optional[datetime] = Field(default=None, description="ISO 8601 datetime")
    scheduled_end:   Optional[datetime] = Field(default=None)
    timezone:        str                = Field(default="UTC", max_length=50)

    # Attendees
    attendees:       List[AttendeeSchema] = Field(default_factory=list)
    organizer_email: Optional[str]        = Field(default=None)

    # Bot
    bot_enabled: bool = Field(default=False)

    # Meta
    tags:     List[str]       = Field(default_factory=list, max_items=20)
    meta_data: Dict[str, Any]  = Field(default_factory=dict)

    @validator("scheduled_end")
    def end_after_start(cls, v, values):
        start = values.get("scheduled_start")
        if v and start and v <= start:
            raise ValueError("scheduled_end must be after scheduled_start")
        return v

    @validator("title")
    def title_not_blank(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be blank")
        return v.strip()

    class Config:
        from_attributes = True


# ============================================
# UPDATE MEETING (full replace)
# ============================================

class MeetingUpdate(BaseModel):
    title:            Optional[str]               = Field(default=None, min_length=1, max_length=500)
    description:      Optional[str]               = Field(default=None)
    meeting_url:      Optional[str]               = Field(default=None)
    meeting_password: Optional[str]               = Field(default=None)
    notes:            Optional[str]               = Field(default=None)

    platform:            Optional[MeetingPlatform] = None
    platform_meeting_id: Optional[str]             = None
    platform_join_url:   Optional[str]             = None

    scheduled_start:  Optional[datetime] = None
    scheduled_end:    Optional[datetime] = None
    timezone:         Optional[str]      = None

    attendees:        Optional[List[AttendeeSchema]] = None
    organizer_email:  Optional[str]                  = None

    bot_enabled:      Optional[bool]          = None
    tags:             Optional[List[str]]     = None
    meta_data:        Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# ============================================
# PATCH MEETING (partial update)
# ============================================

class MeetingPatch(BaseModel):
    """All fields optional — only provided fields are updated"""
    title:            Optional[str]                 = None
    description:      Optional[str]                 = None
    meeting_url:      Optional[str]                 = None
    meeting_password: Optional[str]                 = None
    notes:            Optional[str]                 = None
    platform:         Optional[MeetingPlatform]     = None
    scheduled_start:  Optional[datetime]             = None
    scheduled_end:    Optional[datetime]             = None
    timezone:         Optional[str]                  = None
    attendees:        Optional[List[AttendeeSchema]] = None
    organizer_email:  Optional[str]                  = None
    bot_enabled:      Optional[bool]                 = None
    status:           Optional[MeetingStatus]         = None
    tags:             Optional[List[str]]             = None
    meta_data:        Optional[Dict[str, Any]]        = None

    class Config:
        from_attributes = True


# ============================================
# STATUS TRANSITION
# ============================================

class MeetingStatusUpdate(BaseModel):
    status: MeetingStatus = Field(..., description="New status to transition to")
    reason: Optional[str] = Field(default=None, description="Optional reason for status change")


# ============================================
# MEETING RESPONSE
# ============================================

class MeetingResponse(BaseModel):
    id:               UUID
    company_id:       UUID
    created_by:       Optional[UUID]

    # Details
    title:            str
    description:      Optional[str]
    meeting_url:      Optional[str]
    notes:            Optional[str]

    # Platform
    platform:            Optional[str]
    platform_meeting_id: Optional[str]
    platform_join_url:   Optional[str]

    # Scheduling
    scheduled_start:  Optional[datetime]
    scheduled_end:    Optional[datetime]
    actual_start:     Optional[datetime]
    actual_end:       Optional[datetime]
    duration_minutes: Optional[int]
    timezone:         str

    # Attendees
    attendees:        List[Dict[str, Any]]
    organizer_email:  Optional[str]
    participant_count: int

    # Status
    status:           str

    # Recording
    recording_url:               Optional[str]
    recording_size_bytes:         Optional[int]
    recording_duration_seconds:   Optional[int]
    recording_uploaded_at:        Optional[datetime]

    # Bot
    bot_enabled:   bool
    bot_status:    Optional[str]
    bot_joined_at: Optional[datetime]

    # Transcription
    transcript_status:     Optional[str]
    transcript_word_count: Optional[int]

    # AI
    ai_analysis_status: Optional[str]
    action_items_count: int

    # Meta
    tags:     List[str]
    meta_data: Dict[str, Any]

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# MEETING LIST ITEM (lighter)
# ============================================

class MeetingListItem(BaseModel):
    id:               UUID
    title:            str
    platform:         Optional[str]
    scheduled_start:  Optional[datetime]
    duration_minutes: Optional[int]
    status:           str
    participant_count: int
    action_items_count: int
    transcript_status: Optional[str]
    bot_enabled:       bool
    tags:              List[str]
    created_at:        datetime

    class Config:
        from_attributes = True


# ============================================
# FILTERS
# ============================================

class MeetingFilters(BaseModel):
    status:          Optional[List[MeetingStatus]] = None
    platform:        Optional[List[str]]           = None
    date_from:       Optional[datetime]            = None
    date_to:         Optional[datetime]            = None
    bot_enabled:     Optional[bool]                = None
    has_recording:   Optional[bool]                = None
    has_transcript:  Optional[bool]                = None
    created_by:      Optional[UUID]                = None
    tags:            Optional[List[str]]           = None


# ============================================
# SEARCH
# ============================================

class MeetingSearchParams(BaseModel):
    q:               Optional[str]            = Field(default=None, description="Full-text search query")
    status:          Optional[List[MeetingStatus]] = Field(default=None)
    platform:        Optional[List[MeetingPlatform]] = Field(default=None)
    date_from:       Optional[datetime]       = Field(default=None)
    date_to:         Optional[datetime]       = Field(default=None)
    created_by:      Optional[UUID]           = Field(default=None)
    has_recording:   Optional[bool]           = Field(default=None)
    has_transcript:  Optional[bool]           = Field(default=None)
    tags:            Optional[List[str]]      = Field(default=None)

    # Sorting
    sort_by:    str = Field(default="created_at", description="Field to sort by")
    sort_order: str = Field(default="desc",        description="asc or desc")

    # Pagination
    page:     int = Field(default=1,  ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

    @validator("sort_by")
    def validate_sort_by(cls, v):
        allowed = {"created_at", "scheduled_start", "title", "status", "updated_at"}
        if v not in allowed:
            raise ValueError(f"sort_by must be one of: {allowed}")
        return v

    @validator("sort_order")
    def validate_sort_order(cls, v):
        if v not in ("asc", "desc"):
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v


# ============================================
# RECORDING UPLOAD
# ============================================

class RecordingUploadRequest(BaseModel):
    file_name:      str   = Field(..., description="Original file name")
    file_size_bytes: int  = Field(..., gt=0, description="File size in bytes")
    content_type:   str   = Field(..., description="MIME type e.g. audio/mpeg")
    checksum_md5:   Optional[str] = Field(default=None, description="MD5 checksum for integrity")


# ============================================
# ATTENDEE REQUESTS
# ============================================

class AddAttendeeRequest(BaseModel):
    name: str = Field(..., description="Attendee name")
    email: str = Field(..., description="Attendee email")
    role: str = Field(default="attendee", description="Attendee role")

class RemoveAttendeeRequest(BaseModel):
    email: str = Field(..., description="Attendee email to remove")


class UploadRecordingResponse(BaseModel):
    upload_url:    str              = Field(description="Pre-signed S3 upload URL")
    upload_fields: Dict[str, str]   = Field(default_factory=dict, description="Additional form fields")
    s3_key:        str              = Field(description="S3 object key")
    expires_in:    int              = Field(description="URL expiry in seconds")
    meeting_id:    UUID


# ============================================
# BULK OPERATIONS
# ============================================

class BulkStatusUpdate(BaseModel):
    meeting_ids: List[UUID]   = Field(..., min_items=1, max_items=50)
    status:      MeetingStatus

class BulkDeleteRequest(BaseModel):
    meeting_ids: List[UUID] = Field(..., min_items=1, max_items=50)

class BulkOperationResult(BaseModel):
    succeeded:  List[UUID]
    failed:     List[Dict[str, Any]]
    total:      int
    success_count: int
    fail_count:    int