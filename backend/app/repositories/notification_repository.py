"""
Notification Repository
Vocaply Platform - Day 26: Notifications & Reminders

All database queries for the Notification model.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ──────────────────────────────────────────
    # READ
    # ──────────────────────────────────────────

    async def get_by_id(
        self,
        notification_id: uuid.UUID,
        user_id: str,
    ) -> Optional[Notification]:
        result = await self.db.execute(
            select(Notification).where(
                Notification.id      == notification_id,
                Notification.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id:     str,
        company_id:  str,
        skip:        int  = 0,
        limit:       int  = 20,
        unread_only: bool = False,
    ) -> Tuple[List[Notification], int]:
        base_q = select(Notification).where(
            Notification.user_id    == user_id,
            Notification.company_id == company_id,
        )
        if unread_only:
            base_q = base_q.where(Notification.is_read == False)  # noqa: E712

        # total count
        count_q  = select(func.count()).select_from(base_q.subquery())
        count_r  = await self.db.execute(count_q)
        total    = count_r.scalar_one()

        # paginated rows
        rows_q   = (
            base_q
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows_r   = await self.db.execute(rows_q)
        items    = rows_r.scalars().all()

        return list(items), total

    async def get_unread_count(self, user_id: str) -> int:
        q = select(func.count()).where(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        )
        result = await self.db.execute(q)
        return result.scalar_one()

    # ──────────────────────────────────────────
    # CREATE
    # ──────────────────────────────────────────

    async def create(self, data: dict) -> Notification:
        notification = Notification(**data)
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def bulk_create(self, items: List[dict]) -> List[Notification]:
        notifications = [Notification(**item) for item in items]
        self.db.add_all(notifications)
        await self.db.commit()
        return notifications

    # ──────────────────────────────────────────
    # UPDATE
    # ──────────────────────────────────────────

    async def mark_as_read(
        self,
        notification_id: uuid.UUID,
        user_id: str,
    ) -> Optional[Notification]:
        notification = await self.get_by_id(notification_id, user_id)
        if not notification:
            return None
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(notification)
        return notification

    async def mark_all_as_read(self, user_id: str) -> int:
        """Returns the number of rows updated."""
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
            .values(is_read=True, read_at=now)
            .returning(Notification.id)
        )
        await self.db.commit()
        return len(result.all())
