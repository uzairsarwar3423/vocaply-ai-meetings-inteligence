"""
AI Analysis Worker
Vocaply Platform - Day 10: Action Item Extraction Logic
File: backend/app/workers/ai_analysis_worker.py

Celery tasks that run AI extraction + analysis features in the background.

Task hierarchy:
  analyze_meeting_task
      └─ ActionItemExtractor.extract()          (always)
      └─ MeetingSummaryService.generate()        (if requested)
      └─ KeyDecisionsService.generate()          (if requested)

Webhook notifications are fired on completion.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app

logger = get_task_logger(__name__)


# ============================================
# MAIN ANALYSIS TASK
# ============================================

@celery_app.task(
    bind=True,
    name="app.workers.ai_analysis_worker.analyze_meeting_task",
    max_retries=2,
    default_retry_delay=120,   # 2 minutes between retries
    acks_late=True,
    track_started=True,
)
def analyze_meeting_task(
    self,
    meeting_id:          str,
    company_id:          str,
    user_id:             str | None,
    features:            List[str] | None = None,
    force_rerun:         bool = False,
    chunk_size_words:    int  = 3000,
    min_confidence:      float = 0.4,
) -> Dict[str, Any]:
    """
    Background task: run AI extraction on a completed/transcribed meeting.

    Flow:
      1. Load meeting from DB
      2. Guard: skip if already analyzed (unless force_rerun)
      3. Update meeting AI status → processing
      4. Run ActionItemExtractor
      5. (Optionally) run summary / key-decisions workflows
      6. Update meeting AI status → completed | failed
      7. Fire webhook notification

    Args:
        meeting_id:       UUID string of the meeting.
        company_id:       Company UUID string (for multi-tenant filtering).
        user_id:          Who triggered the analysis (for usage tracking).
        features:         Which features to run. Defaults to ['action_items'].
        force_rerun:      Ignore existing completed status.
        chunk_size_words: Words per transcript chunk.
        min_confidence:   Minimum confidence threshold.

    Returns:
        Dict with extraction summary statistics.
    """
    features = features or ["action_items"]

    logger.info(
        f"[AIWorker] Starting analysis for meeting={meeting_id} "
        f"features={features} force_rerun={force_rerun}"
    )

    try:
        result = asyncio.run(
            _run_analysis(
                meeting_id       = uuid.UUID(meeting_id),
                company_id       = company_id,
                user_id          = user_id,
                features         = features,
                force_rerun      = force_rerun,
                chunk_size_words = chunk_size_words,
                min_confidence   = min_confidence,
            )
        )
        logger.info(f"[AIWorker] Analysis complete for meeting={meeting_id}: {result}")
        return result

    except Exception as exc:
        logger.error(
            f"[AIWorker] Analysis failed for meeting={meeting_id}: {exc}",
            exc_info=True,
        )

        # Mark meeting as failed
        try:
            asyncio.run(
                _update_ai_status(
                    meeting_id = uuid.UUID(meeting_id),
                    status     = "failed",
                    error      = str(exc),
                )
            )
        except Exception:
            pass

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)

        return {
            "success":    False,
            "meeting_id": meeting_id,
            "error":      str(exc),
        }


# ============================================
# ASYNC PROCESSING LOGIC
# ============================================

async def _run_analysis(
    meeting_id:       uuid.UUID,
    company_id:       str,
    user_id:          str | None,
    features:         List[str],
    force_rerun:      bool,
    chunk_size_words: int,
    min_confidence:   float,
) -> Dict[str, Any]:
    """Core async analysis logic executed inside asyncio.run()."""
    from app.db.session import AsyncSessionLocal
    from app.repositories.meeting_repository import MeetingRepository
    from app.schemas.extraction import AnalyzeMeetingRequest
    from app.services.ai.action_item_extractor import ActionItemExtractor

    async with AsyncSessionLocal() as db:
        meeting_repo = MeetingRepository(db)

        # Load meeting
        meeting = await meeting_repo.get_by_id(
            meeting_id = meeting_id,
            company_id = uuid.UUID(company_id) if company_id else meeting_id,
        )
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        # Guard: already completed?
        if (
            meeting.ai_analysis_status == "completed"
            and not force_rerun
        ):
            logger.info(
                f"[AIWorker] Meeting {meeting_id} already analyzed. "
                "Skipping (use force_rerun=True to override)."
            )
            return {
                "success":    True,
                "meeting_id": str(meeting_id),
                "skipped":    True,
                "reason":     "already_analyzed",
            }

        # Mark as processing
        meeting.ai_analysis_status = "processing"
        await db.commit()

        extraction_result = None
        errors: List[str] = []

        # ── Action Items ────────────────────────────────
        if "action_items" in features:
            extractor = ActionItemExtractor(db)
            request   = AnalyzeMeetingRequest(
                features         = features,
                force_rerun      = force_rerun,
                chunk_size_words = chunk_size_words,
                min_confidence   = min_confidence,
            )
            extraction_result = await extractor.extract(
                meeting = meeting,
                request = request,
                user_id = user_id,
            )
            if extraction_result.status == "failed":
                errors.append(f"action_items: {extraction_result.error}")

        # ── Meeting Summary ──────────────────────────────
        # (Placeholder — summary service lives in Day 11)
        if "summary" in features:
            logger.info(f"[AIWorker] Summary feature requested but not yet implemented for {meeting_id}")

        # ── Key Decisions ────────────────────────────────
        if "key_decisions" in features:
            logger.info(f"[AIWorker] Key decisions feature requested but not yet implemented for {meeting_id}")

        # Final status
        final_status = "failed" if errors and not extraction_result else "completed"
        if extraction_result and extraction_result.status == "completed":
            final_status = "completed"

        meeting.ai_analysis_status        = final_status
        meeting.ai_analysis_completed_at  = datetime.now(tz=timezone.utc)
        await db.commit()

        # Fire webhook (non-blocking best-effort)
        await _fire_webhook(
            meeting_id = meeting_id,
            status     = final_status,
            summary    = extraction_result,
        )

        return {
            "success":              final_status == "completed",
            "meeting_id":           str(meeting_id),
            "features":             features,
            "action_items_saved":   getattr(extraction_result, "action_items_extracted", 0),
            "duplicates_skipped":   getattr(extraction_result, "duplicates_skipped", 0),
            "matched_to_users":     getattr(extraction_result, "matched_to_users", 0),
            "errors":               errors,
        }


async def _update_ai_status(
    meeting_id: uuid.UUID,
    status:     str,
    error:      str | None = None,
) -> None:
    """Update meeting AI analysis status in the database."""
    try:
        from app.db.session import AsyncSessionLocal
        from app.repositories.meeting_repository import MeetingRepository

        async with AsyncSessionLocal() as db:
            meeting_repo = MeetingRepository(db)
            # Note: MeetingRepository.get_by_id requires company_id — do a raw lookup
            from sqlalchemy import select
            from app.models.meeting import Meeting

            stmt = select(Meeting).where(Meeting.id == meeting_id)
            result = await db.execute(stmt)
            meeting = result.scalar_one_or_none()

            if meeting:
                meeting.ai_analysis_status = status
                meeting.ai_analysis_completed_at = datetime.now(tz=timezone.utc)
                await db.commit()
    except Exception as exc:
        logger.error(f"[AIWorker] Failed to update AI status: {exc}")


async def _fire_webhook(
    meeting_id: uuid.UUID,
    status:     str,
    summary:    Any,
) -> None:
    """
    Fire webhook notification on analysis completion.
    Best-effort — failures are logged but do not affect the task result.

    In production, replace this stub with an HTTP call to your
    webhook endpoints (e.g. via httpx or a notifications service).
    """
    try:
        logger.info(
            f"[AIWorker] Webhook: meeting={meeting_id} status={status} "
            f"items={getattr(summary, 'action_items_extracted', 0)}"
        )
        # TODO: implement actual webhook dispatch
        # async with httpx.AsyncClient() as client:
        #     await client.post(webhook_url, json=payload)
    except Exception as exc:
        logger.warning(f"[AIWorker] Webhook notification failed (non-critical): {exc}")


# ============================================
# MAINTENANCE / RETRY TASKS
# ============================================

@celery_app.task(name="app.workers.ai_analysis_worker.retry_stuck_analyses")
def retry_stuck_analyses() -> Dict[str, Any]:
    """
    Periodic task: retry meetings stuck in 'processing' AI status for > 30 min.
    Scheduled via celery beat.
    """
    return asyncio.run(_retry_stuck_analyses_async())


async def _retry_stuck_analyses_async() -> Dict[str, Any]:
    from datetime import timedelta

    from sqlalchemy import and_, select

    from app.db.session import AsyncSessionLocal
    from app.models.meeting import Meeting

    async with AsyncSessionLocal() as db:
        cutoff = datetime.now(tz=timezone.utc) - timedelta(minutes=30)
        stmt = select(Meeting).where(
            and_(
                Meeting.ai_analysis_status == "processing",
                Meeting.updated_at < cutoff,
            )
        )
        result = await db.execute(stmt)
        stuck  = result.scalars().all()

        logger.info(f"[AIWorker] Found {len(stuck)} stuck analyses")
        retried = []

        for meeting in stuck:
            meeting.ai_analysis_status = "failed"
            retried.append(str(meeting.id))
            # Re-queue
            analyze_meeting_task.delay(
                meeting_id = str(meeting.id),
                company_id = str(meeting.company_id),
                user_id    = None,
            )

        await db.commit()
        return {"retried": retried, "count": len(retried)}
