"""
AI Usage Model
Vocaply Platform - Day 9: OpenAI Integration & Prompt Engineering
File: backend/app/models/ai_usage.py

Tracks token consumption and cost per company for AI features.
"""
import uuid
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Column, String, Text, Integer, BigInteger,
    Float, DateTime, ForeignKey, Index, Numeric,
    func, text, Boolean
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


# ============================================
# ENUMS
# ============================================

class AIFeatureType(str, enum.Enum):
    """Feature that triggered the AI call."""
    MEETING_SUMMARY        = "meeting_summary"
    ACTION_ITEM_EXTRACTION = "action_item_extraction"
    KEY_DECISIONS          = "key_decisions"
    PARTICIPANT_ANALYSIS   = "participant_analysis"
    TOPIC_EXTRACTION       = "topic_extraction"
    SENTIMENT_ANALYSIS     = "sentiment_analysis"
    CUSTOM                 = "custom"


class AIRequestStatus(str, enum.Enum):
    """Final status of an AI API call."""
    SUCCESS   = "success"
    FAILED    = "failed"
    CACHED    = "cached"
    RATE_LIMITED = "rate_limited"


# ============================================
# AI USAGE MODEL
# ============================================

class AIUsage(Base):
    """
    Records every AI API call made on behalf of a company.

    Indexes:
        - company_id          (tenant isolation)
        - company_id + date   (billing queries)
        - meeting_id          (per-meeting cost)
        - feature_type        (usage breakdown)
        - created_at          (time-series queries)
    """
    __tablename__ = "ai_usage"

    # ------------------------------------------
    # PRIMARY KEY
    # ------------------------------------------
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4()
    )

    # ------------------------------------------
    # FOREIGN KEYS
    # ------------------------------------------
    company_id = Column(
        String,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    meeting_id = Column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # ------------------------------------------
    # REQUEST DETAILS
    # ------------------------------------------
    feature_type    = Column(String(100), nullable=False, index=True)
    model           = Column(String(100), nullable=False, default="gpt-4o-mini")
    prompt_version  = Column(String(50),  nullable=True)
    request_id      = Column(String(255), nullable=True, unique=True)  # OpenAI request-id header
    status          = Column(String(50),  nullable=False, default=AIRequestStatus.SUCCESS.value, index=True)

    # ------------------------------------------
    # TOKEN USAGE
    # ------------------------------------------
    prompt_tokens     = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    total_tokens      = Column(Integer, nullable=False, default=0)

    # ------------------------------------------
    # COST (in USD, high precision)
    # ------------------------------------------
    prompt_cost     = Column(Numeric(12, 8), nullable=False, default=Decimal("0"))
    completion_cost = Column(Numeric(12, 8), nullable=False, default=Decimal("0"))
    total_cost      = Column(Numeric(12, 8), nullable=False, default=Decimal("0"))

    # ------------------------------------------
    # PERFORMANCE
    # ------------------------------------------
    latency_ms    = Column(Integer,  nullable=True)   # Wall-clock time in ms
    was_cached    = Column(Boolean,  nullable=False, default=False)
    retry_count   = Column(Integer,  nullable=False, default=0)

    # ------------------------------------------
    # CONTEXT / METADATA
    # ------------------------------------------
    # Store pruned prompt/response metadata (not full text, just stats)
    meta_data = Column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb")
    )
    error_message = Column(Text, nullable=True)

    # ------------------------------------------
    # DATE (for efficient date-range queries)
    # ------------------------------------------
    usage_date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        index=True
    )

    # ------------------------------------------
    # TIMESTAMPS (inherited created_at / updated_at from Base)
    # ------------------------------------------
    # Base already has created_at / updated_at

    # ------------------------------------------
    # RELATIONSHIPS
    # ------------------------------------------
    company = relationship("Company", lazy="select")
    meeting = relationship("Meeting", lazy="select")

    # ------------------------------------------
    # COMPOSITE INDEXES
    # ------------------------------------------
    __table_args__ = (
        Index("idx_ai_usage_company_date",    "company_id", "usage_date"),
        Index("idx_ai_usage_company_feature", "company_id", "feature_type"),
        Index("idx_ai_usage_meeting",         "meeting_id"),
        Index("idx_ai_usage_status",          "status"),
        {"extend_existing": True},
    )

    # ==========================================
    # HELPERS
    # ==========================================

    @classmethod
    def calculate_cost(
        cls,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "gpt-4o-mini"
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Return (prompt_cost, completion_cost, total_cost) in USD.

        Pricing as of 2024 for gpt-4o-mini:
            Input  : $0.150 / 1M tokens
            Output : $0.600 / 1M tokens
        """
        PRICING = {
            "gpt-4o-mini": {
                "input":  Decimal("0.000000150"),   # per token
                "output": Decimal("0.000000600"),   # per token
            },
            "gpt-4o": {
                "input":  Decimal("0.000005000"),
                "output": Decimal("0.000015000"),
            },
        }
        rates = PRICING.get(model, PRICING["gpt-4o-mini"])
        p_cost = Decimal(str(prompt_tokens))     * rates["input"]
        c_cost = Decimal(str(completion_tokens)) * rates["output"]
        return p_cost, c_cost, p_cost + c_cost

    def to_dict(self) -> dict:
        return {
            "id":                str(self.id),
            "company_id":        self.company_id,
            "meeting_id":        str(self.meeting_id) if self.meeting_id else None,
            "feature_type":      self.feature_type,
            "model":             self.model,
            "prompt_version":    self.prompt_version,
            "status":            self.status,
            "prompt_tokens":     self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens":      self.total_tokens,
            "prompt_cost":       float(self.prompt_cost),
            "completion_cost":   float(self.completion_cost),
            "total_cost":        float(self.total_cost),
            "latency_ms":        self.latency_ms,
            "was_cached":        self.was_cached,
            "retry_count":       self.retry_count,
            "error_message":     self.error_message,
            "usage_date":        self.usage_date.isoformat() if self.usage_date else None,
            "created_at":        self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<AIUsage id={self.id} company={self.company_id} "
            f"feature={self.feature_type} tokens={self.total_tokens} "
            f"cost=${float(self.total_cost):.6f}>"
        )
