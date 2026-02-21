"""
Summary Worker
Vocaply Platform - Day 13

Celery background task for asynchronous meeting summary generation.
"""
from __future__ import annotations

import asyncio
import uuid
from typing import Optional
from uuid import UUID

from loguru import logger

from app.workers.celery_app import celery_app


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: run async code inside a Celery sync worker
# ─────────────────────────────────────────────────────────────────────────────

def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("closed")
        return loop.run_until_complete(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


# ─────────────────────────────────────────────────────────────────────────────
# TASKS
# ─────────────────────────────────────────────────────────────────────────────

@celery_app.task(
    name        = "tasks.generate_meeting_summary",
    bind        = True,
    max_retries = 3,
    default_retry_delay = 60,
    acks_late   = True,
)
def generate_meeting_summary_task(
    self,
    meeting_id:  str,
    company_id:  str,
    title:       str,
    transcript:  str,
    participants: Optional[list] = None,
    duration_min: Optional[int] = None,
) -> dict:
    """
    Celery task: generate a meeting summary asynchronously.

    Args:
        meeting_id:   UUID string of the meeting
        company_id:   UUID string of the company
        title:        Meeting title
        transcript:   Full transcript text
        participants: List of participant names
        duration_min: Duration in minutes

    Returns:
        dict with summary_id and status
    """
    async def _run():
        from app.db.session import AsyncSessionLocal
        from app.repositories.summary_repository import SummaryRepository
        from app.services.ai.summarizer import summarizer_service

        async with AsyncSessionLocal() as db:
            repo = SummaryRepository(db)
            summary = await summarizer_service.generate_summary(
                meeting_id   = uuid.UUID(meeting_id),
                company_id   = uuid.UUID(company_id),
                title        = title,
                transcript   = transcript,
                participants = participants or [],
                duration_min = duration_min,
                repo         = repo,
            )
            return {
                "status":     "completed",
                "summary_id": str(summary.id),
                "meeting_id": meeting_id,
            }

    try:
        result = _run_async(_run())
        logger.info(f"Summary task completed: meeting={meeting_id}")
        return result
    except Exception as exc:
        logger.error(f"Summary task failed for meeting={meeting_id}: {exc}")
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            return {
                "status":     "failed",
                "meeting_id": meeting_id,
                "error":      str(exc),
            }


@celery_app.task(
    name        = "tasks.regenerate_meeting_summary",
    bind        = True,
    max_retries = 2,
    default_retry_delay = 30,
)
def regenerate_meeting_summary_task(
    self,
    meeting_id:  str,
    company_id:  str,
    title:       str,
    transcript:  str,
    participants: Optional[list] = None,
    duration_min: Optional[int] = None,
) -> dict:
    """Force-regenerate an existing summary (overwrites cached version)."""
    async def _run():
        from app.db.session import AsyncSessionLocal
        from app.repositories.summary_repository import SummaryRepository
        from app.services.ai.summarizer import summarizer_service

        async with AsyncSessionLocal() as db:
            repo = SummaryRepository(db)
            summary = await summarizer_service.regenerate_summary(
                meeting_id   = uuid.UUID(meeting_id),
                company_id   = uuid.UUID(company_id),
                title        = title,
                transcript   = transcript,
                participants = participants or [],
                duration_min = duration_min,
                repo         = repo,
            )
            return {
                "status":     "regenerated",
                "summary_id": str(summary.id),
                "meeting_id": meeting_id,
            }

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.error(f"Regeneration task failed for meeting={meeting_id}: {exc}")
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            return {"status": "failed", "meeting_id": meeting_id, "error": str(exc)}
