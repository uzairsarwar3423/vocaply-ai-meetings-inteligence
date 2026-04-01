"""
Reminder Worker
Vocaply Platform - Day 26: Notifications & Reminders

Celery tasks for:
  - send_reminders_task  → 9 AM daily: action items due tomorrow
  - mark_overdue_task    → midnight:   flag + notify overdue items
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from celery import shared_task

logger = logging.getLogger(__name__)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ─────────────────────────────────────────────
# TASK 1: Send reminders (9 AM daily)
# ─────────────────────────────────────────────

@shared_task(
    name="app.workers.reminder_worker.send_reminders_task",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
)
def send_reminders_task(self) -> Dict[str, Any]:
    """
    Find action items whose due_date is tomorrow and whose status is
    pending or in_progress. Send a reminder notification to the assignee.
    """
    from sqlalchemy import select, and_
    from app.db.session import AsyncSessionLocal
    from app.models.action_item import ActionItem, ActionItemStatus
    from app.models.user import User
    from app.services.notifications.notification_service import NotificationService

    async def _run_task():
        now            = datetime.now(timezone.utc)
        tomorrow_start = (now + timedelta(days=1)).replace(hour=0,  minute=0,  second=0, microsecond=0)
        tomorrow_end   = (now + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)

        sent_count = 0
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ActionItem).where(
                    and_(
                        ActionItem.due_date >= tomorrow_start,
                        ActionItem.due_date <= tomorrow_end,
                        ActionItem.status.in_([
                            ActionItemStatus.PENDING.value,
                            ActionItemStatus.IN_PROGRESS.value,
                        ]),
                        ActionItem.assigned_to_id != None,  # noqa: E711
                    )
                )
            )
            items = result.scalars().all()

            svc = NotificationService(db)
            for item in items:
                user_r = await db.execute(
                    select(User).where(User.id == item.assigned_to_id)
                )
                user = user_r.scalar_one_or_none()
                if not user:
                    continue

                prefs = user.notification_settings or {}
                if not prefs.get("meeting_reminders", True):
                    continue

                await svc.send_reminder(
                    action_item_id    = str(item.id),
                    action_item_title = item.title,
                    due_date          = item.due_date,
                    user_id           = str(user.id),
                    user_email        = user.email,
                    user_name         = user.full_name or user.email,
                    company_id        = str(item.company_id),
                )
                sent_count += 1

        logger.info("Sent %d reminders for items due tomorrow.", sent_count)
        return {"status": "done", "reminders_sent": sent_count}

    try:
        return _run(_run_task())
    except Exception as exc:
        logger.error("send_reminders_task failed: %s", exc)
        raise self.retry(exc=exc)


# ─────────────────────────────────────────────
# TASK 2: Mark overdue (midnight)
# ─────────────────────────────────────────────

@shared_task(
    name="app.workers.reminder_worker.mark_overdue_task",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
)
def mark_overdue_task(self) -> Dict[str, Any]:
    """
    Find action items past their due_date that are still pending/in-progress.
    Send overdue notifications to assignees.
    """
    from sqlalchemy import select, and_
    from app.db.session import AsyncSessionLocal
    from app.models.action_item import ActionItem, ActionItemStatus
    from app.models.user import User
    from app.services.notifications.notification_service import NotificationService

    async def _run_task():
        now = datetime.now(timezone.utc)
        overdue_count = 0

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ActionItem).where(
                    and_(
                        ActionItem.due_date < now,
                        ActionItem.status.in_([
                            ActionItemStatus.PENDING.value,
                            ActionItemStatus.IN_PROGRESS.value,
                        ]),
                        ActionItem.assigned_to_id != None,  # noqa: E711
                    )
                )
            )
            items = result.scalars().all()

            svc = NotificationService(db)
            for item in items:
                user_r = await db.execute(
                    select(User).where(User.id == item.assigned_to_id)
                )
                user = user_r.scalar_one_or_none()
                if not user:
                    continue

                prefs = user.notification_settings or {}
                if not prefs.get("email_alerts", True):
                    continue

                await svc.send_overdue(
                    action_item_id    = str(item.id),
                    action_item_title = item.title,
                    due_date          = item.due_date,
                    user_id           = str(user.id),
                    user_email        = user.email,
                    user_name         = user.full_name or user.email,
                    company_id        = str(item.company_id),
                )
                overdue_count += 1

        logger.info("Processed %d overdue items.", overdue_count)
        return {"status": "done", "overdue_notified": overdue_count}

    try:
        return _run(_run_task())
    except Exception as exc:
        logger.error("mark_overdue_task failed: %s", exc)
        raise self.retry(exc=exc)
