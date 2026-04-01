"""
Notification Worker
Vocaply Platform - Day 26: Notifications & Reminders

Celery tasks for:
  - send_notification_task        → ad-hoc notification delivery
  - send_action_item_assigned_task → triggered on action item assignment
  - send_daily_digest_task        → 8 AM daily batch (beat schedule)
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone, date
from typing import Any, Dict, List, Optional

from celery import shared_task

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# HELPER: run async from sync Celery context
# ─────────────────────────────────────────────

def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ─────────────────────────────────────────────
# TASK 1: Generic notification
# ─────────────────────────────────────────────

@shared_task(
    name="app.workers.notification_worker.send_notification_task",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_notification_task(
    self,
    user_id:    str,
    company_id: str,
    type_:      str,
    title:      str,
    body:       Optional[str]       = None,
    metadata:   Optional[Dict]      = None,
    channels:   Optional[List[str]] = None,
    user_email: Optional[str]       = None,
    user_name:  Optional[str]       = None,
) -> Dict[str, Any]:
    from app.db.session import AsyncSessionLocal
    from app.services.notifications.notification_service import NotificationService

    async def _send():
        async with AsyncSessionLocal() as db:
            svc    = NotificationService(db)
            result = await svc.send_notification(
                user_id    = user_id,
                company_id = company_id,
                type_      = type_,
                title      = title,
                body       = body,
                metadata   = metadata,
                channels   = channels,
                user_email = user_email,
                user_name  = user_name,
            )
            return {"status": "sent", "notification_id": str(result.id) if result else None}

    try:
        return _run(_send())
    except Exception as exc:
        logger.error("send_notification_task failed: %s", exc)
        raise self.retry(exc=exc)


# ─────────────────────────────────────────────
# TASK 2: Action item assigned
# ─────────────────────────────────────────────

@shared_task(
    name="app.workers.notification_worker.send_action_item_assigned_task",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_action_item_assigned_task(self, action_item_id: str) -> Dict[str, Any]:
    """
    Looks up the action item by ID, resolves the assignee, and dispatches
    an assignment notification.
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    from app.models.action_item import ActionItem
    from app.models.user import User
    from app.services.notifications.notification_service import NotificationService

    async def _send():
        async with AsyncSessionLocal() as db:
            # Fetch action item
            result = await db.execute(
                select(ActionItem).where(ActionItem.id == action_item_id)
            )
            item = result.scalar_one_or_none()
            if not item or not item.assigned_to_id:
                logger.info("No assignee for action_item %s — skipping", action_item_id)
                return {"status": "skipped", "reason": "no_assignee"}

            # Fetch assignee user
            user_r = await db.execute(
                select(User).where(User.id == item.assigned_to_id)
            )
            user = user_r.scalar_one_or_none()
            if not user:
                return {"status": "skipped", "reason": "user_not_found"}

            svc = NotificationService(db)
            await svc.send_action_item_assigned(
                action_item_id    = str(item.id),
                action_item_title = item.title,
                meeting_title     = "Meeting",  # fetched from meeting relation if eager loaded
                due_date          = item.due_date,
                assignee_user_id  = str(user.id),
                assignee_email    = user.email,
                assignee_name     = user.full_name or user.email,
                company_id        = str(item.company_id),
            )
            return {"status": "sent", "action_item_id": action_item_id}

    try:
        return _run(_send())
    except Exception as exc:
        logger.error("send_action_item_assigned_task failed: %s", exc)
        raise self.retry(exc=exc)


# ─────────────────────────────────────────────
# TASK 3: Daily digest (beat at 08:00)
# ─────────────────────────────────────────────

@shared_task(
    name="app.workers.notification_worker.send_daily_digest_task",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
)
def send_daily_digest_task(self) -> Dict[str, Any]:
    """
    For every active user with email_alerts enabled, aggregate their
    pending action items and send a daily digest email.
    """
    from sqlalchemy import select, func as sql_func
    from sqlalchemy import or_
    from app.db.session import AsyncSessionLocal
    from app.models.user import User
    from app.models.action_item import ActionItem, ActionItemStatus
    from app.services.notifications.email_sender import EmailSender
    from pathlib import Path
    from app.core.config import settings

    async def _send():
        sent_count = 0
        async with AsyncSessionLocal() as db:
            # Get all active users
            users_r = await db.execute(
                select(User).where(User.is_active == True)  # noqa: E712
            )
            users = users_r.scalars().all()

            sender = EmailSender()

            for user in users:
                prefs = user.notification_settings or {}
                if not prefs.get("email_alerts", True):
                    continue

                # Fetch user's action items
                items_r = await db.execute(
                    select(ActionItem).where(
                        ActionItem.assigned_to_id == user.id,
                        ActionItem.status.in_(["pending", "in_progress"]),
                    ).limit(20)
                )
                items = items_r.scalars().all()

                from app.models.action_item import ActionItemStatus
                from datetime import datetime, timezone as tz

                now = datetime.now(tz.utc)
                overdue = [i for i in items if i.due_date and i.due_date.replace(tzinfo=tz.utc) < now]
                pending = [i for i in items if i.status == ActionItemStatus.PENDING.value]

                stats = {
                    "total":     len(items),
                    "pending":   len(pending),
                    "overdue":   len(overdue),
                    "completed": 0,
                }

                digest_items = [
                    {
                        "title":    i.title,
                        "priority": i.priority,
                        "due_date": i.due_date.strftime("%b %d") if i.due_date else None,
                    }
                    for i in items[:10]
                ]

                from app.services.notifications.email_sender import EmailSender
                sender = EmailSender()
                html = sender.render_template(
                    "daily_digest.html",
                    {
                        "user_name":    user.full_name or user.email,
                        "date":         now.strftime("%B %d, %Y"),
                        "stats":        stats,
                        "items":        digest_items,
                        "frontend_url": settings.FRONTEND_URL,
                    },
                )
                ok = await sender.send_email(
                    to_email = user.email,
                    subject  = f"Your Daily Digest — {now.strftime('%b %d')}",
                    html     = html,
                )
                if ok:
                    sent_count += 1

        return {"status": "done", "digests_sent": sent_count}

    try:
        return _run(_send())
    except Exception as exc:
        logger.error("send_daily_digest_task failed: %s", exc)
        raise self.retry(exc=exc)
