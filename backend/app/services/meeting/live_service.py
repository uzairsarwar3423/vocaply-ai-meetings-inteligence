"""
Live Meeting Service
Vocaply Platform - Day 28: Live Transcription & AI Hub
File: backend/app/services/meeting/live_service.py

Handles real-time logic for active meetings:
  • Accumulating transcript chunks
  • Triggering extraction every N words/seconds
  • Broadcasting events to the room
"""
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.meeting import Meeting
from app.models.transcript import Transcript
from app.services.websocket_manager import ws_manager
from app.core.websocket import ServerEvent, SubscriptionChannel
from app.services.ai.action_item_extractor import ActionItemExtractor
from app.schemas.extraction import AnalyzeMeetingRequest


class MeetingLiveService:
    """
    Manages the session state for a meeting happening in real-time.
    Typically instantiated per active meeting or held in a global registry.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        # Cache for transcripts to avoid constant DB re-reads for extraction
        self._transcript_cache: Dict[str, List[str]] = {}
        # Track word counts for extraction triggers
        self._word_counts: Dict[str, int] = {}
        self._extraction_lock = asyncio.Lock()

    async def handle_transcript_chunk(
        self,
        meeting_id: str,
        company_id: str,
        speaker_name: str,
        text: str,
        start_time: float,
        is_final: bool = True
    ):
        """
        Processes a new chunk of transcription.
        1. Broadcasts to all live listeners.
        2. Persists to DB (if final).
        3. Checks if it's time to run AI extraction.
        """
        # Broadcast immediately to frontend
        await ws_manager.broadcast_to_company(
            company_id=company_id,
            event=ServerEvent.TRANSCRIPT_CHUNK,
            data={
                "meeting_id": meeting_id,
                "speaker": speaker_name,
                "text": text,
                "start_time": start_time,
                "is_final": is_final
            },
            channel=SubscriptionChannel.MEETING_LIVE,
            resource_id=meeting_id
        )

        if not is_final:
            return

        # Cache text for extraction
        current_text = self._transcript_cache.get(meeting_id, [])
        current_text.append(f"[{speaker_name}]: {text}")
        self._transcript_cache[meeting_id] = current_text
        
        count = self._word_counts.get(meeting_id, 0) + len(text.split())
        self._word_counts[meeting_id] = count

        # Trigger extraction every 150 words
        if count >= 150:
            asyncio.create_task(self.trigger_live_extraction(meeting_id, company_id))
            self._word_counts[meeting_id] = 0

    async def trigger_live_extraction(self, meeting_id: str, company_id: str):
        """
        Runs the extraction pipeline on the recent transcript history.
        Only extracts 'new' items since the last run.
        """
        if self._extraction_lock.locked():
            return
            
        async with self._extraction_lock:
            try:
                from app.repositories.meeting_repository import MeetingRepository
                repo = MeetingRepository(self.db)
                meeting = await repo.get_by_id(uuid.UUID(meeting_id), company_id=company_id)
                
                if not meeting:
                    return

                extractor = ActionItemExtractor(self.db)
                # We request extraction for the entire transcript so far (incremental logic is in extractor)
                summary = await extractor.extract(
                    meeting=meeting,
                    request=AnalyzeMeetingRequest(features=["action_items"], min_confidence=0.6)
                )

                if summary.action_items_extracted > 0:
                    logger.info(f"Live Extraction: Found {summary.action_items_extracted} items for {meeting_id}")
                    # The extractor persists them to DB. We notification subscribers.
                    await ws_manager.broadcast_to_company(
                        company_id=company_id,
                        event=ServerEvent.LIVE_ACTION_ITEM,
                        data={
                            "meeting_id": meeting_id,
                            "count": summary.action_items_extracted,
                            "message": f"Identified {summary.action_items_extracted} new action items."
                        },
                        channel=SubscriptionChannel.MEETING_LIVE,
                        resource_id=meeting_id
                    )
            except Exception as e:
                logger.error(f"Live extraction failed for {meeting_id}: {e}")

live_meeting_service = None # Dependency provided by FastAPI

def get_live_meeting_service(db: AsyncSession) -> MeetingLiveService:
    return MeetingLiveService(db)
