"""
Email Sender
Vocaply Platform - Day 26: Notifications & Reminders

Sends HTML emails via SendGrid. Falls back gracefully when API key is absent.
Uses Jinja2 to render templates from the templates/ directory.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"


class EmailSender:

    def __init__(self) -> None:
        from app.core.config import settings
        self.api_key    = getattr(settings, "SENDGRID_API_KEY", None)
        self.from_email = getattr(settings, "SENDGRID_FROM_EMAIL", "noreply@vocaply.ai")

    # ──────────────────────────────────────────
    # RENDER
    # ──────────────────────────────────────────

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a Jinja2 HTML template from the templates/ directory."""
        try:
            from jinja2 import Environment, FileSystemLoader, select_autoescape
            env = Environment(
                loader        = FileSystemLoader(str(TEMPLATES_DIR)),
                autoescape    = select_autoescape(["html"]),
            )
            template = env.get_template(template_name)
            return template.render(**context)
        except Exception as exc:
            logger.warning("Template render failed (%s): %s — falling back to plain text", template_name, exc)
            return f"<p><strong>{context.get('title', '')}</strong></p><p>{context.get('body', '')}</p>"

    # ──────────────────────────────────────────
    # SEND
    # ──────────────────────────────────────────

    async def send_email(
        self,
        to_email: str,
        subject:  str,
        html:     str,
        text:     Optional[str] = None,
    ) -> bool:
        """
        Send an HTML email via SendGrid.
        Returns True on success, False (non-raising) when not configured.
        """
        if not self.api_key:
            logger.warning(
                "SENDGRID_API_KEY not configured — email not sent to %s: %s",
                to_email, subject,
            )
            return False

        try:
            import sendgrid as sg_module
            from sendgrid.helpers.mail import Mail, Content, To, From

            sg = sg_module.SendGridAPIClient(api_key=self.api_key)

            mail = Mail(
                from_email      = From(self.from_email, "Vocaply AI"),
                to_emails       = To(to_email),
                subject         = subject,
                html_content    = Content("text/html", html),
            )
            if text:
                mail.content = [Content("text/plain", text), Content("text/html", html)]

            response = sg.client.mail.send.post(request_body=mail.get())
            logger.info(
                "Email sent to %s (subject=%r) — status %s",
                to_email, subject, response.status_code,
            )
            return True

        except ImportError:
            logger.warning("sendgrid package not installed — email not sent.")
            return False
        except Exception as exc:
            logger.error("SendGrid error sending to %s: %s", to_email, exc)
            raise
