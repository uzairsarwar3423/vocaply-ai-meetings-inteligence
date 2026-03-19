"""
Action Item Model
Vocaply Platform - Day 10

Stores AI-extracted or manually created tasks from meetings.
"""
from sqlalchemy import Index
import uuid
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, String, Text, Float,
    DateTime, ForeignKey, Boolean, Integer
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class ActionItemStatus(str, enum.Enum):
    PENDING     = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED   = "completed"
    CANCELLED   = "cancelled"


class ActionItemPriority(str, enum.Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"
    URGENT = "urgent"


class ActionItem(Base):
    """
    Tasks or action items extracted from a meeting.
    Can be assigned to users or identified by email.
    """
    __tablename__ = "action_items"

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
        index=True
    )

    company_id = Column(
        String,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Assigned to a registered user
    assigned_to_id = Column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # ── Content ──────────────────────────────────
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # ── AI Extraction Metadata ───────────────────
    is_ai_generated = Column(Boolean, nullable=False, default=True)
    confidence_score = Column(Float, nullable=True)       # 0.0-1.0
    transcript_quote = Column(Text, nullable=True)        # The text it was extracted from
    transcript_start_time = Column(Float, nullable=True) # Point in meeting
    
    # ── Assignment Info ──────────────────────────
    assignee_name = Column(String(255), nullable=True)
    assignee_email = Column(String(255), nullable=True, index=True)
    
    # ── Status & Priority ────────────────────────
    status = Column(
        String(50),
        nullable=False,
        default=ActionItemStatus.PENDING.value,
        index=True
    )
    priority = Column(
        String(50),
        nullable=False,
        default=ActionItemPriority.MEDIUM.value,
        index=True
    )
    
    # ── Dates ────────────────────────────────────
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # ── Timestamps ───────────────────────────────
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # ── Relationships ────────────────────────────
    meeting = relationship("Meeting", back_populates="action_items")
    company = relationship("Company")
    assigned_to = relationship("User")

    # ── Indexes ──────────────────────────────────
    __table_args__ = (
        # New optimized composite indexes
        Index("idx_action_items_company_status", "company_id", "status", "created_at"),
        Index("idx_action_items_assigned_due", "assigned_to_id", "due_date", "status"),
        Index("idx_action_items_meeting_status", "meeting_id", "status"),
        Index("idx_action_items_priority_status", "company_id", "priority", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ActionItem id={self.id} meeting={self.meeting_id} status={self.status}>"
