"""
Bot Session Model
Tracks bot instances and their lifecycle
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, String, DateTime, ForeignKey,
    Integer, Float, Boolean, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class BotSession(Base):
    """
    Tracks a bot instance lifecycle for a meeting.
    
    Bot lifecycle:
    INITIALIZING → AVAILABLE → ASSIGNED → JOINING → 
    IN_MEETING → RECORDING → LEAVING → COMPLETED
    """
    __tablename__ = "bot_sessions"

    # ── Primary Key ──────────────────────────────
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4()
    )

    # ── Foreign Keys ─────────────────────────────
    meeting_id = Column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One bot per meeting
        index=True
    )

    company_id = Column(
        String,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # ── Bot Info ─────────────────────────────────
    bot_instance_id = Column(String(100), nullable=True)  # ID from bot service
    bot_platform = Column(String(50), nullable=False)     # zoom, google_meet, teams
    
    # ── Status ───────────────────────────────────
    status = Column(String(50), nullable=False, default="initializing")
    # Values: initializing, available, assigned, joining, in_meeting, 
    #         recording, leaving, completed, failed, terminated
    
    # ── Lifecycle Timestamps ─────────────────────
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    joined_at = Column(DateTime(timezone=True), nullable=True)
    left_at = Column(DateTime(timezone=True), nullable=True)
    
    # ── Recording ────────────────────────────────
    recording_started = Column(DateTime(timezone=True), nullable=True)
    recording_completed = Column(DateTime(timezone=True), nullable=True)
    recording_url = Column(String(500), nullable=True)
    recording_duration = Column(Float, nullable=True)  # Seconds
    
    # ── Monitoring ───────────────────────────────
    participant_count = Column(Integer, nullable=False, default=0)
    is_alone = Column(Boolean, nullable=False, default=False)
    alone_since = Column(DateTime(timezone=True), nullable=True)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    
    # ── Error Tracking ───────────────────────────
    error = Column(String(500), nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    # ── Metadata ─────────────────────────────────
    bot_metadata = Column(JSONB, nullable=True, default=dict)
    # Stores: pool info, browser info, audio stats, etc.
    
    # ── Timestamps ───────────────────────────────
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # ── Relationships ────────────────────────────
    meeting = relationship("Meeting", back_populates="bot_session")
    company = relationship("Company")

    # ── Indexes ──────────────────────────────────
    __table_args__ = (
        Index("idx_bot_sessions_status", "status"),
        Index("idx_bot_sessions_company", "company_id", "status"),
    )

    # ── Properties ───────────────────────────────
    @property
    def duration(self) -> Optional[float]:
        """Get session duration in seconds"""
        if not self.joined_at:
            return None
        
        end = self.left_at or datetime.utcnow()
        return (end - self.joined_at).total_seconds()

    @property
    def is_active(self) -> bool:
        """Check if bot is currently active"""
        return self.status in ['joining', 'in_meeting', 'recording']

    def __repr__(self) -> str:
        return f"<BotSession id={self.id} meeting={self.meeting_id} status={self.status}>"