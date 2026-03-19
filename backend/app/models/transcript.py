"""
Transcript Model
Vocaply Platform - Day 7

Stores individual transcript chunks with speaker info, timestamps, and confidence.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, String, Text, Integer, Float,
    DateTime, ForeignKey, Index, Boolean, text as sa_text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Transcript(Base):
    """
    Individual transcript chunk (one speaker turn).
    Stored as granular segments for search, speaker filtering, timeline view.
    """
    __tablename__ = "transcripts"

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

    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # ── Content ──────────────────────────────────
    text = Column(Text, nullable=False)
    
    # ── Speaker Info ─────────────────────────────
    speaker_id = Column(String(100), nullable=True)      # "speaker_0", "speaker_1" from Deepgram
    speaker_name = Column(String(255), nullable=True)    # Resolved name if matched
    speaker_email = Column(String(255), nullable=True, index=True)
    
    # ── Timing ───────────────────────────────────
    start_time = Column(Float, nullable=False)            # Seconds from meeting start
    end_time = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)              # end - start
    timestamp = Column(DateTime(timezone=True), nullable=True)  # Absolute time (meeting.start + offset)
    
    # ── Metadata ─────────────────────────────────
    confidence = Column(Float, nullable=True)             # 0.0-1.0 from Deepgram
    language = Column(String(10), nullable=False, default="en")
    channel = Column(Integer, nullable=True)              # Audio channel (multi-track)
    sequence_number = Column(Integer, nullable=False)     # Order within meeting
    
    # Words with timestamps (for precise search/playback)
    words = Column(JSONB, nullable=True)                  # [{"word": "hello", "start": 0.5, "end": 0.8, "confidence": 0.95}]
    
    # ── Edit History ─────────────────────────────
    is_edited = Column(Boolean, nullable=False, default=False)
    original_text = Column(Text, nullable=True)           # Backup before manual edit
    edited_by = Column(String, nullable=True)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    
    # ── Timestamps ───────────────────────────────
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # ── Relationships ────────────────────────────
    meeting = relationship("Meeting", back_populates="transcripts")
    company = relationship("Company")
    user = relationship("User")

    # ── Indexes ──────────────────────────────────
    __table_args__ = (
        # Existing indexes
        Index("idx_transcripts_meeting_seq", "meeting_id", "sequence_number"),
        Index("idx_transcripts_speaker", "meeting_id", "speaker_id"),
        Index("idx_transcripts_time", "meeting_id", "start_time"),
        Index("idx_transcripts_search", sa_text("to_tsvector('english', text)"), postgresql_using="gin"),

        # New optimized indexes
        Index("idx_transcripts_meeting_time", "meeting_id", "start_time", "end_time"),
        Index("idx_transcripts_speaker_email", "meeting_id", "speaker_email", "start_time"),
        Index("idx_transcripts_company_created", "company_id", "created_at"),
    )

    # ── Properties ───────────────────────────────
    @property
    def display_speaker(self) -> str:
        """Return best available speaker identifier"""
        if self.speaker_name:
            return self.speaker_name
        if self.speaker_email:
            return self.speaker_email.split("@")[0].title()
        if self.speaker_id:
            return f"Speaker {self.speaker_id.replace('speaker_', '').upper()}"
        return "Unknown Speaker"

    @property
    def formatted_time(self) -> str:
        """Format start time as MM:SS"""
        mins = int(self.start_time // 60)
        secs = int(self.start_time % 60)
        return f"{mins}:{secs:02d}"

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    def __repr__(self) -> str:
        return f"<Transcript id={self.id} meeting={self.meeting_id} speaker={self.speaker_id}>"


# ============================================
# TRANSCRIPT METADATA (per meeting)
# ============================================

class TranscriptMetadata(Base):
    """
    Aggregate metadata for an entire meeting's transcript.
    Stored separately from individual chunks for performance.
    """
    __tablename__ = "transcript_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.uuid_generate_v4())
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    # ── Aggregates ───────────────────────────────
    total_chunks = Column(Integer, nullable=False, default=0)
    total_words = Column(Integer, nullable=False, default=0)
    total_duration_seconds = Column(Float, nullable=False, default=0.0)
    average_confidence = Column(Float, nullable=True)
    
    # ── Speakers ─────────────────────────────────
    speaker_count = Column(Integer, nullable=False, default=0)
    speakers = Column(JSONB, nullable=False, default=list, server_default="[]")
    # Format: [{"id": "speaker_0", "name": "John", "email": "john@co.com", "word_count": 523, "duration": 120.5}]
    
    # ── Language ─────────────────────────────────
    detected_language = Column(String(10), nullable=True)
    language_confidence = Column(Float, nullable=True)
    
    # ── Processing ───────────────────────────────
    deepgram_request_id = Column(String(255), nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    deepgram_model = Column(String(50), nullable=True)
    
    # ── Costs ────────────────────────────────────
    audio_duration_billed = Column(Float, nullable=True)  # Deepgram bills by audio length
    estimated_cost_usd = Column(Float, nullable=True)
    
    # ── Timestamps ───────────────────────────────
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    meeting = relationship("Meeting", back_populates="transcript_metadata")

    def __repr__(self) -> str:
        return f"<TranscriptMetadata meeting={self.meeting_id} chunks={self.total_chunks}>"