"""
Action Item Extractor
Vocaply Platform - Day 10: Action Item Extraction Logic
File: backend/app/services/ai/action_item_extractor.py

Orchestrates the full extraction pipeline:
  1. Load transcript chunks from DB
  2. Chunk text to fit model context window
  3. Call GPT-4o-mini via OpenAIService
  4. Parse + validate JSON response
  5. Match assignees to registered users (EntityMatcher)
  6. Confidence scoring
  7. Duplicate detection (title similarity)
  8. Due-date normalisation
  9. Priority assessment
 10. Persist extracted items via ActionItemRepository
"""
from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.action_item import ActionItem, ActionItemPriority
from app.models.ai_usage import AIFeatureType
from app.models.meeting import Meeting
from app.repositories.action_item_repository import ActionItemRepository
from app.repositories.transcript_repository import TranscriptRepository
from app.schemas.extraction import AnalyzeMeetingRequest, ExtractionSummary, ExtractedActionItem
from app.services.ai.entity_matcher import EntityMatcher
from app.services.ai.openai_service import openai_service


# ============================================
# CONSTANTS
# ============================================

MAX_CHUNK_WORDS     = 3_000     # default words per prompt
DEDUP_THRESHOLD     = 0.82      # SequenceMatcher ratio for duplicate detection
MIN_CONFIDENCE      = 0.40      # Items below this are discarded

# Natural-language → timedelta mapping for due-date inference
_RELATIVE_DATES: List[Tuple[re.Pattern, int]] = [
    (re.compile(r"\btoday\b",                   re.I), 0),
    (re.compile(r"\btomorrow\b",                re.I), 1),
    (re.compile(r"\bthis\s+week\b",             re.I), 3),
    (re.compile(r"\bend\s+of\s+(?:the\s+)?week\b", re.I), 5),
    (re.compile(r"\bnext\s+week\b",             re.I), 7),
    (re.compile(r"\btwo\s+weeks\b|2\s+weeks\b", re.I), 14),
    (re.compile(r"\bthis\s+month\b",            re.I), 14),
    (re.compile(r"\bend\s+of\s+(?:the\s+)?month\b", re.I), 28),
    (re.compile(r"\bmonday\b",                  re.I), None),   # handled below
    (re.compile(r"\btuesday\b",                 re.I), None),
    (re.compile(r"\bwednesday\b",               re.I), None),
    (re.compile(r"\bthursday\b",                re.I), None),
    (re.compile(r"\bfriday\b",                  re.I), None),
]

_WEEKDAY_MAP = {
    "monday": 0, "tuesday": 1, "wednesday": 2,
    "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
}

# Priority signals
_HIGH_PRIORITY_WORDS   = re.compile(
    r"\b(urgent|asap|immediately|critical|high.priority|blocker|must|crucial)\b", re.I
)
_LOW_PRIORITY_WORDS    = re.compile(
    r"\b(when.you.can|whenever|low.priority|nice.to.have|eventually)\b", re.I
)


# ============================================
# UTILITY FUNCTIONS
# ============================================

def _chunk_text(text: str, max_words: int) -> List[str]:
    """Split transcript text into chunks of at most `max_words` words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i : i + max_words]))
    return chunks


def _title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _is_duplicate(
    title: str,
    existing_titles: List[str],
    threshold: float = DEDUP_THRESHOLD,
) -> bool:
    return any(_title_similarity(title, existing) >= threshold for existing in existing_titles)


def _parse_iso_date(date_str: Optional[str]) -> Optional[datetime]:
    """Try to parse an ISO-8601 date string; return None on failure."""
    if not date_str:
        return None
    try:
        parsed = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _infer_due_date(date_hint: Optional[str]) -> Optional[datetime]:
    """
    Convert a natural-language date hint like 'by Friday' to a datetime.
    Falls back to ISO parsing if it looks like a date.
    """
    if not date_hint:
        return None

    # ISO date first
    iso = _parse_iso_date(date_hint)
    if iso:
        return iso

    now = datetime.now(tz=timezone.utc)

    # Weekday lookup
    for day_name, weekday_num in _WEEKDAY_MAP.items():
        if day_name in date_hint.lower():
            days_ahead = (weekday_num - now.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7      # next occurrence
            return (now + timedelta(days=days_ahead)).replace(
                hour=17, minute=0, second=0, microsecond=0
            )

    # Relative patterns
    for pattern, days in _RELATIVE_DATES:
        if pattern.search(date_hint) and days is not None:
            return (now + timedelta(days=days)).replace(
                hour=17, minute=0, second=0, microsecond=0
            )

    return None


def _assess_priority(
    text: str,
    ai_priority: str = "medium",
) -> str:
    """
    Override AI priority assessment with keyword signals from description/title.
    GPT-4o-mini's declared priority takes precedence unless overridden by keywords.
    """
    combined = text.lower()
    if _HIGH_PRIORITY_WORDS.search(combined):
        return ActionItemPriority.HIGH.value
    if _LOW_PRIORITY_WORDS.search(combined):
        return ActionItemPriority.LOW.value

    # Map generic strings to our enum
    mapping = {
        "urgent": ActionItemPriority.URGENT.value,
        "high":   ActionItemPriority.HIGH.value,
        "medium": ActionItemPriority.MEDIUM.value,
        "low":    ActionItemPriority.LOW.value,
    }
    return mapping.get(ai_priority.lower(), ActionItemPriority.MEDIUM.value)


def _compute_confidence(
    raw_confidence: float,
    has_assignee:   bool,
    has_due_date:   bool,
    quote_length:   int,
) -> float:
    """
    Adjust the model's raw confidence with structure bonuses.
    """
    score = max(0.0, min(1.0, raw_confidence))
    if has_assignee:
        score = min(1.0, score + 0.05)
    if has_due_date:
        score = min(1.0, score + 0.05)
    if quote_length > 20:
        score = min(1.0, score + 0.03)
    return round(score, 4)


def _item_fingerprint(title: str, assignee_email: Optional[str]) -> str:
    """Stable hash to detect exact duplicates across re-runs."""
    raw = f"{title.lower().strip()}|{(assignee_email or '').lower()}"
    return hashlib.md5(raw.encode()).hexdigest()  # noqa: S324


# ============================================
# MAIN EXTRACTOR CLASS
# ============================================

class ActionItemExtractor:
    """
    Full action-item extraction pipeline for a single meeting.

    Typical usage::

        extractor = ActionItemExtractor(db)
        summary   = await extractor.extract(
            meeting   = meeting_obj,
            request   = AnalyzeMeetingRequest(),
            user_id   = current_user_id,
        )
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db             = db
        self._transcript_repo = TranscriptRepository(db)
        self._action_repo    = ActionItemRepository(db)

    # ==========================================
    # PUBLIC ENTRY POINT
    # ==========================================

    async def extract(
        self,
        meeting:  Meeting,
        request:  AnalyzeMeetingRequest,
        user_id:  Optional[str] = None,
    ) -> ExtractionSummary:
        """
        Run the complete extraction pipeline.

        Returns an ExtractionSummary with counts and status.
        """
        started_at = datetime.now(tz=timezone.utc)
        summary = ExtractionSummary(
            meeting_id          = meeting.id,
            features_requested  = request.features,
            status              = "processing",
            processing_started_at = started_at,
        )

        try:
            # ── Step 1: Load full transcript ──────────────
            transcript_text, chunk_timeline = await self._load_transcript(meeting.id)
            if not transcript_text.strip():
                logger.warning(f"[Extractor] Meeting {meeting.id} has no transcript text.")
                summary.status = "completed"
                summary.processing_completed_at = datetime.now(tz=timezone.utc)
                return summary

            # ── Step 2: Build entity matcher ──────────────
            matcher = EntityMatcher.from_attendee_dicts(
                attendee_dicts = meeting.attendees or [],
            )

            # ── Step 3: Load existing titles for dedup ────
            existing_items  = await self._action_repo.list_by_meeting(
                meeting_id = meeting.id,
                company_id = uuid.UUID(str(meeting.company_id)),
            )
            existing_titles = [item.title for item in existing_items]
            existing_fps    = {
                _item_fingerprint(item.title, item.assignee_email)
                for item in existing_items
            }

            # ── Step 4: Chunk transcript & call GPT ───────
            max_words    = request.chunk_size_words or MAX_CHUNK_WORDS
            text_chunks  = _chunk_text(transcript_text, max_words)
            all_extracted: List[ExtractedActionItem] = []

            participant_names = ", ".join(
                a.get("name") or a.get("email", "") for a in (meeting.attendees or [])
            )
            meeting_date = (
                meeting.scheduled_start.strftime("%Y-%m-%d")
                if meeting.scheduled_start else "Unknown"
            )

            for chunk_idx, chunk in enumerate(text_chunks):
                logger.info(
                    f"[Extractor] Meeting {meeting.id} — chunk {chunk_idx + 1}/{len(text_chunks)}"
                )
                extracted = await self._call_gpt(
                    meeting_title     = meeting.title,
                    meeting_date      = meeting_date,
                    participant_names = participant_names,
                    transcript_text   = chunk,
                    company_id        = str(meeting.company_id),
                    meeting_id        = meeting.id,
                    user_id           = user_id,
                )
                all_extracted.extend(extracted)

            # ── Step 5: Filter, deduplicate, persist ──────
            new_items: List[ActionItem] = []
            duplicates_skipped = 0
            matched_to_users   = 0

            for ex in all_extracted:
                # Confidence filter
                if ex.confidence < (request.min_confidence or MIN_CONFIDENCE):
                    logger.debug(
                        f"[Extractor] Skipping low-confidence item: "
                        f"'{ex.title}' ({ex.confidence:.2f})"
                    )
                    continue

                # Fingerprint dedup
                fp = _item_fingerprint(ex.title, ex.assignee_email)
                if fp in existing_fps:
                    duplicates_skipped += 1
                    continue

                # Title similarity dedup
                if _is_duplicate(ex.title, existing_titles):
                    duplicates_skipped += 1
                    continue

                # Due date
                due_date = _infer_due_date(ex.due_date)

                # Priority
                priority = _assess_priority(
                    f"{ex.title} {ex.description or ''}",
                    ai_priority=ex.priority,
                )

                # Confidence adjustment
                confidence = _compute_confidence(
                    raw_confidence = ex.confidence,
                    has_assignee   = bool(ex.assignee_name or ex.assignee_email),
                    has_due_date   = due_date is not None,
                    quote_length   = len(ex.transcript_quote or ""),
                )

                # Entity matching
                match = matcher.match(ex.assignee_name, ex.assignee_email)
                if match.user_id:
                    matched_to_users += 1

                action_item = ActionItem(
                    meeting_id            = meeting.id,
                    company_id            = str(meeting.company_id),
                    assigned_to_id        = match.user_id,
                    title                 = ex.title[:500],
                    description           = ex.description,
                    is_ai_generated       = True,
                    confidence_score      = confidence,
                    transcript_quote      = ex.transcript_quote,
                    transcript_start_time = ex.transcript_start_time,
                    assignee_name         = match.name or ex.assignee_name,
                    assignee_email        = match.email or ex.assignee_email,
                    priority              = priority,
                    due_date              = due_date,
                )

                new_items.append(action_item)
                existing_titles.append(action_item.title)
                existing_fps.add(fp)

            # Bulk insert
            if new_items:
                await self._action_repo.bulk_create(new_items)

            # Update meeting counter
            total_count = len(existing_items) + len(new_items)
            meeting.action_items_count = total_count
            meeting.ai_analysis_status = "completed"
            meeting.ai_analysis_completed_at = datetime.now(tz=timezone.utc)
            await self._db.commit()

            summary.status                   = "completed"
            summary.action_items_extracted   = len(new_items)
            summary.duplicates_skipped       = duplicates_skipped
            summary.matched_to_users         = matched_to_users
            summary.processing_completed_at  = datetime.now(tz=timezone.utc)
            summary.meta["chunks_processed"] = len(text_chunks)
            summary.meta["total_extracted"]  = len(all_extracted)

            logger.info(
                f"[Extractor] Meeting {meeting.id} — "
                f"{len(new_items)} items saved, {duplicates_skipped} duplicates skipped, "
                f"{matched_to_users} matched to users."
            )
            return summary

        except Exception as exc:
            logger.error(f"[Extractor] Failed for meeting {meeting.id}: {exc}", exc_info=True)
            try:
                meeting.ai_analysis_status = "failed"
                await self._db.commit()
            except Exception:
                pass
            summary.status = "failed"
            summary.error  = str(exc)
            summary.processing_completed_at = datetime.now(tz=timezone.utc)
            return summary

    # ==========================================
    # PRIVATE: LOAD TRANSCRIPT
    # ==========================================

    async def _load_transcript(
        self,
        meeting_id: uuid.UUID,
    ) -> Tuple[str, Dict[float, str]]:
        """
        Load all transcript chunks for a meeting and assemble the full text.
        Also returns a timeline mapping start_time → text for quote lookup.
        Uses get_meeting_transcript from TranscriptRepository (no company_id filter needed
        since we are always filtering by meeting_id which is already company-scoped).
        """
        from app.models.transcript import Transcript
        from sqlalchemy import select as sa_select

        # Direct DB query — more reliable than relying on a possibly-absent company_id
        stmt = (
            sa_select(Transcript)
            .where(Transcript.meeting_id == meeting_id)
            .order_by(Transcript.sequence_number)
        )
        result = await self._db.execute(stmt)
        chunks = list(result.scalars().all())

        timeline: Dict[float, str] = {}
        lines: List[str] = []

        for chunk in chunks:
            speaker = chunk.speaker_name or chunk.speaker_id or "Speaker"
            text    = chunk.text or ""
            start   = chunk.start_time or 0.0
            lines.append(f"[{speaker}]: {text}")
            timeline[start] = text

        return "\n".join(lines), timeline

    # ==========================================
    # PRIVATE: GPT CALL
    # ==========================================

    async def _call_gpt(
        self,
        meeting_title:     str,
        meeting_date:      str,
        participant_names: str,
        transcript_text:   str,
        company_id:        str,
        meeting_id:        uuid.UUID,
        user_id:           Optional[str],
    ) -> List[ExtractedActionItem]:
        """
        Call GPT-4o-mini via OpenAIService and parse the JSON response
        into a list of ExtractedActionItem objects.
        """
        try:
            result = await openai_service.analyze(
                feature_type = AIFeatureType.ACTION_ITEM_EXTRACTION,
                variables    = {
                    "meeting_title":     meeting_title,
                    "meeting_date":      meeting_date,
                    "participant_names": participant_names,
                    "transcript_text":   transcript_text,
                },
                company_id = company_id,
                meeting_id = meeting_id,
                user_id    = user_id,
                db         = self._db,
            )

            if result.status != "success" or not result.parsed:
                logger.warning(
                    f"[Extractor] OpenAI returned non-success status: {result.status} "
                    f"| error: {result.error}"
                )
                return []

            raw_items: List[Dict[str, Any]] = result.parsed.get("action_items", [])
            extracted: List[ExtractedActionItem] = []

            for raw in raw_items:
                if not raw.get("title"):
                    continue
                try:
                    extracted.append(
                        ExtractedActionItem(
                            title                 = str(raw["title"])[:500],
                            description           = raw.get("description"),
                            assignee_name         = raw.get("assignee_name"),
                            assignee_email        = raw.get("assignee_email"),
                            due_date              = raw.get("due_date"),
                            priority              = raw.get("priority", "medium"),
                            category              = raw.get("category", "other"),
                            confidence            = float(raw.get("confidence", 0.5)),
                            transcript_quote      = raw.get("transcript_quote"),
                            transcript_start_time = raw.get("transcript_start_time"),
                        )
                    )
                except Exception as item_exc:
                    logger.debug(f"[Extractor] Skipping malformed action item: {item_exc}")

            return extracted

        except Exception as exc:
            logger.error(f"[Extractor] OpenAI call failed: {exc}", exc_info=True)
            return []


# ============================================
# SINGLETON
# ============================================

def get_extractor(db: AsyncSession) -> ActionItemExtractor:
    """Factory — creates a fresh extractor bound to the given session."""
    return ActionItemExtractor(db)
