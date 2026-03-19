"""
Meeting Attendee Model
Normalized attendee information for meetings.
Replaces the JSONB attendees field in meetings table.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, String, Boolean,
    DateTime, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class MeetingAttendee(Base):
    """
    Normalized attendee information for meetings.
    Provides better querying, indexing, and relational integrity.
    """
    __tablename__ = "meeting_attendees"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4()
    )

    # Foreign Keys
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

    # User linkage (if registered user)
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Attendee Information
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="attendee")  # organizer, attendee

    # Participation Tracking
    joined_at = Column(DateTime(timezone=True), nullable=True)
    left_at = Column(DateTime(timezone=True), nullable=True)
    is_present = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=func.now(), onupdate=datetime.utcnow)

    # Relationships
    meeting = relationship("Meeting", back_populates="meeting_attendees")
    company = relationship("Company")
    user = relationship("User")

    # Business Logic Methods
    def mark_joined(self) -> None:
        """Mark attendee as joined"""
        if not self.joined_at:
            self.joined_at = datetime.utcnow()
            self.is_present = True

    def mark_left(self) -> None:
        """Mark attendee as left"""
        if not self.left_at:
            self.left_at = datetime.utcnow()

    @property
    def duration_seconds(self) -> Optional[int]:
        """Calculate participation duration"""
        if self.joined_at and self.left_at:
            return int((self.left_at - self.joined_at).total_seconds())
        elif self.joined_at:
            return int((datetime.utcnow() - self.joined_at).total_seconds())
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "id": str(self.id),
            "meeting_id": str(self.meeting_id),
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "user_id": str(self.user_id) if self.user_id else None,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "left_at": self.left_at.isoformat() if self.left_at else None,
            "is_present": self.is_present,
            "duration_seconds": self.duration_seconds,
        }

    def __repr__(self):
        return f"<MeetingAttendee meeting={self.meeting_id} email={self.email} role={self.role}>"