"""
Summaries API Router
Vocaply Platform - Day 13

Endpoints:
  POST /meetings/{id}/summarize         → trigger summary generation
  GET  /meetings/{id}/summary           → get existing summary
  PUT  /summaries/{id}                  → user-edit summary
  POST /summaries/{id}/regenerate       → force-regenerate summary
  GET  /summaries/{id}/export/{format}  → export as markdown/pdf/docx
"""
from __future__ import annotations

import uuid
from typing import Optional, List

from fastapi import (
    APIRouter, Depends, HTTPException, BackgroundTasks,
    Query, status
)
from fastapi.responses import PlainTextResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_async_db
from app.models.meeting_summary import MeetingSummary as MeetingSummaryModel
from app.repositories.summary_repository import SummaryRepository
from app.repositories.meeting_repository import MeetingRepository
from app.repositories.transcript_repository import TranscriptRepository
from app.schemas.summary import (
    MeetingSummary as MeetingSummarySchema,
    MeetingSummaryUpdate,
)

# ─────────────────────────────────────────────────────────────────────────────
# ROUTERS
# Two routers so we can mount at different prefixes in router.py
# ─────────────────────────────────────────────────────────────────────────────

# /meetings/{id}/summarize  &  /meetings/{id}/summary
meetings_summary_router = APIRouter(tags=["Meeting Summaries"])

# /summaries/{id}
summaries_router = APIRouter(tags=["Meeting Summaries"])


# ─────────────────────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────────────────────

async def get_summary_repo(db: AsyncSession = Depends(get_async_db)) -> SummaryRepository:
    return SummaryRepository(db)

async def get_meeting_repo(db: AsyncSession = Depends(get_async_db)) -> MeetingRepository:
    return MeetingRepository(db)

async def get_transcript_repo(db: AsyncSession = Depends(get_async_db)) -> TranscriptRepository:
    return TranscriptRepository(db)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

async def _get_summary_or_404(
    summary_id: uuid.UUID,
    company_id: uuid.UUID,
    repo: SummaryRepository,
) -> MeetingSummaryModel:
    summary = await repo.get_by_id(summary_id, company_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Summary {summary_id} not found")
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# POST /meetings/{id}/summarize
# ─────────────────────────────────────────────────────────────────────────────

@meetings_summary_router.post(
    "/{meeting_id}/summarize",
    summary     = "Trigger AI summary generation",
    description = (
        "Start background AI summary generation for a meeting. "
        "The summary will be available at GET /meetings/{id}/summary once complete."
    ),
    status_code = status.HTTP_202_ACCEPTED,
)
async def trigger_summary(
    meeting_id:      uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user     = Depends(get_current_user),
    meeting_repo:    MeetingRepository    = Depends(get_meeting_repo),
    transcript_repo: TranscriptRepository = Depends(get_transcript_repo),
    summary_repo:    SummaryRepository    = Depends(get_summary_repo),
):
    """Trigger async summary generation for a meeting."""
    # Validate meeting exists and belongs to company
    meeting = await meeting_repo.get_by_id(meeting_id, current_user.company_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Get transcript
    transcript_obj = await transcript_repo.get_by_meeting_id(
        meeting_id = meeting_id,
        company_id = current_user.company_id,
    )
    if not transcript_obj or not transcript_obj.content:
        raise HTTPException(
            status_code=400,
            detail="Meeting has no transcript. Transcribe the recording first."
        )

    # Extract participants from meeting attendees
    participants = [
        a.get("name") or a.get("email", "Unknown")
        for a in (meeting.attendees or [])
    ]

    # Fire background task
    background_tasks.add_task(
        _run_summary_in_background,
        meeting_id   = meeting_id,
        company_id   = current_user.company_id,
        title        = meeting.title,
        transcript   = transcript_obj.content,
        participants = participants,
        duration_min = meeting.duration_minutes,
        repo         = summary_repo,
    )

    return {
        "message":    "Summary generation started",
        "meeting_id": str(meeting_id),
        "status":     "processing",
    }


async def _run_summary_in_background(
    meeting_id:   uuid.UUID,
    company_id:   uuid.UUID,
    title:        str,
    transcript:   str,
    participants: list,
    duration_min: Optional[int],
    repo:         SummaryRepository,
) -> None:
    """Background coroutine that runs the summarizer."""
    from app.services.ai.summarizer import summarizer_service
    try:
        await summarizer_service.generate_summary(
            meeting_id   = meeting_id,
            company_id   = company_id,
            title        = title,
            transcript   = transcript,
            participants = participants,
            duration_min = duration_min,
            repo         = repo,
        )
    except Exception as exc:
        from loguru import logger
        logger.error(f"Background summary failed for meeting={meeting_id}: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# GET /meetings/{id}/summary
# ─────────────────────────────────────────────────────────────────────────────

@meetings_summary_router.get(
    "/{meeting_id}/summary",
    response_model = MeetingSummarySchema,
    summary        = "Get meeting summary",
)
async def get_meeting_summary(
    meeting_id:   uuid.UUID,
    current_user  = Depends(get_current_user),
    summary_repo: SummaryRepository = Depends(get_summary_repo),
):
    """Retrieve the AI-generated summary for a meeting."""
    summary = await summary_repo.get_by_meeting(meeting_id, current_user.company_id)
    if not summary:
        raise HTTPException(
            status_code=404,
            detail="No summary found for this meeting. Use POST /summarize to generate one."
        )
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# PUT /summaries/{id}  — user edits
# ─────────────────────────────────────────────────────────────────────────────

@summaries_router.put(
    "/{summary_id}",
    response_model = MeetingSummarySchema,
    summary        = "Update / user-edit a summary",
)
async def update_summary(
    summary_id:   uuid.UUID,
    data:         MeetingSummaryUpdate,
    current_user  = Depends(get_current_user),
    summary_repo: SummaryRepository = Depends(get_summary_repo),
):
    """Allow users to edit the AI-generated summary fields."""
    summary = await _get_summary_or_404(summary_id, current_user.company_id, summary_repo)
    updated = await summary_repo.update(summary, data)
    return updated


# ─────────────────────────────────────────────────────────────────────────────
# POST /summaries/{id}/regenerate
# ─────────────────────────────────────────────────────────────────────────────

@summaries_router.post(
    "/{summary_id}/regenerate",
    summary     = "Regenerate a meeting summary",
    status_code = status.HTTP_202_ACCEPTED,
)
async def regenerate_summary(
    summary_id:      uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user     = Depends(get_current_user),
    summary_repo:    SummaryRepository    = Depends(get_summary_repo),
    transcript_repo: TranscriptRepository = Depends(get_transcript_repo),
    meeting_repo:    MeetingRepository    = Depends(get_meeting_repo),
):
    """Force-regenerate an existing summary using the latest AI model."""
    summary = await _get_summary_or_404(summary_id, current_user.company_id, summary_repo)

    meeting = await meeting_repo.get_by_id(summary.meeting_id, current_user.company_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Parent meeting not found")

    transcript_obj = await transcript_repo.get_by_meeting_id(
        meeting_id = summary.meeting_id,
        company_id = current_user.company_id,
    )
    if not transcript_obj or not transcript_obj.content:
        raise HTTPException(status_code=400, detail="No transcript available for regeneration")

    participants = [
        a.get("name") or a.get("email", "Unknown")
        for a in (meeting.attendees or [])
    ]

    background_tasks.add_task(
        _run_summary_in_background,
        meeting_id   = summary.meeting_id,
        company_id   = current_user.company_id,
        title        = meeting.title,
        transcript   = transcript_obj.content,
        participants = participants,
        duration_min = meeting.duration_minutes,
        repo         = summary_repo,
    )

    return {
        "message":    "Summary regeneration started",
        "summary_id": str(summary_id),
        "status":     "processing",
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /summaries/{id}/export/{format}
# ─────────────────────────────────────────────────────────────────────────────

@summaries_router.get(
    "/{summary_id}/export/{fmt}",
    summary     = "Export summary to markdown / text",
    response_class = PlainTextResponse,
)
async def export_summary(
    summary_id:   uuid.UUID,
    fmt:          str,
    current_user  = Depends(get_current_user),
    summary_repo: SummaryRepository = Depends(get_summary_repo),
):
    """
    Export the summary as markdown (fmt=markdown) or plain text (fmt=text).
    PDF/DOCX generation can be added later via a dedicated export service.
    """
    if fmt not in ("markdown", "text", "md"):
        raise HTTPException(status_code=400, detail="Supported formats: markdown, text")

    summary = await _get_summary_or_404(summary_id, current_user.company_id, summary_repo)
    return _render_export(summary, fmt)


def _render_export(summary: MeetingSummaryModel, fmt: str) -> str:
    """Render summary as Markdown or plain text."""
    lines = []

    if fmt in ("markdown", "md"):
        lines.append(f"# Meeting Summary\n")
        if summary.short_summary:
            lines.append(f"> {summary.short_summary}\n")
        if summary.detailed_summary:
            lines.append(f"\n## Overview\n\n{summary.detailed_summary}\n")
        if summary.key_points:
            lines.append("\n## Key Discussion Points\n")
            for p in summary.key_points:
                lines.append(f"- {p}")
        if summary.decisions:
            lines.append("\n\n## Decisions Made\n")
            for d in summary.decisions:
                lines.append(f"- {d}")
        if summary.topics:
            lines.append("\n\n## Topics\n")
            for t in summary.topics:
                topic  = t.get("topic", "") if isinstance(t, dict) else str(t)
                sent   = t.get("sentiment", "") if isinstance(t, dict) else ""
                lines.append(f"- **{topic}** _{sent}_")
        if summary.sentiment:
            lines.append(f"\n\n---\n_Overall sentiment: **{summary.sentiment}**_")
    else:
        # Plain text
        if summary.short_summary:
            lines.append(f"SUMMARY: {summary.short_summary}\n")
        if summary.detailed_summary:
            lines.append(f"\nOVERVIEW:\n{summary.detailed_summary}\n")
        if summary.key_points:
            lines.append("\nKEY POINTS:")
            for p in summary.key_points:
                lines.append(f"  * {p}")
        if summary.decisions:
            lines.append("\nDECISIONS:")
            for d in summary.decisions:
                lines.append(f"  * {d}")
        if summary.sentiment:
            lines.append(f"\nSentiment: {summary.sentiment}")

    return "\n".join(lines)
