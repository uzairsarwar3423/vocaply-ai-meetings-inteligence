"""
Meeting Summarizer Service
Vocaply Platform - Day 13

Uses GPT-4o-mini to produce structured meeting summaries:
  - Executive overview (2-3 paragraphs)
  - Key discussion points
  - Decisions made
  - Topics with sentiment
  - Overall sentiment
  - Next steps / follow-ups
"""
from __future__ import annotations

import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from loguru import logger
from openai import AsyncOpenAI

from app.core.config import settings
from app.models.meeting_summary import MeetingSummary
from app.repositories.summary_repository import SummaryRepository


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT
# ─────────────────────────────────────────────────────────────────────────────

SUMMARY_SYSTEM_PROMPT = """You are an expert meeting analyst. Analyze the meeting transcript and return a JSON object with the following exact structure:

{
  "short_summary": "A single-sentence TL;DR (max 150 chars)",
  "detailed_summary": "2-3 paragraph executive overview in markdown. Include context, main discussion, and outcomes.",
  "key_points": ["point 1", "point 2", ...],
  "decisions": ["decision 1", "decision 2", ...],
  "next_steps": ["follow-up 1", "follow-up 2", ...],
  "topics": [
    {"topic": "Topic Name", "sentiment": "positive|neutral|negative", "importance": 0.0-1.0}
  ],
  "sentiment": "positive|neutral|negative",
  "sentiment_score": 0.0-1.0,
  "participant_insights": [
    {"name": "Speaker Name", "contribution": "brief description", "sentiment": "positive|neutral|negative"}
  ]
}

Rules:
- key_points: 3-8 specific discussion points
- decisions: Only explicit decisions made, empty list if none
- next_steps: Concrete follow-ups with ownership when possible
- topics: 3-7 main topics discussed
- All text must be professional and concise
- Return valid JSON only, no markdown wrapper"""


SUMMARY_USER_PROMPT = """Meeting Title: {title}
Duration: {duration}
Participants: {participants}
Date: {date}

TRANSCRIPT:
{transcript}

Analyze this meeting and return the structured JSON summary."""


# ─────────────────────────────────────────────────────────────────────────────
# SERVICE
# ─────────────────────────────────────────────────────────────────────────────

class MeetingSummarizerService:
    """
    Generates AI meeting summaries using GPT-4o-mini.
    Stores results in meeting_summaries table via SummaryRepository.
    """

    def __init__(self) -> None:
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        self._client = AsyncOpenAI(api_key=api_key or "dummy-key")
        self._model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    async def generate_summary(
        self,
        *,
        meeting_id:   UUID,
        company_id:   UUID,
        title:        str,
        transcript:   str,
        participants: List[str] | None = None,
        duration_min: int | None = None,
        meeting_date: datetime | None = None,
        repo:         SummaryRepository,
    ) -> MeetingSummary:
        """
        Generate a meeting summary and persist it.

        Args:
            meeting_id:   UUID of the parent meeting
            company_id:   UUID of the company (multi-tenant)
            title:        Meeting title
            transcript:   Full transcript text
            participants: List of participant names
            duration_min: Meeting duration in minutes
            meeting_date: When the meeting occurred
            repo:         Injected SummaryRepository for DB access

        Returns:
            Persisted MeetingSummary ORM instance
        """
        if not transcript or not transcript.strip():
            raise ValueError("Cannot summarize an empty transcript")

        # Truncate extremely long transcripts (~100k token safe limit)
        transcript = self._truncate_transcript(transcript, max_chars=80_000)

        user_prompt = SUMMARY_USER_PROMPT.format(
            title       = title,
            duration    = f"{duration_min} minutes" if duration_min else "unknown",
            participants= ", ".join(participants) if participants else "unknown",
            date        = meeting_date.strftime("%Y-%m-%d %H:%M") if meeting_date else "unknown",
            transcript  = transcript,
        )

        t0 = time.monotonic()
        raw_json, token_usage = await self._call_openai(user_prompt)
        elapsed = time.monotonic() - t0

        parsed = self._parse_response(raw_json)

        summary_obj = MeetingSummary(
            id                      = uuid.uuid4(),
            meeting_id              = meeting_id,
            company_id              = str(company_id),
            short_summary           = parsed.get("short_summary"),
            detailed_summary        = parsed.get("detailed_summary"),
            key_points              = parsed.get("key_points", []),
            decisions               = parsed.get("decisions", []),
            topics                  = parsed.get("topics", []),
            sentiment               = parsed.get("sentiment"),
            model_version           = self._model,
            generation_time_seconds = round(elapsed, 2),
            token_usage             = token_usage,
        )

        # Attach extra fields as meta (not in base model)
        summary_obj.__dict__["next_steps"]           = parsed.get("next_steps", [])
        summary_obj.__dict__["sentiment_score"]      = parsed.get("sentiment_score", 0.5)
        summary_obj.__dict__["participant_insights"] = parsed.get("participant_insights", [])

        persisted = await repo.create_or_update(summary_obj)
        logger.info(
            f"Summary generated for meeting={meeting_id} "
            f"in {elapsed:.1f}s | tokens={token_usage}"
        )
        return persisted

    async def regenerate_summary(
        self,
        *,
        meeting_id:   UUID,
        company_id:   UUID,
        title:        str,
        transcript:   str,
        participants: List[str] | None = None,
        duration_min: int | None = None,
        meeting_date: datetime | None = None,
        repo:         SummaryRepository,
    ) -> MeetingSummary:
        """Force-regenerate (bypasses cache, overwrites existing)."""
        return await self.generate_summary(
            meeting_id   = meeting_id,
            company_id   = company_id,
            title        = title,
            transcript   = transcript,
            participants = participants,
            duration_min = duration_min,
            meeting_date = meeting_date,
            repo         = repo,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL
    # ─────────────────────────────────────────────────────────────────────────

    async def _call_openai(self, user_prompt: str) -> tuple[str, int]:
        """Call GPT-4o-mini and return (raw_content, total_tokens)."""
        try:
            response = await self._client.chat.completions.create(
                model           = self._model,
                messages        = [
                    {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature     = 0.3,
                max_tokens      = 2048,
                response_format = {"type": "json_object"},
            )
            content     = response.choices[0].message.content or "{}"
            total_tokens = response.usage.total_tokens if response.usage else 0
            return content, total_tokens
        except Exception as exc:
            logger.error(f"OpenAI summarization failed: {exc}")
            raise

    @staticmethod
    def _parse_response(raw: str) -> Dict[str, Any]:
        """Parse JSON response with safe fallback."""
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(f"Could not parse summary JSON: {raw[:200]}")
            return {
                "short_summary":    "Summary generation encountered an issue.",
                "detailed_summary": raw[:2000],
                "key_points":       [],
                "decisions":        [],
                "next_steps":       [],
                "topics":           [],
                "sentiment":        "neutral",
            }

    @staticmethod
    def _truncate_transcript(text: str, max_chars: int = 80_000) -> str:
        """Truncate from the middle to preserve start and end context."""
        if len(text) <= max_chars:
            return text
        half = max_chars // 2
        return (
            text[:half]
            + "\n\n[...transcript truncated for length...]\n\n"
            + text[-half:]
        )


# ─────────────────────────────────────────────────────────────────────────────
# SINGLETON
# ─────────────────────────────────────────────────────────────────────────────

summarizer_service = MeetingSummarizerService()
