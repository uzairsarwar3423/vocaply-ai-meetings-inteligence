"""
Meeting Model
Vocaply Platform - Day 4: Meeting Management Backend
File: backend/app/models/meeting.py
"""
import uuid
import enum
from datetime import datetime
from typing import Optional, List, Any

from sqlalchemy import (
    Column, String, Text, Boolean, Integer,
    BigInteger, Float, DateTime, ForeignKey, Index, func, text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.base import Base


# ============================================
# ENUMS
# ============================================

class MeetingStatus(str, enum.Enum):
    SCHEDULED    = "scheduled"
    IN_PROGRESS  = "in_progress"
    TRANSCRIBING = "transcribing"
    ANALYZING    = "analyzing"
    COMPLETED    = "completed"
    CANCELLED    = "cancelled"
    FAILED       = "failed"


class MeetingPlatform(str, enum.Enum):
    ZOOM         = "zoom"
    GOOGLE_MEET  = "google_meet"
    TEAMS        = "teams"
    OTHER        = "other"


class BotStatus(str, enum.Enum):
    JOINING  = "joining"
    IN_CALL  = "in_call"
    LEFT     = "left"
    FAILED   = "failed"


class TranscriptStatus(str, enum.Enum):
    PENDING    = "pending"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    FAILED     = "failed"


class AIAnalysisStatus(str, enum.Enum):
    PENDING    = "pending"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    FAILED     = "failed"


# ============================================
# VALID STATUS TRANSITIONS
# ============================================
# Only these transitions are allowed.
# e.g., scheduled → in_progress is OK
#       completed → in_progress is NOT OK

VALID_STATUS_TRANSITIONS = {
    MeetingStatus.SCHEDULED:    [MeetingStatus.IN_PROGRESS,  MeetingStatus.CANCELLED],
    MeetingStatus.IN_PROGRESS:  [MeetingStatus.TRANSCRIBING, MeetingStatus.COMPLETED, MeetingStatus.FAILED],
    MeetingStatus.TRANSCRIBING: [MeetingStatus.ANALYZING,    MeetingStatus.FAILED],
    MeetingStatus.ANALYZING:    [MeetingStatus.COMPLETED,    MeetingStatus.FAILED],
    MeetingStatus.COMPLETED:    [],
    MeetingStatus.CANCELLED:    [],
    MeetingStatus.FAILED:       [MeetingStatus.SCHEDULED],   # Allow retry
}


# ============================================
# MEETING MODEL
# ============================================

class Meeting(Base):
    """
    Core meeting entity. Multi-tenant: always filter by company_id.
    
    Status flow:
        scheduled → in_progress → transcribing → analyzing → completed
                  ↘ cancelled
                                               ↘ failed → scheduled (retry)
    """
    __tablename__ = "meetings"

    # ------------------------------------------
    # PRIMARY KEY
    # ------------------------------------------
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4()
    )

    # ------------------------------------------
    # FOREIGN KEYS (Multi-tenancy)
    # ------------------------------------------
    company_id = Column(
        String,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_by = Column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # ------------------------------------------
    # MEETING DETAILS
    # ------------------------------------------
    title             = Column(String(500), nullable=False)
    description       = Column(Text,        nullable=True)
    meeting_url       = Column(Text,        nullable=True)
    meeting_password  = Column(String(100), nullable=True)
    notes             = Column(Text,        nullable=True)

    # ------------------------------------------
    # PLATFORM
    # ------------------------------------------
    platform            = Column(String(50),  nullable=True, index=True)
    platform_meeting_id = Column(String(255), nullable=True, index=True)
    platform_join_url   = Column(Text,        nullable=True)
    platform_start_url  = Column(Text,        nullable=True)

    # ------------------------------------------
    # SCHEDULING
    # ------------------------------------------
    scheduled_start   = Column(DateTime(timezone=True), nullable=True, index=True)
    scheduled_end     = Column(DateTime(timezone=True), nullable=True)
    actual_start      = Column(DateTime(timezone=True), nullable=True)
    actual_end        = Column(DateTime(timezone=True), nullable=True)
    duration_minutes  = Column(Integer,     nullable=True)
    timezone          = Column(String(50),  nullable=False, default="UTC")

    # ------------------------------------------
    # ATTENDEES (DEPRECATED - Use meeting_attendees table)
    # ------------------------------------------
    # Legacy JSONB field - will be removed after migration
    attendees = Column(JSONB, nullable=False, default=list, server_default="[]")
    organizer_email = Column(String(255), nullable=True)
    participant_count = Column(Integer, nullable=False, default=0)

    # ------------------------------------------
    # STATUS
    # ------------------------------------------
    status = Column(
        String(50),
        nullable=False,
        default=MeetingStatus.SCHEDULED.value,
        index=True
    )

    # ------------------------------------------
    # RECORDING
    # ------------------------------------------
    recording_url              = Column(Text,       nullable=True)
    recording_s3_key           = Column(Text,       nullable=True)
    recording_size_bytes       = Column(BigInteger,  nullable=True)
    recording_duration_seconds = Column(Integer,    nullable=True)
    recording_uploaded_at      = Column(DateTime(timezone=True), nullable=True)

    # ------------------------------------------
    # BOT
    # ------------------------------------------
    bot_enabled     = Column(Boolean,   nullable=False, default=False)
    bot_instance_id = Column(String(255), nullable=True)
    bot_status      = Column(String(50),  nullable=True)
    bot_joined_at   = Column(DateTime(timezone=True), nullable=True)
    bot_left_at     = Column(DateTime(timezone=True), nullable=True)

    # ------------------------------------------
    # TRANSCRIPTION
    # ------------------------------------------
    transcript_status       = Column(String(50), nullable=True)
    transcript_completed_at = Column(DateTime(timezone=True), nullable=True)
    transcript_word_count   = Column(Integer,    nullable=True)

    # ------------------------------------------
    # AI ANALYSIS
    # ------------------------------------------
    ai_analysis_status       = Column(String(50), nullable=True)
    ai_analysis_completed_at = Column(DateTime(timezone=True), nullable=True)
    action_items_count        = Column(Integer,   nullable=False, default=0)

    # ------------------------------------------
    # METADATA
    # ------------------------------------------
    tags     = Column(ARRAY(String), nullable=False, default=list, server_default="{}")
    meta_data = Column("metadata", JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))

    # ------------------------------------------
    # TIMESTAMPS
    # ------------------------------------------
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=func.now(), onupdate=datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # ------------------------------------------
    # RELATIONSHIPS
    # ------------------------------------------
    company = relationship("Company", back_populates="meetings", lazy="select")
    creator = relationship("User", back_populates="meetings", foreign_keys=[created_by], lazy="select")

    # Attendee relationships (normalized)
    meeting_attendees = relationship(
        "MeetingAttendee",
        back_populates="meeting",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Transcription relationships
    transcripts = relationship("Transcript", back_populates="meeting", cascade="all, delete-orphan", lazy="dynamic")
    transcript_metadata = relationship("TranscriptMetadata", back_populates="meeting", uselist=False, cascade="all, delete-orphan")
    
    # AI Analysis relationships
    # NOTE: this used to be a ``dynamic`` relationship which returns a
    # ``Query`` object instead of a list. that choice was made early on to
    # allow filtering (e.g. ``meeting.action_items.filter(...)``) without
    # triggering a SQL load, but it has a severe downside: dynamic
    # relationships **do not support eager loading**. the list endpoint
    # applies ``selectinload(Meeting.action_items)`` for performance, which
    # raised the ``InvalidRequestError`` seen in the logs:
    #
    #     'Meeting.action_items' does not support object population - eager
    #      loading cannot be applied.
    #
    # The simplest fix is to make the relationship normal (select/selectin)
    # so that the repository can eagerly load it without errors. callers
    # that previously treated ``meeting.action_items`` as a query will still
    # receive a list; there were no usages of the dynamic behaviour in the
    # codebase, so this change is safe and preserves the earlier performance
    # optimisation. if filtering is required it can be done by querying the
    # ``ActionItem`` table directly.
    action_items = relationship(
        "ActionItem",
        back_populates="meeting",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    summary = relationship(
        "MeetingSummary",
        back_populates="meeting",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="select",
    )
    
    # Bot sessions
    bot_session = relationship("BotSession", back_populates="meeting", uselist=False, cascade="all, delete-orphan")

    # ------------------------------------------
    # COMPOSITE INDEXES
    # ------------------------------------------
    __table_args__ = (
        # Existing indexes
        Index("idx_meetings_company_status",    "company_id", "status"),
        Index("idx_meetings_company_scheduled", "company_id", "scheduled_start"),
        Index("idx_meetings_company_created",   "company_id", "created_at"),
        Index("idx_meetings_platform_id",       "platform",   "platform_meeting_id"),

        # New optimized composite indexes
        Index("idx_meetings_company_status_created", "company_id", "status", "created_at"),
        Index("idx_meetings_company_platform", "company_id", "platform", "created_at"),
        Index("idx_meetings_scheduled_range", "company_id", "scheduled_start", "scheduled_end"),
        Index("idx_meetings_creator_status", "created_by", "status", "created_at"),

        {"extend_existing": True},
    )

    # ==========================================
    # HYBRID PROPERTIES
    # ==========================================

    @hybrid_property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @hybrid_property
    def is_active(self) -> bool:
        return self.deleted_at is None

    @hybrid_property
    def is_completed(self) -> bool:
        return self.status == MeetingStatus.COMPLETED.value

    @hybrid_property
    def actual_duration_seconds(self) -> Optional[int]:
        if self.actual_start and self.actual_end:
            return int((self.actual_end - self.actual_start).total_seconds())
        return None

    # ==========================================
    # VALIDATORS
    # ==========================================

    @validates("status")
    def validate_status_transition(self, key: str, new_status: str) -> str:
        """Enforce valid status transitions"""
        if self.status and self.status != new_status:
            try:
                current = MeetingStatus(self.status)
                new     = MeetingStatus(new_status)
                allowed = VALID_STATUS_TRANSITIONS.get(current, [])
                if new not in allowed:
                    allowed_values = [s.value for s in allowed]
                    raise ValueError(
                        f"Cannot transition from '{self.status}' to '{new_status}'. "
                        f"Allowed transitions: {allowed_values or 'none'}"
                    )
            except KeyError:
                raise ValueError(f"Unknown status: {new_status}")
        return new_status

    @validates("platform")
    def validate_platform(self, key: str, value: Optional[str]) -> Optional[str]:
        if value is not None:
            valid = [p.value for p in MeetingPlatform]
            if value not in valid:
                raise ValueError(f"Invalid platform '{value}'. Allowed: {valid}")
        return value

    @validates("attendees")
    def validate_attendees(self, key: str, value: Any) -> Any:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("Attendees must be a list")
        for i, a in enumerate(value):
            if not isinstance(a, dict):
                raise ValueError(f"Attendee[{i}] must be a dict")
            if "email" not in a:
                raise ValueError(f"Attendee[{i}] is missing 'email'")
        return value

    # ==========================================
    # BUSINESS LOGIC METHODS
    # ==========================================

    def can_transition_to(self, new_status: str) -> bool:
        """Check if a status transition is valid without applying it"""
        try:
            current = MeetingStatus(self.status)
            new     = MeetingStatus(new_status)
            return new in VALID_STATUS_TRANSITIONS.get(current, [])
        except ValueError:
            return False

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        self.deleted_at = None

    def start_meeting(self) -> None:
        self.status      = MeetingStatus.IN_PROGRESS.value
        self.actual_start = datetime.utcnow()

    def end_meeting(self) -> None:
        self.actual_end = datetime.utcnow()
        if self.actual_start:
            seconds = (self.actual_end - self.actual_start).total_seconds()
            self.duration_minutes = int(seconds / 60)

    def add_attendee(self, email: str, name: str = None, role: str = "attendee") -> None:
        """Add attendee using the normalized MeetingAttendee table"""
        from app.models.meeting_attendee import MeetingAttendee

        # Check if attendee already exists
        existing = next((a for a in self.meeting_attendees if a.email == email), None)
        if existing:
            return  # Already exists

        # Create new attendee
        attendee = MeetingAttendee(
            meeting_id=self.id,
            company_id=self.company_id,
            email=email,
            name=name or email,
            role=role,
        )
        self.meeting_attendees.append(attendee)
        self.participant_count = len(self.meeting_attendees)

    def remove_attendee(self, email: str) -> None:
        """Remove attendee from the normalized table"""
        self.meeting_attendees = [a for a in self.meeting_attendees if a.email != email]
        self.participant_count = len(self.meeting_attendees)

    def get_attendee(self, email: str) -> Optional["MeetingAttendee"]:
        """Get attendee by email"""
        return next((a for a in self.meeting_attendees if a.email == email), None)

    def mark_attendee_joined(self, email: str) -> None:
        """Mark an attendee as joined"""
        attendee = self.get_attendee(email)
        if attendee:
            attendee.mark_joined()

    def mark_attendee_left(self, email: str) -> None:
        """Mark an attendee as left"""
        attendee = self.get_attendee(email)
        if attendee:
            attendee.mark_left()

    def to_dict(self) -> dict:
        return {
            "id":                       str(self.id),
            "company_id":               str(self.company_id),
            "created_by":               str(self.created_by) if self.created_by else None,
            "title":                    self.title,
            "description":              self.description,
            "meeting_url":              self.meeting_url,
            "platform":                 self.platform,
            "platform_meeting_id":      self.platform_meeting_id,
            "platform_join_url":        self.platform_join_url,
            "scheduled_start":          self.scheduled_start.isoformat()  if self.scheduled_start  else None,
            "scheduled_end":            self.scheduled_end.isoformat()    if self.scheduled_end    else None,
            "actual_start":             self.actual_start.isoformat()     if self.actual_start     else None,
            "actual_end":               self.actual_end.isoformat()       if self.actual_end       else None,
            "duration_minutes":         self.duration_minutes,
            "timezone":                 self.timezone,
            "attendees": [attendee.to_dict() for attendee in self.meeting_attendees] if self.meeting_attendees else [],
            "organizer_email":          self.organizer_email,
            "participant_count":        self.participant_count,
            "status":                   self.status,
            "recording_url":            self.recording_url,
            "recording_size_bytes":     self.recording_size_bytes,
            "recording_duration_seconds": self.recording_duration_seconds,
            "bot_enabled":              self.bot_enabled,
            "bot_status":               self.bot_status,
            "bot_joined_at":            self.bot_joined_at.isoformat()    if self.bot_joined_at    else None,
            "transcript_status":        self.transcript_status,
            "transcript_word_count":    self.transcript_word_count,
            "ai_analysis_status":       self.ai_analysis_status,
            "action_items_count":       self.action_items_count,
            "tags":                     self.tags or [],
            "notes":                    self.notes,
            "meta_data":                 self.meta_data or {},
            "created_at":               self.created_at.isoformat()       if self.created_at       else None,
            "updated_at":               self.updated_at.isoformat()       if self.updated_at       else None,
        }

    def __repr__(self) -> str:
        return f"<Meeting id={self.id} title={self.title!r} status={self.status}>"