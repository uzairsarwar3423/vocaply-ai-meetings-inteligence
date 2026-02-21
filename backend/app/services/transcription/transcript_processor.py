"""
Transcript Processor
Vocaply Platform - Day 7

Processes Deepgram response into database-ready transcript chunks.
Handles speaker matching, chunking, and storage.
"""

import uuid
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from app.models.transcript import Transcript, TranscriptMetadata
from app.models.meeting import Meeting
from app.repositories.transcript_repository import TranscriptRepository


class TranscriptProcessor:
    """
    Processes raw Deepgram transcription into structured DB records.
    
    Flow:
    1. Parse Deepgram response
    2. Match speakers to meeting attendees
    3. Create transcript chunks
    4. Generate metadata
    5. Save to database
    """

    def __init__(self, repository: TranscriptRepository):
        self.repo = repository

    # ============================================
    # MAIN PROCESSING
    # ============================================

    async def process_transcription(
        self,
        meeting: Meeting,
        deepgram_result: Dict[str, Any],
        audio_duration: float,
    ) -> Tuple[int, TranscriptMetadata]:
        """
        Process complete Deepgram response and save to DB.
        Returns (chunks_created, metadata)
        """
        # Extract structured data
        speaker_turns = deepgram_result.get("speaker_turns", [])
        words = deepgram_result.get("words", [])
        avg_confidence = deepgram_result.get("average_confidence")
        detected_language = deepgram_result.get("language", "en")
        
        # Match speakers to meeting attendees
        speaker_map = self._match_speakers(meeting, speaker_turns)

        # Create transcript chunks from speaker turns
        chunks = []
        for idx, turn in enumerate(speaker_turns):
            speaker_id = str(turn.get("speaker", "unknown"))
            mapped = speaker_map.get(speaker_id, {})

            chunk = Transcript(
                meeting_id=meeting.id,
                company_id=meeting.company_id,
                user_id=mapped.get("user_id"),
                text=turn.get("text", ""),
                speaker_id=speaker_id,
                speaker_name=mapped.get("name"),
                speaker_email=mapped.get("email"),
                start_time=turn.get("start", 0.0),
                end_time=turn.get("end", 0.0),
                duration=turn.get("end", 0.0) - turn.get("start", 0.0),
                timestamp=self._calculate_timestamp(meeting, turn.get("start", 0.0)),
                confidence=self._calculate_turn_confidence(turn, words),
                language=detected_language,
                sequence_number=idx,
                words=self._extract_turn_words(turn, words),
            )
            chunks.append(chunk)

        # Bulk insert chunks
        await self.repo.bulk_create_chunks(chunks)

        # Create metadata
        speakers = deepgram_result.get("speaker_turns", [])
        speaker_list = self._build_speaker_list(speaker_turns, speaker_map)

        metadata = TranscriptMetadata(
            meeting_id=meeting.id,
            company_id=meeting.company_id,
            total_chunks=len(chunks),
            total_words=sum(len(c.text.split()) for c in chunks),
            total_duration_seconds=audio_duration,
            average_confidence=avg_confidence,
            speaker_count=len(speaker_list),
            speakers=speaker_list,
            detected_language=detected_language,
            deepgram_request_id=deepgram_result.get("request_id"),
            deepgram_model=deepgram_result.get("model"),
        )

        await self.repo.create_metadata(metadata)

        return len(chunks), metadata

    # ============================================
    # SPEAKER MATCHING
    # ============================================

    def _match_speakers(
        self,
        meeting: Meeting,
        speaker_turns: List[Dict],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Match Deepgram speaker IDs to meeting attendees.
        
        Strategy:
        1. If meeting has <= 2 attendees, map directly (speaker_0 → first attendee)
        2. Use voice fingerprinting (future)
        3. Use calendar invite order as heuristic
        4. Let users manually assign later
        """
        speaker_map = {}
        attendees = meeting.attendees or []

        # Extract unique speaker IDs
        unique_speakers = list({str(t.get("speaker")) for t in speaker_turns if t.get("speaker") is not None})
        unique_speakers.sort()

        # Simple heuristic: map in order
        for idx, speaker_id in enumerate(unique_speakers):
            if idx < len(attendees):
                attendee = attendees[idx]
                speaker_map[speaker_id] = {
                    "name": attendee.get("name"),
                    "email": attendee.get("email"),
                    "user_id": None,  # TODO: lookup user by email
                }
            else:
                speaker_map[speaker_id] = {
                    "name": None,
                    "email": None,
                    "user_id": None,
                }

        return speaker_map

    # ============================================
    # HELPERS
    # ============================================

    def _calculate_timestamp(
        self,
        meeting: Meeting,
        offset_seconds: float,
    ) -> Optional[datetime]:
        """Calculate absolute timestamp from meeting start + offset"""
        if not meeting.actual_start:
            return None
        return meeting.actual_start + timedelta(seconds=offset_seconds)

    def _calculate_turn_confidence(
        self,
        turn: Dict,
        all_words: List[Dict],
    ) -> Optional[float]:
        """Calculate average confidence for a speaker turn"""
        start = turn.get("start", 0)
        end = turn.get("end", 0)
        
        # Find words in this turn's time range
        turn_words = [
            w for w in all_words
            if w.get("start", 0) >= start and w.get("end", 0) <= end
        ]
        
        if not turn_words:
            return None
        
        confidences = [w.get("confidence", 0) for w in turn_words if "confidence" in w]
        return sum(confidences) / len(confidences) if confidences else None

    def _extract_turn_words(
        self,
        turn: Dict,
        all_words: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Extract word-level timestamps for a turn"""
        start = turn.get("start", 0)
        end = turn.get("end", 0)
        
        turn_words = [
            {
                "word": w.get("word"),
                "start": w.get("start"),
                "end": w.get("end"),
                "confidence": w.get("confidence"),
            }
            for w in all_words
            if w.get("start", 0) >= start and w.get("end", 0) <= end
        ]
        
        return turn_words

    def _build_speaker_list(
        self,
        speaker_turns: List[Dict],
        speaker_map: Dict[str, Dict],
    ) -> List[Dict[str, Any]]:
        """Build aggregated speaker metadata list"""
        speakers_stats = {}

        for turn in speaker_turns:
            speaker_id = str(turn.get("speaker", "unknown"))
            
            if speaker_id not in speakers_stats:
                mapped = speaker_map.get(speaker_id, {})
                speakers_stats[speaker_id] = {
                    "id": speaker_id,
                    "name": mapped.get("name"),
                    "email": mapped.get("email"),
                    "word_count": 0,
                    "duration": 0.0,
                }

            speakers_stats[speaker_id]["word_count"] += turn.get("num_words", 0)
            speakers_stats[speaker_id]["duration"] += (turn.get("end", 0) - turn.get("start", 0))

        return list(speakers_stats.values())

    # ============================================
    # SPEAKER REASSIGNMENT
    # ============================================

    async def reassign_speaker(
        self,
        meeting_id: uuid.UUID,
        old_speaker_id: str,
        new_name: Optional[str] = None,
        new_email: Optional[str] = None,
    ) -> int:
        """
        Manually reassign a speaker across all chunks.
        Returns number of chunks updated.
        """
        return await self.repo.update_speaker_info(
            meeting_id=meeting_id,
            speaker_id=old_speaker_id,
            name=new_name,
            email=new_email,
        )

    # ============================================
    # MERGING & SPLITTING
    # ============================================

    async def merge_chunks(
        self,
        chunk_ids: List[uuid.UUID],
    ) -> Optional[Transcript]:
        """Merge multiple chunks into one (e.g., same speaker, consecutive)"""
        chunks = await self.repo.get_chunks_by_ids(chunk_ids)
        
        if not chunks or len(chunks) < 2:
            return None

        # Sort by sequence
        chunks.sort(key=lambda c: c.sequence_number)

        # Verify same meeting and speaker
        if len({c.meeting_id for c in chunks}) > 1:
            raise ValueError("Cannot merge chunks from different meetings")
        if len({c.speaker_id for c in chunks}) > 1:
            raise ValueError("Cannot merge chunks from different speakers")

        # Create merged chunk
        merged = Transcript(
            meeting_id=chunks[0].meeting_id,
            company_id=chunks[0].company_id,
            user_id=chunks[0].user_id,
            text=" ".join(c.text for c in chunks),
            speaker_id=chunks[0].speaker_id,
            speaker_name=chunks[0].speaker_name,
            speaker_email=chunks[0].speaker_email,
            start_time=chunks[0].start_time,
            end_time=chunks[-1].end_time,
            duration=chunks[-1].end_time - chunks[0].start_time,
            timestamp=chunks[0].timestamp,
            confidence=sum(c.confidence or 0 for c in chunks) / len(chunks),
            language=chunks[0].language,
            sequence_number=chunks[0].sequence_number,
            words=sum([c.words or [] for c in chunks], []),
        )

        # Save merged, delete old
        await self.repo.create_chunk(merged)
        await self.repo.delete_chunks(chunk_ids)

        return merged