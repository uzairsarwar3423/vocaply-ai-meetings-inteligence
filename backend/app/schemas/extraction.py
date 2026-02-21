"""
Extraction Schemas
Vocaply Platform - Day 10: Action Item Extraction Logic
File: backend/app/schemas/extraction.py

Request/response schemas for triggering AI analysis and
returning extraction results.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================
# TRIGGER ANALYSIS REQUEST
# ============================================

class AnalyzeMeetingRequest(BaseModel):
    """
    Body for POST /api/v1/meetings/{id}/analyze.
    All fields are optional — defaults are applied by the service.
    """
    force_rerun: bool = Field(
        default=False,
        description="If True, re-runs extraction even if already completed.",
    )
    features: List[str] = Field(
        default=["action_items", "summary", "key_decisions"],
        description=(
            "Which AI features to run. "
            "Options: action_items, summary, key_decisions, "
            "participant_analysis, topic_extraction, sentiment_analysis"
        ),
    )
    model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use for extraction.",
    )
    chunk_size_words: int = Field(
        default=3000,
        ge=500,
        le=10000,
        description="Maximum words per transcript chunk sent to the model.",
    )
    min_confidence: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score to include an action item.",
    )


# ============================================
# EXTRACTED ACTION ITEM (raw AI output)
# ============================================

class ExtractedActionItem(BaseModel):
    """
    A single action item as returned directly by GPT-4o-mini
    before any DB operations.
    """
    title: str
    description: Optional[str] = None
    assignee_name: Optional[str] = None
    assignee_email: Optional[str] = None
    due_date: Optional[str] = None          # "YYYY-MM-DD" or natural language
    priority: str = "medium"
    category: str = "other"
    confidence: float = 0.5
    transcript_quote: Optional[str] = None
    transcript_start_time: Optional[float] = None


# ============================================
# EXTRACTION RESULT
# ============================================

class ExtractionSummary(BaseModel):
    """Aggregate result of a completed analysis run."""
    meeting_id: uuid.UUID
    task_id: Optional[str] = None           # Celery task ID
    features_requested: List[str]
    status: str                             # "queued" | "processing" | "completed" | "failed"
    action_items_extracted: int = 0
    duplicates_skipped: int = 0
    matched_to_users: int = 0
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    error: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


# ============================================
# ANALYSIS STATUS RESPONSE
# ============================================

class AnalysisStatusResponse(BaseModel):
    """Returned immediately when analysis is queued."""
    meeting_id: uuid.UUID
    task_id: Optional[str]
    status: str
    message: str
    estimated_seconds: Optional[int] = None
