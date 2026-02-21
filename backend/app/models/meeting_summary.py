"""
Meeting Summary Model
Vocaply Platform - Day 13

Stores AI-generated executive summaries, key points, and decisions.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy import (
    Column, String, Text, Float,
    DateTime, ForeignKey, Boolean, Integer
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class MeetingSummary(Base):
    """
    Consolidated AI analysis of a meeting.
    Stored as a single record per meeting.
    """
    __tablename__ = "meeting_summaries"

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
        unique=True,
        nullable=False,
        index=True
    )

    company_id = Column(
        String,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # ── Content ──────────────────────────────────
    short_summary = Column(String(1000), nullable=True)   # One-liner or brief overview
    detailed_summary = Column(Text, nullable=True)        # Executive summary (markdown)
    
    # ── Structured Data ──────────────────────────
    # List of key discussion points
    key_points = Column(ARRAY(Text), nullable=False, default=list, server_default="{}")
    
    # List of specific decisions made
    decisions = Column(ARRAY(Text), nullable=False, default=list, server_default="{}")
    
    # Topics discussed with sentiment/relevance
    # Format: [{"topic": "Budget", "sentiment": "neutral", "importance": 0.8}]
    topics = Column(JSONB, nullable=False, default=list, server_default="[]")
    
    # Overall meeting sentiment: positive, neutral, negative
    sentiment = Column(String(50), nullable=True)
    
    # ── Metadata ─────────────────────────────────
    model_version = Column(String(50), nullable=True)     # e.g., "gpt-4o-mini"
    generation_time_seconds = Column(Float, nullable=True)
    token_usage = Column(Integer, nullable=True)          # Total tokens used for this summary
    
    # ── Timestamps ───────────────────────────────
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # ── Relationships ────────────────────────────
    meeting = relationship("Meeting", back_populates="summary")
    company = relationship("Company")

    def __repr__(self) -> str:
        return f"<MeetingSummary meeting={self.meeting_id}>"
