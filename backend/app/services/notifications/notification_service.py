"""
Notification Service
Vocaply Platform - Day 26: Notifications & Reminders

Core orchestrator: creates DB records + dispatches across channels (in-app,
email, Slack). All channel sends degrade gracefully when credentials are absent.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.notification import NotificationChannel, NotificationType
from app.repositories.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)


# ============================================
# MAIN ORCHESTRATOR
# ============================================

class NotificationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db   = db
        self.repo = NotificationRepository(db)

    # ──────────────────────────────────────────
    # PRIMARY SEND
    # ──────────────────────────────────────────

    async def send_notification(
        self,
        user_id:    str,
        company_id: str,
        type_:      str,
        title:      str,
        body:       Optional[str]         = None,
        metadata:   Optional[Dict]        = None,
        channels:   Optional[List[str]]   = None,
        # Optional direct fields for email
        user_email: Optional[str]         = None,
        user_name:  Optional[str]         = None,
    ) -> Optional[Any]:
        """
        Create an in-app notification record and dispatch enabled channels.
        Returns the notification ORM instance (or None on error).
        """
        if channels is None:
            channels = [NotificationChannel.IN_APP]

        sent_channels: List[str] = []

        # 1. Persist in-app record
        if NotificationChannel.IN_APP in channels:
            try:
                notification = await self.repo.create(
                    {
                        "user_id":       user_id,
                        "company_id":    company_id,
                        "type":          type_,
                        "title":         title,
                        "body":          body,
                        "metadata_":     metadata or {},
                        "sent_channels": [],
                        "sent_at":       datetime.now(timezone.utc),
                    }
                )
                sent_channels.append(NotificationChannel.IN_APP)
            except Exception as exc:
                logger.error("Failed to persist notification: %s", exc)
                notification = None
        else:
            notification = None

        # 2. Email
        if NotificationChannel.EMAIL in channels and user_email:
            try:
                await self._send_email_notification(
                    type_=type_,
                    title=title,
                    body=body or "",
                    to_email=user_email,
                    user_name=user_name or "there",
                    metadata=metadata or {},
                )
                sent_channels.append(NotificationChannel.EMAIL)
            except Exception as exc:
                logger.warning("Email send failed (non-fatal): %s", exc)

        # 3. Slack
        if NotificationChannel.SLACK in channels:
            try:
                await self._send_slack_notification(title=title, body=body or "")
                sent_channels.append(NotificationChannel.SLACK)
            except Exception as exc:
                logger.warning("Slack send failed (non-fatal): %s", exc)

        # Update sent_channels on the record
        if notification and sent_channels:
            notification.sent_channels = sent_channels
            await self.db.commit()

        return notification

    # ──────────────────────────────────────────
    # CONVENIENCE WRAPPERS
    # ──────────────────────────────────────────

    async def send_action_item_assigned(
        self,
        action_item_id:   str,
        action_item_title: str,
        meeting_title:    str,
        due_date:         Optional[datetime],
        assignee_user_id: str,
        assignee_email:   str,
        assignee_name:    str,
        company_id:       str,
    ) -> None:
        due_str = due_date.strftime("%b %d, %Y") if due_date else "No due date"
        await self.send_notification(
            user_id    = assignee_user_id,
            company_id = company_id,
            type_      = NotificationType.ACTION_ITEM_ASSIGNED,
            title      = f"Action item assigned: {action_item_title}",
            body       = f'From meeting "{meeting_title}". Due: {due_str}.',
            metadata   = {
                "action_item_id": action_item_id,
                "meeting_title":  meeting_title,
                "due_date":       due_str,
                "url":            f"{settings.FRONTEND_URL}/action-items",
            },
            channels    = [NotificationChannel.IN_APP, NotificationChannel.EMAIL],
            user_email  = assignee_email,
            user_name   = assignee_name,
        )

    async def send_reminder(
        self,
        action_item_id:    str,
        action_item_title: str,
        due_date:          datetime,
        user_id:           str,
        user_email:        str,
        user_name:         str,
        company_id:        str,
    ) -> None:
        due_str = due_date.strftime("%b %d, %Y")
        await self.send_notification(
            user_id    = user_id,
            company_id = company_id,
            type_      = NotificationType.REMINDER,
            title      = f"Reminder: '{action_item_title}' is due tomorrow",
            body       = f"Complete this action item by {due_str}.",
            metadata   = {
                "action_item_id": action_item_id,
                "due_date":       due_str,
                "url":            f"{settings.FRONTEND_URL}/action-items",
            },
            channels   = [NotificationChannel.IN_APP, NotificationChannel.EMAIL],
            user_email = user_email,
            user_name  = user_name,
        )

    async def send_overdue(
        self,
        action_item_id:    str,
        action_item_title: str,
        due_date:          datetime,
        user_id:           str,
        user_email:        str,
        user_name:         str,
        company_id:        str,
    ) -> None:
        due_str = due_date.strftime("%b %d, %Y")
        await self.send_notification(
            user_id    = user_id,
            company_id = company_id,
            type_      = NotificationType.OVERDUE,
            title      = f"Overdue: '{action_item_title}'",
            body       = f"This action item was due on {due_str} and is now overdue.",
            metadata   = {
                "action_item_id": action_item_id,
                "due_date":       due_str,
                "url":            f"{settings.FRONTEND_URL}/action-items",
            },
            channels   = [NotificationChannel.IN_APP, NotificationChannel.EMAIL],
            user_email = user_email,
            user_name  = user_name,
        )

    # ──────────────────────────────────────────
    # PRIVATE CHANNEL HELPERS
    # ──────────────────────────────────────────

    async def _send_email_notification(
        self,
        type_:     str,
        title:     str,
        body:      str,
        to_email:  str,
        user_name: str,
        metadata:  Dict,
    ) -> None:
        from app.services.notifications.email_sender import EmailSender
        sender = EmailSender()

        template_map = {
            NotificationType.ACTION_ITEM_ASSIGNED: "action_item_assigned.html",
            NotificationType.REMINDER:             "reminder.html",
            NotificationType.OVERDUE:              "reminder.html",
            NotificationType.DAILY_DIGEST:         "daily_digest.html",
        }
        template = template_map.get(type_, "reminder.html")

        html = sender.render_template(
            template,
            {
                "user_name":  user_name,
                "title":      title,
                "body":       body,
                "metadata":   metadata,
                "frontend_url": settings.FRONTEND_URL,
            },
        )
        await sender.send_email(
            to_email = to_email,
            subject  = title,
            html     = html,
        )

    async def _send_slack_notification(self, title: str, body: str) -> None:
        """Stub: send Slack message when SLACK_BOT_TOKEN is configured."""
        if not getattr(settings, "SLACK_BOT_TOKEN", None):
            logger.debug("Slack not configured — skipping Slack notification.")
            return
        # Future: use slack_sdk to post to a channel
        logger.info("Slack notification: %s — %s", title, body)
