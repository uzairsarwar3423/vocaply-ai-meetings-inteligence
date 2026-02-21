"""
AI Usage Repository
Vocaply Platform - Day 9: OpenAI Integration & Prompt Engineering
File: backend/app/repositories/ai_usage_repository.py

Database access layer for the ai_usage table.
Provides:
  - Single record creation
  - Company usage aggregation (daily / monthly)
  - Paginated listing with filters
  - Cost analytics helpers
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, and_, cast
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.ai_usage import AIUsage, AIFeatureType, AIRequestStatus
from app.schemas.ai import (
    AIUsageSummary,
    AIUsageCompanyStats,
)


class AIUsageRepository:
    """
    All database operations for the ai_usage table.
    Multi-tenant: every query filters on company_id.
    """

    # ==========================================
    # CREATE
    # ==========================================

    def create(
        self,
        db:                Session,
        company_id:        str,
        feature_type:      str,
        model:             str,
        prompt_version:    str,
        status:            str,
        prompt_tokens:     int,
        completion_tokens: int,
        total_tokens:      int,
        prompt_cost:       Decimal,
        completion_cost:   Decimal,
        total_cost:        Decimal,
        latency_ms:        Optional[int]  = None,
        was_cached:        bool           = False,
        retry_count:       int            = 0,
        meeting_id:        Optional[UUID] = None,
        user_id:           Optional[str]  = None,
        request_id:        Optional[str]  = None,
        error_message:     Optional[str]  = None,
        meta_data:         Optional[Dict] = None,
    ) -> AIUsage:
        """Insert a new ai_usage row and return the populated object."""
        record = AIUsage(
            company_id        = company_id,
            meeting_id        = meeting_id,
            user_id           = user_id,
            feature_type      = feature_type,
            model             = model,
            prompt_version    = prompt_version,
            request_id        = request_id,
            status            = status,
            prompt_tokens     = prompt_tokens,
            completion_tokens = completion_tokens,
            total_tokens      = total_tokens,
            prompt_cost       = prompt_cost,
            completion_cost   = completion_cost,
            total_cost        = total_cost,
            latency_ms        = latency_ms,
            was_cached        = was_cached,
            retry_count       = retry_count,
            error_message     = error_message,
            meta_data         = meta_data or {},
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    # ==========================================
    # LIST / FILTER
    # ==========================================

    def list_by_company(
        self,
        db:           Session,
        company_id:   str,
        *,
        meeting_id:   Optional[UUID]  = None,
        feature_type: Optional[str]   = None,
        status:       Optional[str]   = None,
        from_date:    Optional[date]  = None,
        to_date:      Optional[date]  = None,
        page:         int             = 1,
        page_size:    int             = 50,
    ) -> tuple[List[AIUsage], int]:
        """
        Paginated listing with optional filters.

        Returns:
            (items: list, total: int)
        """
        q = db.query(AIUsage).filter(AIUsage.company_id == company_id)

        if meeting_id:
            q = q.filter(AIUsage.meeting_id == meeting_id)
        if feature_type:
            q = q.filter(AIUsage.feature_type == feature_type)
        if status:
            q = q.filter(AIUsage.status == status)
        if from_date:
            q = q.filter(AIUsage.usage_date >= datetime.combine(from_date, datetime.min.time()))
        if to_date:
            q = q.filter(AIUsage.usage_date <= datetime.combine(to_date, datetime.max.time()))

        total = q.count()
        items = (
            q.order_by(AIUsage.usage_date.desc())
             .offset((page - 1) * page_size)
             .limit(page_size)
             .all()
        )
        return items, total

    def get_by_id(self, db: Session, usage_id: UUID, company_id: str) -> Optional[AIUsage]:
        return (
            db.query(AIUsage)
              .filter(AIUsage.id == usage_id, AIUsage.company_id == company_id)
              .first()
        )

    def list_by_meeting(self, db: Session, meeting_id: UUID, company_id: str) -> List[AIUsage]:
        return (
            db.query(AIUsage)
              .filter(AIUsage.meeting_id == meeting_id, AIUsage.company_id == company_id)
              .order_by(AIUsage.usage_date.desc())
              .all()
        )

    # ==========================================
    # AGGREGATION QUERIES
    # ==========================================

    def daily_aggregation(
        self,
        db:         Session,
        company_id: str,
        day:        date,
    ) -> AIUsageSummary:
        """Sum usage metrics for a single day."""
        start = datetime.combine(day, datetime.min.time())
        end   = datetime.combine(day, datetime.max.time())

        row = (
            db.query(
                func.count(AIUsage.id).label("total_requests"),
                func.coalesce(func.sum(AIUsage.prompt_tokens),     0).label("prompt_tokens"),
                func.coalesce(func.sum(AIUsage.completion_tokens), 0).label("completion_tokens"),
                func.coalesce(func.sum(AIUsage.total_tokens),      0).label("total_tokens"),
                func.coalesce(func.sum(AIUsage.total_cost),        0).label("total_cost"),
                func.count(
                    AIUsage.id
                ).filter(AIUsage.was_cached == True).label("cached_requests"),
            )
            .filter(
                AIUsage.company_id == company_id,
                AIUsage.usage_date.between(start, end),
            )
            .one()
        )

        feature_breakdown = self._feature_breakdown(db, company_id, start, end)

        return AIUsageSummary(
            company_id        = company_id,
            period            = day.isoformat(),
            total_requests    = row.total_requests or 0,
            cached_requests   = row.cached_requests or 0,
            prompt_tokens     = int(row.prompt_tokens or 0),
            completion_tokens = int(row.completion_tokens or 0),
            total_tokens      = int(row.total_tokens or 0),
            total_cost_usd    = float(row.total_cost or 0),
            feature_breakdown = feature_breakdown,
        )

    def monthly_aggregation(
        self,
        db:         Session,
        company_id: str,
        year:       int,
        month:      int,
    ) -> AIUsageSummary:
        """Sum usage metrics for a calendar month."""
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(seconds=1)

        row = (
            db.query(
                func.count(AIUsage.id).label("total_requests"),
                func.coalesce(func.sum(AIUsage.prompt_tokens),     0).label("prompt_tokens"),
                func.coalesce(func.sum(AIUsage.completion_tokens), 0).label("completion_tokens"),
                func.coalesce(func.sum(AIUsage.total_tokens),      0).label("total_tokens"),
                func.coalesce(func.sum(AIUsage.total_cost),        0).label("total_cost"),
                func.count(
                    AIUsage.id
                ).filter(AIUsage.was_cached == True).label("cached_requests"),
            )
            .filter(
                AIUsage.company_id == company_id,
                AIUsage.usage_date.between(start, end),
            )
            .one()
        )

        feature_breakdown = self._feature_breakdown(db, company_id, start, end)

        return AIUsageSummary(
            company_id        = company_id,
            period            = f"{year:04d}-{month:02d}",
            total_requests    = row.total_requests or 0,
            cached_requests   = row.cached_requests or 0,
            prompt_tokens     = int(row.prompt_tokens or 0),
            completion_tokens = int(row.completion_tokens or 0),
            total_tokens      = int(row.total_tokens or 0),
            total_cost_usd    = float(row.total_cost or 0),
            feature_breakdown = feature_breakdown,
        )

    def company_stats(
        self,
        db:               Session,
        company_id:       str,
        monthly_budget:   float = 50.0,
    ) -> AIUsageCompanyStats:
        """Return today + this-month stats for the dashboard."""
        today_summary = self.daily_aggregation(db, company_id, date.today())
        now           = datetime.utcnow()
        month_summary = self.monthly_aggregation(db, company_id, now.year, now.month)

        used_pct = (
            (month_summary.total_cost_usd / monthly_budget * 100)
            if monthly_budget > 0 else 0.0
        )

        return AIUsageCompanyStats(
            company_id          = company_id,
            today               = today_summary,
            this_month          = month_summary,
            monthly_budget_usd  = monthly_budget,
            budget_used_percent = min(used_pct, 100.0),
            is_over_budget      = month_summary.total_cost_usd > monthly_budget,
        )

    def total_cost_for_meeting(self, db: Session, meeting_id: UUID, company_id: str) -> float:
        """Sum all AI costs incurred for a specific meeting."""
        result = (
            db.query(func.coalesce(func.sum(AIUsage.total_cost), 0))
              .filter(
                  AIUsage.meeting_id == meeting_id,
                  AIUsage.company_id == company_id,
              )
              .scalar()
        )
        return float(result or 0)

    # ==========================================
    # PRIVATE HELPERS
    # ==========================================

    def _feature_breakdown(
        self,
        db:         Session,
        company_id: str,
        start:      datetime,
        end:        datetime,
    ) -> Dict[str, int]:
        """Return {feature_type: request_count} mapping."""
        rows = (
            db.query(AIUsage.feature_type, func.count(AIUsage.id))
              .filter(
                  AIUsage.company_id == company_id,
                  AIUsage.usage_date.between(start, end),
              )
              .group_by(AIUsage.feature_type)
              .all()
        )
        return {row[0]: row[1] for row in rows}


# ============================================
# MODULE-LEVEL SINGLETON
# ============================================

ai_usage_repo = AIUsageRepository()
