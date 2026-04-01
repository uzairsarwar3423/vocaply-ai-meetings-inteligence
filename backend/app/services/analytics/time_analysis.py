"""
Time Analysis Service
Vocaply Platform - Day 27

Generates time-series trend data and meeting activity heatmap data.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.meeting import Meeting, MeetingStatus
from app.models.action_item import ActionItem, ActionItemStatus


_DAYS_OF_WEEK = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


class TimeAnalysisService:
    """Builds heatmap and trend data from meetings and action_items tables."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_meeting_heatmap(
        self,
        company_id: str,
        days: int = 90,
    ) -> dict:
        """
        Return meeting activity heatmap: count of meetings by day-of-week and hour.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        rows_q = await self.db.execute(
            select(
                extract("dow",  Meeting.scheduled_start).label("day_of_week"),  # 0=Sun
                extract("hour", Meeting.scheduled_start).label("hour"),
                func.count(Meeting.id).label("count"),
            )
            .where(
                and_(
                    Meeting.company_id == company_id,
                    Meeting.scheduled_start >= since,
                    Meeting.deleted_at == None,  # noqa: E711
                    Meeting.scheduled_start != None,  # noqa: E711
                )
            )
            .group_by("day_of_week", "hour")
            .order_by("day_of_week", "hour")
        )
        rows = rows_q.fetchall()

        # Build a 7×24 grid initialised to 0
        grid: dict[str, dict[int, int]] = {
            day: {h: 0 for h in range(24)} for day in _DAYS_OF_WEEK
        }
        max_count = 0
        for row in rows:
            dow_idx = int(row.day_of_week)
            hour    = int(row.hour)
            count   = int(row.count)
            day_label = _DAYS_OF_WEEK[dow_idx]
            grid[day_label][hour] = count
            if count > max_count:
                max_count = count

        # Flatten for recharts-friendly format
        heatmap_data = []
        for day in _DAYS_OF_WEEK:
            for hour in range(24):
                heatmap_data.append(
                    {
                        "day": day,
                        "hour": hour,
                        "count": grid[day][hour],
                    }
                )

        return {
            "heatmap": heatmap_data,
            "max_count": max_count,
            "days_of_week": _DAYS_OF_WEEK,
        }

    async def get_action_item_trends(
        self,
        company_id: str,
        days: int = 30,
        granularity: str = "daily",  # daily | weekly | monthly
    ) -> list[dict]:
        """
        Return daily/weekly/monthly counts of action items created vs completed.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        if granularity == "weekly":
            trunc = "week"
        elif granularity == "monthly":
            trunc = "month"
        else:
            trunc = "day"

        rows_q = await self.db.execute(
            select(
                func.date_trunc(trunc, ActionItem.created_at).label("period"),
                func.count(ActionItem.id).label("created"),
                func.sum(
                    func.cast(
                        ActionItem.status == ActionItemStatus.COMPLETED.value,
                        func.Integer() if False else None,  # we use case below
                    )
                ).label("_unused"),  # placeholder — overwritten below
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
        # The above query won't work well for the completed sum; redo with case
        from sqlalchemy import case as sa_case

        rows_q = await self.db.execute(
            select(
                func.date_trunc(trunc, ActionItem.created_at).label("period"),
                func.count(ActionItem.id).label("created"),
                func.sum(
                    sa_case(
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
        rows = rows_q.fetchall()
        result = []
        for row in rows:
            period_dt: datetime = row.period
            created   = int(row.created)
            completed = int(row.completed)
            label = (
                period_dt.strftime("%b %d")
                if trunc in ("day", "week")
                else period_dt.strftime("%b %Y")
            )
            result.append(
                {
                    "date": label,
                    "created": created,
                    "completed": completed,
                }
            )
        return result

    async def get_meeting_efficiency(
        self,
        company_id: str,
        days: int = 30,
    ) -> list[dict]:
        """
        Return meetings per day with their action_items_count (efficiency metric).
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        rows_q = await self.db.execute(
            select(
                func.date_trunc("day", Meeting.created_at).label("period"),
                func.count(Meeting.id).label("meetings"),
                func.sum(Meeting.action_items_count).label("action_items"),
            )
            .where(
                and_(
                    Meeting.company_id == company_id,
                    Meeting.created_at >= since,
                    Meeting.deleted_at == None,  # noqa: E711
                )
            )
            .group_by("period")
            .order_by("period")
        )
        rows = rows_q.fetchall()
        result = []
        for row in rows:
            period_dt: datetime  = row.period
            meetings     = int(row.meetings)
            action_items = int(row.action_items or 0)
            efficiency   = round(action_items / meetings, 1) if meetings > 0 else 0.0
            result.append(
                {
                    "date": period_dt.strftime("%b %d"),
                    "meetings": meetings,
                    "action_items": action_items,
                    "items_per_meeting": efficiency,
                }
            )
        return result
