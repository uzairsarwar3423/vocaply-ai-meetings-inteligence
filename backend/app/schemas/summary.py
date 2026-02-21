"""
Meeting Summary Schemas
Vocaply Platform - Day 13

Pydantic models for AI-generated meeting summaries.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TopicSchema(BaseModel):
    topic: str
    sentiment: Optional[str] = None
    importance: float = 0.5


class MeetingSummaryBase(BaseModel):
    short_summary: Optional[str] = Field(None, max_length=1000)
    detailed_summary: Optional[str] = None
    key_points: List[str] = []
    decisions: List[str] = []
    topics: List[TopicSchema] = []
    sentiment: Optional[str] = None
    
    model_config = {
        "protected_namespaces": ()
    }


class MeetingSummaryCreate(MeetingSummaryBase):
    meeting_id: uuid.UUID
    company_id: uuid.UUID
    model_version: Optional[str] = None
    token_usage: Optional[int] = None


class MeetingSummaryUpdate(MeetingSummaryBase):
    pass


class MeetingSummary(MeetingSummaryBase):
    id: uuid.UUID
    meeting_id: uuid.UUID
    company_id: uuid.UUID
    model_version: Optional[str] = None
    generation_time_seconds: Optional[float] = None
    token_usage: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }
