"""
Calendar Event Model
Vocaply Platform - Day 7: Calendar Sync & Bot Auto-Join
"""

import uuid
from datetime import datetime
from typing import Optional, Any, List

from sqlalchemy import (
    Column, String, Text, Boolean, Integer,
    DateTime, ForeignKey, Index, func, text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.base import Base


class CalendarEvent(Base):
    """
    Synced calendar event from Google or Outlook.
    Used for meeting detection and bot auto-join scheduling.
    """
    __tablename__ = "calendar_events"

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
    # FOREIGN KEYS
    # ------------------------------------------
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    company_id = Column(
        String,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    meeting_id = Column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # ------------------------------------------
    # PROVIDER INFO
    # ------------------------------------------
    calendar_provider = Column(String(50), nullable=False)  # 'google', 'outlook'
    external_event_id = Column(String(255), nullable=False)
    
    # ------------------------------------------
    # EVENT DETAILS
    # ------------------------------------------
    title       = Column(String(500), nullable=False)
    description = Column(Text,        nullable=True)
    location    = Column(String(500), nullable=True)
    start_time  = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time    = Column(DateTime(timezone=True), nullable=False)
    timezone    = Column(String(100), nullable=True)
    all_day     = Column(Boolean,     default=False, server_default='false')
    
    # ------------------------------------------
    # MEETING DETECTION
    # ------------------------------------------
    has_meeting_url  = Column(Boolean,    default=False, server_default='false')
    meeting_url      = Column(Text,       nullable=True)
    meeting_platform = Column(String(50), nullable=True)
    
    # ------------------------------------------
    # AUTO-JOIN SETTINGS & STATUS
    # ------------------------------------------
    auto_join_enabled      = Column(Boolean, default=False, server_default='false')
    auto_join_scheduled    = Column(Boolean, default=False, server_default='false')
    auto_join_executed     = Column(Boolean, default=False, server_default='false')
    auto_join_scheduled_at = Column(DateTime(timezone=True), nullable=True)
    
    # ------------------------------------------
    # METADATA & SYNC
    # ------------------------------------------
    raw_event_data = Column(JSONB,   nullable=False, default=dict, server_default="'{}'::jsonb")
    attendees      = Column(JSONB,   nullable=False, default=list, server_default="'[]'::jsonb")
    organizer      = Column(JSONB,   nullable=False, default=dict, server_default="'{}'::jsonb")
    last_synced_at = Column(DateTime(timezone=True), default=datetime.utcnow, server_default=func.now())
    sync_version   = Column(Integer,  default=1, server_default='1')
    
    # ------------------------------------------
    # TIMESTAMPS
    # ------------------------------------------
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=func.now(), onupdate=datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # ------------------------------------------
    # RELATIONSHIPS
    # ------------------------------------------
    user    = relationship("User",    lazy="select")
    company = relationship("Company", lazy="select")
    meeting = relationship("Meeting", lazy="select")

    # ------------------------------------------
    # CONSTRAINTS & INDEXES
    # ------------------------------------------
    __table_args__ = (
        # Prevent duplicate events from the same provider for a single user
        UniqueConstraint(
            'user_id', 'calendar_provider', 'external_event_id',
            name='uq_calendar_event_external_id'
        ),
        # Index for fast range queries by user
        Index('idx_cal_events_user_start', 'user_id', 'start_time'),
        # Index for scheduler lookups
        Index('idx_cal_events_scheduler', 'auto_join_enabled', 'auto_join_scheduled', 'start_time'),
        {"extend_existing": True},
    )

    # ------------------------------------------
    # PROPERTIES
    # ------------------------------------------
    @hybrid_property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @hybrid_property
    def is_active(self) -> bool:
        return self.deleted_at is None

    # ------------------------------------------
    # METHODS
    # ------------------------------------------
    def to_dict(self) -> dict:
        return {
            "id":                     str(self.id),
            "user_id":                self.user_id,
            "company_id":             self.company_id,
            "meeting_id":             str(self.meeting_id) if self.meeting_id else None,
            "calendar_provider":      self.calendar_provider,
            "external_event_id":      self.external_event_id,
            "title":                  self.title,
            "description":            self.description,
            "location":               self.location,
            "start_time":             self.start_time.isoformat() if self.start_time else None,
            "end_time":               self.end_time.isoformat()   if self.end_time   else None,
            "timezone":               self.timezone,
            "all_day":                self.all_day,
            "has_meeting_url":        self.has_meeting_url,
            "meeting_url":            self.meeting_url,
            "meeting_platform":       self.meeting_platform,
            "auto_join_enabled":      self.auto_join_enabled,
            "auto_join_scheduled":    self.auto_join_scheduled,
            "auto_join_executed":     self.auto_join_executed,
            "auto_join_scheduled_at": self.auto_join_scheduled_at.isoformat() if self.auto_join_scheduled_at else None,
            "last_synced_at":         self.last_synced_at.isoformat() if self.last_synced_at else None,
            "created_at":             self.created_at.isoformat()     if self.created_at     else None,
            "updated_at":             self.updated_at.isoformat()     if self.updated_at     else None,
        }

    def __repr__(self) -> str:
        return f"<CalendarEvent id={self.id} title={self.title!r} provider={self.calendar_provider}>"