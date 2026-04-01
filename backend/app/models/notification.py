"""
Notification Model
Vocaply Platform - Day 26: Notifications & Reminders

Stores in-app notifications for users. Each record represents one
notification sent (or to be sent) across one or more channels.
"""
import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Boolean,
    DateTime, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class NotificationType(str, enum.Enum):
    ACTION_ITEM_ASSIGNED = "action_item_assigned"
    REMINDER             = "reminder"
    OVERDUE              = "overdue"
    DAILY_DIGEST         = "daily_digest"
    SYSTEM               = "system"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL  = "email"
    SLACK  = "slack"


class Notification(Base):
    """
    In-app notification record. One row per notification per user.
    """
    __tablename__ = "notifications"

    # ── Primary Key ──────────────────────────────
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4(),
    )

    # ── Recipient ────────────────────────────────
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id = Column(
        String,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Content ──────────────────────────────────
    type = Column(
        String(50),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)
    body  = Column(Text, nullable=True)

    # ── State ────────────────────────────────────
    is_read = Column(Boolean, nullable=False, default=False, server_default="false")
    read_at = Column(DateTime(timezone=True), nullable=True)

    # ── Delivery Metadata ────────────────────────
    # {"meeting_id": "...", "action_item_id": "...", "url": "/action-items/..."}
    metadata_     = Column("metadata", JSONB, nullable=True, default=dict)
    # ["in_app", "email"] — channels already sent
    sent_channels = Column(JSONB, nullable=False, default=list, server_default="[]")

    # ── Scheduling ───────────────────────────────
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at      = Column(DateTime(timezone=True), nullable=True)

    # ── Timestamps ───────────────────────────────
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ── Relationships ────────────────────────────
    user    = relationship("User")
    company = relationship("Company")

    # ── Indexes ──────────────────────────────────
    __table_args__ = (
        Index("idx_notifications_user_read",    "user_id", "is_read", "created_at"),
        Index("idx_notifications_company_type", "company_id", "type", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Notification id={self.id} user={self.user_id} type={self.type} read={self.is_read}>"
