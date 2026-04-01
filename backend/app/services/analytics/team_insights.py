"""
Team Insights Service
Vocaply Platform - Day 27

Per-user productivity stats: assigned vs completed, avg completion time,
and meeting creation counts.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.action_item import ActionItem, ActionItemStatus
from app.models.meeting import Meeting
from app.models.user import User


class TeamInsightsService:
    """Calculates per-user productivity from the action_items and meetings tables."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_team_performance(
        self,
        company_id: str,
        days: int = 30,
    ) -> list[dict]:
        """
        Return a list of team members with their productivity stats.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        # Action-item stats per user (only items assigned to a registered user)
        ai_q = await self.db.execute(
            select(
                ActionItem.assigned_to_id,
                func.count(ActionItem.id).label("assigned"),
                func.sum(
                    case(
                        (ActionItem.status == ActionItemStatus.COMPLETED.value, 1),
                        else_=0,
                    )
                ).label("completed"),
                func.avg(
                    case(
                        (
                            and_(
                                ActionItem.status == ActionItemStatus.COMPLETED.value,
                                ActionItem.completed_at != None,  # noqa: E711
                            ),
                            func.extract(
                                "epoch",
                                ActionItem.completed_at - ActionItem.created_at,
                            ),
                        ),
                        else_=None,
                    )
                ).label("avg_secs"),
            )
            .where(
                and_(
                    ActionItem.company_id == company_id,
                    ActionItem.created_at >= since,
                    ActionItem.assigned_to_id != None,  # noqa: E711
                )
            )
            .group_by(ActionItem.assigned_to_id)
        )
        ai_rows = {row.assigned_to_id: row for row in ai_q.fetchall()}

        # Meeting creation stats per user
        m_q = await self.db.execute(
            select(
                Meeting.created_by,
                func.count(Meeting.id).label("meetings_created"),
            )
            .where(
                and_(
                    Meeting.company_id == company_id,
                    Meeting.created_at >= since,
                    Meeting.deleted_at == None,  # noqa: E711
                )
            )
            .group_by(Meeting.created_by)
        )
        meeting_rows = {row.created_by: row.meetings_created for row in m_q.fetchall()}

        # Collect all relevant user IDs
        user_ids = set(ai_rows.keys()) | set(meeting_rows.keys())
        if not user_ids:
            return []

        # Fetch user display info
        users_q = await self.db.execute(
            select(User.id, User.full_name, User.email).where(
                User.id.in_(user_ids)
            )
        )
        users_map = {u.id: u for u in users_q.fetchall()}

        result = []
        for uid in user_ids:
            user = users_map.get(uid)
            name = user.full_name if user else "Unknown"
            email = user.email if user else ""

            ai = ai_rows.get(uid)
            assigned  = int(ai.assigned)  if ai else 0
            completed = int(ai.completed) if ai else 0
            avg_secs  = float(ai.avg_secs) if ai and ai.avg_secs else 0.0
            avg_hours = round(avg_secs / 3600, 1) if avg_secs else 0.0
            rate = round((completed / assigned * 100), 1) if assigned > 0 else 0.0

            meetings_created = meeting_rows.get(uid, 0)

            result.append(
                {
                    "user_id": uid,
                    "name": name,
                    "email": email,
                    "assigned": assigned,
                    "completed": completed,
                    "pending": assigned - completed,
                    "completion_rate": rate,
                    "avg_completion_hours": avg_hours,
                    "meetings_created": meetings_created,
                }
            )

        # Sort by completed desc
        result.sort(key=lambda x: x["completed"], reverse=True)
        return result
