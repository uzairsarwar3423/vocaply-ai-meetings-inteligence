"""
Speaker Diarization
Vocaply Platform - Day 7

Advanced speaker matching and identification.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from difflib import SequenceMatcher

from app.models.meeting import Meeting
from app.models.user import User


class SpeakerDiarization:
    """
    Speaker identification and matching service.
    
    Methods:
    1. Heuristic matching (attendee order, email domain)
    2. Voice fingerprinting (future with Deepgram's speaker recognition)
    3. Manual correction workflow
    """

    def __init__(self):
        pass

    # ============================================
    # AUTOMATIC MATCHING
    # ============================================

    def match_speakers_to_attendees(
        self,
        meeting: Meeting,
        speaker_ids: List[str],
        speaker_stats: Optional[Dict[str, Dict]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Match Deepgram speaker IDs to meeting attendees.
        
        Returns: {speaker_id: {name, email, user_id, confidence}}
        """
        attendees = meeting.attendees or []
        
        if not attendees:
            return self._create_unmatched_mapping(speaker_ids)

        # Strategy 1: Direct mapping if counts match
        if len(speaker_ids) == len(attendees):
            return self._map_by_order(speaker_ids, attendees)

        # Strategy 2: Use organizer heuristic
        organizer_email = meeting.organizer_email
        if organizer_email and len(speaker_ids) >= 1:
            return self._map_with_organizer_hint(speaker_ids, attendees, organizer_email, speaker_stats)

        # Strategy 3: Fallback to sequential
        return self._map_by_order(speaker_ids, attendees)

    def _map_by_order(
        self,
        speaker_ids: List[str],
        attendees: List[Dict],
    ) -> Dict[str, Dict[str, Any]]:
        """Simple 1:1 mapping in order"""
        mapping = {}
        for idx, speaker_id in enumerate(speaker_ids):
            if idx < len(attendees):
                attendee = attendees[idx]
                mapping[speaker_id] = {
                    "name": attendee.get("name"),
                    "email": attendee.get("email"),
                    "user_id": None,
                    "confidence": 0.6,  # Medium confidence
                }
            else:
                mapping[speaker_id] = {
                    "name": None,
                    "email": None,
                    "user_id": None,
                    "confidence": 0.0,
                }
        return mapping

    def _map_with_organizer_hint(
        self,
        speaker_ids: List[str],
        attendees: List[Dict],
        organizer_email: str,
        speaker_stats: Optional[Dict[str, Dict]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Use organizer as anchor point.
        Heuristic: organizer likely speaks most.
        """
        mapping = {}

        # Find organizer in attendee list
        organizer = next((a for a in attendees if a.get("email") == organizer_email), None)
        
        if not organizer or not speaker_stats:
            return self._map_by_order(speaker_ids, attendees)

        # Sort speakers by word count (descending)
        sorted_speakers = sorted(
            speaker_ids,
            key=lambda sid: speaker_stats.get(sid, {}).get("word_count", 0),
            reverse=True
        )

        # Assign top speaker to organizer
        if sorted_speakers:
            mapping[sorted_speakers[0]] = {
                "name": organizer.get("name"),
                "email": organizer.get("email"),
                "user_id": None,
                "confidence": 0.7,
            }

        # Assign rest in order
        remaining_speakers = [s for s in speaker_ids if s not in mapping]
        remaining_attendees = [a for a in attendees if a.get("email") != organizer_email]

        for idx, speaker_id in enumerate(remaining_speakers):
            if idx < len(remaining_attendees):
                attendee = remaining_attendees[idx]
                mapping[speaker_id] = {
                    "name": attendee.get("name"),
                    "email": attendee.get("email"),
                    "user_id": None,
                    "confidence": 0.5,
                }
            else:
                mapping[speaker_id] = {
                    "name": None,
                    "email": None,
                    "user_id": None,
                    "confidence": 0.0,
                }

        return mapping

    def _create_unmatched_mapping(
        self,
        speaker_ids: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """Create mapping with all speakers unmatched"""
        return {
            sid: {
                "name": None,
                "email": None,
                "user_id": None,
                "confidence": 0.0,
            }
            for sid in speaker_ids
        }

    # ============================================
    # NAME SIMILARITY
    # ============================================

    def fuzzy_match_name(
        self,
        detected_name: str,
        candidate_names: List[str],
        threshold: float = 0.7,
    ) -> Optional[Tuple[str, float]]:
        """
        Fuzzy match a detected name against candidates.
        Returns (matched_name, confidence) or None
        """
        detected_clean = self._normalize_name(detected_name)
        
        best_match = None
        best_score = 0.0

        for candidate in candidate_names:
            candidate_clean = self._normalize_name(candidate)
            score = SequenceMatcher(None, detected_clean, candidate_clean).ratio()
            
            if score > best_score:
                best_score = score
                best_match = candidate

        if best_score >= threshold:
            return (best_match, best_score)
        
        return None

    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        # Lowercase, remove punctuation, extra spaces
        name = name.lower().strip()
        name = re.sub(r"[^\w\s]", "", name)
        name = re.sub(r"\s+", " ", name)
        return name

    # ============================================
    # SPEAKER LABELS
    # ============================================

    def generate_speaker_label(
        self,
        speaker_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> str:
        """
        Generate display label for a speaker.
        Priority: Name > Email username > Speaker ID
        """
        if name:
            return name
        
        if email:
            # Extract username from email
            username = email.split("@")[0]
            # Title case with special handling for common patterns
            parts = re.split(r"[._-]", username)
            return " ".join(p.capitalize() for p in parts)
        
        # Fallback: prettify speaker ID
        # "speaker_0" → "Speaker A"
        if speaker_id.startswith("speaker_"):
            num = speaker_id.replace("speaker_", "")
            if num.isdigit():
                idx = int(num)
                letter = chr(65 + idx) if idx < 26 else num  # A-Z, then numbers
                return f"Speaker {letter}"
        
        return speaker_id.upper()

    # ============================================
    # CONFIDENCE SCORING
    # ============================================

    def calculate_match_confidence(
        self,
        speaker_stats: Dict[str, Any],
        attendee: Dict[str, Any],
        total_speakers: int,
        total_attendees: int,
    ) -> float:
        """
        Calculate confidence score for a speaker-attendee match.
        
        Factors:
        - Number mismatch penalty
        - Speaking time (more talking → higher confidence if matched to organizer)
        - Name similarity (if names available)
        """
        confidence = 0.5  # Base

        # Perfect count match
        if total_speakers == total_attendees:
            confidence += 0.2

        # Name similarity (if available)
        if speaker_stats.get("name") and attendee.get("name"):
            match = self.fuzzy_match_name(
                speaker_stats["name"],
                [attendee["name"]],
                threshold=0.6,
            )
            if match:
                confidence += 0.3 * match[1]

        return min(confidence, 1.0)