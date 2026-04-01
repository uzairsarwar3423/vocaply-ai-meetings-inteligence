"""
Completion Metrics
Vocaply Platform - Day 27

Calculates action item completion rates, overdue counts, and status distributions
for a given company over a specified time window.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.action_item import ActionItem, ActionItemStatus


class CompletionMetricsService:
    """Calculates completion-related KPIs from the action_items table."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_metrics(
        self,
        company_id: str,
        days: int = 30,
    ) -> dict:
        """
        Return overview KPIs for the given company over the last `days` days.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)
        now = datetime.now(timezone.utc)

        # Total action items in the window
        total_q = await self.db.execute(
            select(func.count(ActionItem.id)).where(
                and_(
                    ActionItem.company_id == company_id,
                    ActionItem.created_at >= since,
                )
            )
        )
        total = total_q.scalar_one_or_none() or 0

        # Status breakdown
        status_q = await self.db.execute(
            select(ActionItem.status, func.count(ActionItem.id))
            .where(
                and_(
                    ActionItem.company_id == company_id,
                    ActionItem.created_at >= since,
                )
            )
            .group_by(ActionItem.status)
        )
        status_counts: dict[str, int] = {row[0]: row[1] for row in status_q.fetchall()}

        completed = status_counts.get(ActionItemStatus.COMPLETED.value, 0)
        pending    = status_counts.get(ActionItemStatus.PENDING.value, 0)
        in_progress = status_counts.get(ActionItemStatus.IN_PROGRESS.value, 0)
        cancelled  = status_counts.get(ActionItemStatus.CANCELLED.value, 0)

        completion_rate = round((completed / total * 100), 1) if total > 0 else 0.0

        # Overdue: not completed and past due_date
        overdue_q = await self.db.execute(
            select(func.count(ActionItem.id)).where(
                and_(
                    ActionItem.company_id == company_id,
                    ActionItem.created_at >= since,
                    ActionItem.status != ActionItemStatus.COMPLETED.value,
                    ActionItem.status != ActionItemStatus.CANCELLED.value,
                    ActionItem.due_date != None,  # noqa: E711
                    ActionItem.due_date < now,
                )
            )
        )
        overdue = overdue_q.scalar_one_or_none() or 0

        # Average time to complete (hours) — only completed items with both timestamps
        avg_time_q = await self.db.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        ActionItem.completed_at - ActionItem.created_at
                    )
                )
            ).where(
                and_(
                    ActionItem.company_id == company_id,
                    ActionItem.created_at >= since,
                    ActionItem.status == ActionItemStatus.COMPLETED.value,
                    ActionItem.completed_at != None,  # noqa: E711
                )
            )
        )
        avg_secs = avg_time_q.scalar_one_or_none() or 0
        avg_hours = round(avg_secs / 3600, 1) if avg_secs else 0.0

        return {
            "total_created": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "cancelled": cancelled,
            "overdue": overdue,
            "completion_rate": completion_rate,
            "avg_completion_hours": avg_hours,
            "period_days": days,
            "status_distribution": [
                {"status": "Completed",   "count": completed,   "color": "#10b981"},
                {"status": "In Progress", "count": in_progress, "color": "#3b82f6"},
                {"status": "Pending",     "count": pending,     "color": "#f59e0b"},
                {"status": "Cancelled",   "count": cancelled,   "color": "#6b7280"},
            ],
        }

    async def get_completion_rate_over_time(
        self,
        company_id: str,
        days: int = 30,
        granularity: str = "daily",   # daily | weekly | monthly
    ) -> list[dict]:
        """
        Return time-series data for the completion rate chart.
        Each point: date label + rate.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        if granularity == "weekly":
            trunc = "week"
        elif granularity == "monthly":
            trunc = "month"
        else:
            trunc = "day"

        total_by_period_q = await self.db.execute(
            select(
                func.date_trunc(trunc, ActionItem.created_at).label("period"),
                func.count(ActionItem.id).label("total"),
                func.sum(
                    case(
                        (ActionItem.status == ActionItemStatus.COMPLETED.value, 1),
                        else_=0,
                    )
                ).label("completed"),
            )
            .where(
                and_(
                    ActionItem.company_id == company_id,
                    ActionItem.created_at >= since,
                )
            )
            .group_by("period")
            .order_by("period")
        )

        rows = total_by_period_q.fetchall()
        result = []
        for row in rows:
            period_dt: datetime = row.period
            total = row.total or 0
            completed = row.completed or 0
            rate = round((completed / total * 100), 1) if total > 0 else 0.0
            result.append(
                {
                    "date": period_dt.strftime("%b %d") if trunc in ("day", "week") else period_dt.strftime("%b %Y"),
                    "completion_rate": rate,
                    "total": total,
                    "completed": completed,
                }
            )
        return result
