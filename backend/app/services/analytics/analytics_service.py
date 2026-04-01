"""
Analytics Service (Orchestrator)
Vocaply Platform - Day 27

High-level entry point consumed by the API layer. Delegates to specialised sub-services.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.meeting import Meeting
from app.services.analytics.completion_metrics import CompletionMetricsService
from app.services.analytics.team_insights import TeamInsightsService
from app.services.analytics.time_analysis import TimeAnalysisService


class AnalyticsService:
    """Facade over all analytics sub-services."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._completion = CompletionMetricsService(db)
        self._team       = TeamInsightsService(db)
        self._time       = TimeAnalysisService(db)

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------

    async def get_overview(self, company_id: str, days: int = 30) -> dict:
        """
        Returns aggregated KPIs:
          - action item metrics
          - total meetings in the period
          - meeting efficiency (avg action items per meeting)
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        # Completion KPIs
        completion = await self._completion.get_metrics(company_id, days)

        # Total meetings
        m_q = await self.db.execute(
            select(
                func.count(Meeting.id).label("total"),
                func.avg(Meeting.action_items_count).label("avg_items"),
            ).where(
                and_(
                    Meeting.company_id == company_id,
                    Meeting.created_at >= since,
                    Meeting.deleted_at == None,  # noqa: E711
                )
            )
        )
        m_row = m_q.fetchone()
        total_meetings  = int(m_row.total) if m_row else 0
        avg_items_per_m = round(float(m_row.avg_items or 0), 1) if m_row else 0.0

        return {
            **completion,
            "total_meetings": total_meetings,
            "avg_items_per_meeting": avg_items_per_m,
            "period_days": days,
        }

    # ------------------------------------------------------------------
    # Completion rate trend
    # ------------------------------------------------------------------

    async def get_completion_rate(
        self,
        company_id: str,
        days: int = 30,
        granularity: str = "daily",
    ) -> dict:
        trend = await self._completion.get_completion_rate_over_time(
            company_id, days, granularity
        )
        return {"trend": trend, "granularity": granularity, "period_days": days}

    # ------------------------------------------------------------------
    # Team performance
    # ------------------------------------------------------------------

    async def get_team_performance(self, company_id: str, days: int = 30) -> dict:
        team = await self._team.get_team_performance(company_id, days)
        return {"team": team, "period_days": days}

    # ------------------------------------------------------------------
    # Time trends
    # ------------------------------------------------------------------

    async def get_time_trends(
        self,
        company_id: str,
        days: int = 30,
        granularity: str = "daily",
    ) -> dict:
        heatmap    = await self._time.get_meeting_heatmap(company_id, days)
        ai_trends  = await self._time.get_action_item_trends(company_id, days, granularity)
        efficiency = await self._time.get_meeting_efficiency(company_id, days)
        return {
            **heatmap,
            "action_item_trends": ai_trends,
            "meeting_efficiency": efficiency,
            "granularity": granularity,
            "period_days": days,
        }

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    async def export_data(self, company_id: str, days: int = 30) -> dict:
        """Return all analytics data as a single dict for download."""
        overview    = await self.get_overview(company_id, days)
        completion  = await self.get_completion_rate(company_id, days)
        team        = await self.get_team_performance(company_id, days)
        time_trends = await self.get_time_trends(company_id, days)

        return {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "company_id": company_id,
            "period_days": days,
            "overview": overview,
            "completion_rate_trend": completion,
            "team_performance": team,
            "time_trends": time_trends,
        }
