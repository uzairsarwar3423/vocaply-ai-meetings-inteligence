"""
Entity Matcher
Vocaply Platform - Day 10: Action Item Extraction Logic
File: backend/app/services/ai/entity_matcher.py

Matches extracted assignee names / emails from AI output to
actual registered users in the database.

Strategy (in priority order):
  1. Exact email match
  2. Lowercased email match
  3. Fuzzy first-name + last-name match against attendee list
  4. First-name-only partial match (lower confidence)
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple


# ── simple name normaliser ───────────────────────────────────────

def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def _name_similarity(a: str, b: str) -> float:
    """SequenceMatcher ratio between two normalised strings."""
    return SequenceMatcher(None, _normalise(a), _normalise(b)).ratio()


# ============================================
# ATTENDEE CANDIDATE
# ============================================

class AttendeeCandidate:
    """
    Lightweight representation of a meeting participant or
    registered user — fed into the matcher.
    """
    __slots__ = ("user_id", "name", "email")

    def __init__(
        self,
        user_id: Optional[str],
        name: Optional[str],
        email: Optional[str],
    ) -> None:
        self.user_id = user_id
        self.name    = name or ""
        self.email   = email or ""


# ============================================
# MATCH RESULT
# ============================================

class MatchResult:
    """Outcome of a single entity-matching attempt."""

    __slots__ = ("user_id", "email", "name", "confidence", "method")

    def __init__(
        self,
        user_id:    Optional[str],
        email:      Optional[str],
        name:       Optional[str],
        confidence: float,
        method:     str,
    ) -> None:
        self.user_id    = user_id
        self.email      = email
        self.name       = name
        self.confidence = confidence
        self.method     = method   # "exact_email" | "fuzzy_name" | "partial_name" | "unmatched"


# ============================================
# ENTITY MATCHER SERVICE
# ============================================

class EntityMatcher:
    """
    Matches AI-extracted assignee mentions to known attendees / users.

    Usage::

        candidates = [
            AttendeeCandidate(user_id="u1", name="Alice Smith", email="alice@co.com"),
            AttendeeCandidate(user_id=None,  name="Bob",         email="bob@vendor.com"),
        ]
        matcher = EntityMatcher(candidates)

        result = matcher.match(
            assignee_name="Alice",
            assignee_email=None,
        )
        # result.user_id == "u1", result.confidence == 0.85
    """

    # Thresholds
    FULL_NAME_THRESHOLD  = 0.80
    PARTIAL_NAME_THRESHOLD = 0.65

    def __init__(self, attendees: List[AttendeeCandidate]) -> None:
        self._attendees = attendees
        # Pre-build email → candidate index for O(1) lookup
        self._email_index: Dict[str, AttendeeCandidate] = {
            a.email.lower(): a for a in attendees if a.email
        }

    # ── Public API ───────────────────────────────────────────────

    def match(
        self,
        assignee_name:  Optional[str],
        assignee_email: Optional[str],
    ) -> MatchResult:
        """
        Attempt to match an extracted assignee to a known attendee.

        Returns a MatchResult with confidence 0.0–1.0.
        Confidence < 0.5 means the match is speculative.
        """
        # Strategy 1: exact email
        if assignee_email:
            candidate = self._email_index.get(assignee_email.lower())
            if candidate:
                return MatchResult(
                    user_id    = candidate.user_id,
                    email      = candidate.email,
                    name       = candidate.name,
                    confidence = 1.0,
                    method     = "exact_email",
                )

        # Strategy 2: fuzzy full-name match
        if assignee_name:
            best_score: float = 0.0
            best_candidate: Optional[AttendeeCandidate] = None

            for att in self._attendees:
                score = _name_similarity(assignee_name, att.name)
                if score > best_score:
                    best_score     = score
                    best_candidate = att

            if best_candidate and best_score >= self.FULL_NAME_THRESHOLD:
                return MatchResult(
                    user_id    = best_candidate.user_id,
                    email      = best_candidate.email,
                    name       = best_candidate.name,
                    confidence = best_score,
                    method     = "fuzzy_name",
                )

            # Strategy 3: first-name partial match
            if best_candidate and best_score >= self.PARTIAL_NAME_THRESHOLD:
                return MatchResult(
                    user_id    = best_candidate.user_id,
                    email      = best_candidate.email,
                    name       = best_candidate.name,
                    confidence = best_score * 0.9,   # slight penalty
                    method     = "partial_name",
                )

        # No match
        return MatchResult(
            user_id    = None,
            email      = assignee_email,
            name       = assignee_name,
            confidence = 0.0,
            method     = "unmatched",
        )

    def match_all(
        self,
        pairs: List[Tuple[Optional[str], Optional[str]]],
    ) -> List[MatchResult]:
        """Batch match. pairs = [(name, email), ...]"""
        return [self.match(name, email) for name, email in pairs]

    @classmethod
    def from_attendee_dicts(
        cls,
        attendee_dicts: List[dict],
        registered_users: Optional[List[dict]] = None,
    ) -> "EntityMatcher":
        """
        Build from the meeting.attendees JSONB list and optional
        list of registered user dicts {"id", "name", "email"}.
        """
        candidates: List[AttendeeCandidate] = []

        # Seed from meeting attendees
        for att in attendee_dicts or []:
            candidates.append(
                AttendeeCandidate(
                    user_id = att.get("user_id"),
                    name    = att.get("name") or att.get("email", ""),
                    email   = att.get("email"),
                )
            )

        # Override with registered user data if available
        if registered_users:
            email_to_idx = {c.email.lower(): i for i, c in enumerate(candidates) if c.email}
            for u in registered_users:
                email = (u.get("email") or "").lower()
                idx   = email_to_idx.get(email)
                if idx is not None:
                    candidates[idx].user_id = u.get("id")
                    candidates[idx].name    = u.get("name") or candidates[idx].name
                else:
                    candidates.append(
                        AttendeeCandidate(
                            user_id = u.get("id"),
                            name    = u.get("name") or "",
                            email   = u.get("email") or "",
                        )
                    )

        return cls(candidates)
