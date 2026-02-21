"""
Transcript Schemas
Vocaply Platform - Day 7

Pydantic models for transcript chunks, metadata, and search results.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, EmailStr


# ── Word Schema ────────────────────────────────
class TranscriptWord(BaseModel):
    word: str
    start: float
    end: float
    confidence: float
    speaker: Optional[int] = None

    class Config:
        from_attributes = True


# ── Transcript Chunk Schemas ───────────────────
class TranscriptBase(BaseModel):
    text: str
    speaker_id: Optional[str] = None
    speaker_name: Optional[str] = None
    speaker_email: Optional[EmailStr] = None
    start_time: float
    end_time: float
    duration: float
    confidence: Optional[float] = None
    language: str = "en"
    sequence_number: int


class TranscriptCreate(TranscriptBase):
    meeting_id: uuid.UUID
    company_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    words: Optional[List[Dict[str, Any]]] = None


class TranscriptUpdate(BaseModel):
    text: Optional[str] = None
    speaker_id: Optional[str] = None
    speaker_name: Optional[str] = None
    speaker_email: Optional[EmailStr] = None


class Transcript(TranscriptBase):
    id: uuid.UUID
    meeting_id: uuid.UUID
    words: Optional[List[Dict[str, Any]]] = None
    is_edited: bool
    edited_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Transcript Metadata Schemas ────────────────
class SpeakerStats(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    word_count: int
    duration: float


class TranscriptMetadataBase(BaseModel):
    total_chunks: int = 0
    total_words: int = 0
    total_duration_seconds: float = 0.0
    average_confidence: Optional[float] = None
    speaker_count: int = 0
    speakers: List[Dict[str, Any]] = []
    detected_language: Optional[str] = None


class TranscriptMetadata(TranscriptMetadataBase):
    id: uuid.UUID
    meeting_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Search Schemas ─────────────────────────────
class TranscriptSearchResult(BaseModel):
    chunk: Transcript
    relevance_score: Optional[float] = None


class TranscriptSearchResponse(BaseModel):
    results: List[Transcript]
    total: int
    query: str
