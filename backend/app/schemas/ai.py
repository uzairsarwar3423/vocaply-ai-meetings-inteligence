"""
AI Schemas
Vocaply Platform - Day 9: OpenAI Integration & Prompt Engineering
File: backend/app/schemas/ai.py

Pydantic v2 schemas for:
  - AI usage records (read / list / aggregation)
  - Trigger requests (run analysis on demand)
  - AI feature results (per-feature typed responses)
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ============================================
# BASE
# ============================================

class _Base(BaseModel):
    model_config = {"from_attributes": True}


# ============================================
# AI USAGE SCHEMAS
# ============================================

class AIUsageBase(_Base):
    company_id:        str
    meeting_id:        Optional[UUID]  = None
    feature_type:      str
    model:             str             = "gpt-4o-mini"
    status:            str
    prompt_tokens:     int             = 0
    completion_tokens: int             = 0
    total_tokens:      int             = 0
    prompt_cost:       Decimal         = Decimal("0")
    completion_cost:   Decimal         = Decimal("0")
    total_cost:        Decimal         = Decimal("0")
    latency_ms:        Optional[int]   = None
    was_cached:        bool            = False
    retry_count:       int             = 0
    error_message:     Optional[str]   = None
    usage_date:        Optional[datetime] = None


class AIUsageRead(AIUsageBase):
    id:             UUID
    prompt_version: Optional[str] = None
    request_id:     Optional[str] = None
    created_at:     datetime


class AIUsageList(_Base):
    items:      List[AIUsageRead]
    total:      int
    page:       int
    page_size:  int


# ============================================
# DAILY / MONTHLY AGGREGATION
# ============================================

class AIUsageSummary(_Base):
    """Aggregated usage returned by the API for a period."""
    company_id:        str
    period:            str            # "2024-01-15" (day) or "2024-01" (month)
    total_requests:    int            = 0
    cached_requests:   int            = 0
    prompt_tokens:     int            = 0
    completion_tokens: int            = 0
    total_tokens:      int            = 0
    total_cost_usd:    float          = 0.0
    feature_breakdown: Dict[str, int] = Field(default_factory=dict)


class AIUsageCompanyStats(_Base):
    """Stats for the analytics dashboard."""
    company_id:           str
    today:                AIUsageSummary
    this_month:           AIUsageSummary
    monthly_budget_usd:   float = 50.0
    budget_used_percent:  float = 0.0
    is_over_budget:       bool  = False


# ============================================
# TRIGGER / RUN REQUESTS
# ============================================

class AIAnalysisRequest(_Base):
    """Body for POST /ai/analyze – trigger an AI feature for a meeting."""
    meeting_id:       UUID
    feature_type:     str = Field(
        ...,
        description=(
            "One of: meeting_summary, action_item_extraction, key_decisions, "
            "participant_analysis, topic_extraction, sentiment_analysis"
        ),
    )
    template_version: Optional[str]  = Field(
        None,
        description="Pin a specific prompt version; omit to use latest.",
    )
    use_cache:        bool            = True
    model:            str             = "gpt-4o-mini"

    @field_validator("feature_type")
    @classmethod
    def validate_feature_type(cls, v: str) -> str:
        allowed = {
            "meeting_summary", "action_item_extraction", "key_decisions",
            "participant_analysis", "topic_extraction", "sentiment_analysis",
        }
        if v not in allowed:
            raise ValueError(f"feature_type must be one of {allowed}")
        return v


class BulkAIAnalysisRequest(_Base):
    """Run multiple features at once for a meeting."""
    meeting_id:    UUID
    feature_types: List[str] = Field(
        ...,
        min_length=1,
        description="List of feature_type strings.",
    )
    use_cache:     bool = True
    model:         str  = "gpt-4o-mini"


# ============================================
# FEATURE RESULT SCHEMAS
# ============================================

class MeetingSummaryResult(_Base):
    executive_summary:           str
    main_topics:                 List[str]          = []
    key_outcomes:                List[str]          = []
    decisions_made:              List[str]          = []
    open_questions:              List[str]          = []
    next_steps:                  List[str]          = []
    sentiment:                   str                = "neutral"
    meeting_effectiveness_score: Optional[int]      = None
    word_count:                  Optional[int]      = None


class ActionItemResult(_Base):
    title:          str
    description:    Optional[str] = None
    assignee_name:  Optional[str] = None
    assignee_email: Optional[str] = None
    due_date:       Optional[str] = None
    priority:       str           = "medium"
    category:       str           = "other"
    confidence:     float         = 1.0


class ActionItemsResult(_Base):
    action_items:     List[ActionItemResult] = []
    total_count:      int                    = 0
    unassigned_count: int                    = 0


class DecisionResult(_Base):
    title:          str
    description:    Optional[str] = None
    decision_maker: Optional[str] = None
    rationale:      Optional[str] = None
    impact:         str           = "medium"
    category:       str           = "other"
    confidence:     float         = 1.0


class KeyDecisionsResult(_Base):
    decisions:   List[DecisionResult] = []
    total_count: int                  = 0


class ParticipantResult(_Base):
    name:                  str
    email:                 Optional[str] = None
    role:                  str           = "contributor"
    speaking_time_percent: Optional[int] = None
    key_contributions:     List[str]     = []
    sentiment:             str           = "neutral"
    engagement_level:      str           = "medium"


class ParticipantAnalysisResult(_Base):
    participants:    List[ParticipantResult] = []
    total_speakers:  int                     = 0
    dominant_speaker: Optional[str]          = None
    meeting_dynamic: str                     = "discussion"


class TopicResult(_Base):
    name:               str
    description:        Optional[str] = None
    time_spent_percent: Optional[int] = None
    subtopics:          List[str]     = []
    category:           str           = "other"
    keywords:           List[str]     = []


class TopicExtractionResult(_Base):
    topics:                 List[TopicResult] = []
    total_topics:           int               = 0
    primary_topic:          Optional[str]     = None
    off_topic_time_percent: Optional[int]     = None


class SentimentMoment(_Base):
    type:        str
    description: Optional[str] = None
    quote:       Optional[str] = None


class SentimentAnalysisResult(_Base):
    overall_sentiment:       str                    = "neutral"
    overall_score:           float                  = 0.0
    sentiment_progression:   str                    = "stable"
    per_speaker_sentiment:   Dict[str, Any]         = Field(default_factory=dict)
    highlighted_moments:     List[SentimentMoment]  = []
    meeting_health_score:    Optional[int]          = None


# ============================================
# GENERIC AI RESPONSE WRAPPER
# ============================================

class AIAnalysisResponse(_Base):
    """Generic wrapper returned by POST /ai/analyze."""
    meeting_id:        UUID
    feature_type:      str
    status:            str
    model:             str
    prompt_version:    str
    was_cached:        bool
    latency_ms:        int
    total_tokens:      int
    total_cost_usd:    float
    result:            Any             # typed by feature at the service layer
    error:             Optional[str]   = None


class BulkAIAnalysisResponse(_Base):
    """Wrapper for bulk feature runs."""
    meeting_id: UUID
    results:    Dict[str, AIAnalysisResponse]


# ============================================
# TEMPLATE INFO SCHEMA
# ============================================

class TemplateInfo(_Base):
    key:         str
    versions:    List[str]
    latest:      str
    description: str
    max_tokens:  int
    json_mode:   bool
