"""
Mock Transcription Streamer
Vocaply Platform - Day 28: Live Transcription & AI Hub
File: backend/app/services/transcription/mock_streamer.py

Used for demonstration and testing of live meeting features.
"""
import asyncio
import random
import uuid
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.services.meeting.live_service import get_live_meeting_service


MOCK_TRANSCRIPT_SCRIPTS = [
    "Hello everyone, thanks for joining today's project sync. We have a few updates to go over.",
    "First, regarding the design phase. Sarah, you mentioned you'd have the mockups ready for review?",
    "Yes, I'll have the final Figma designs shared by tomorrow afternoon.",
    "Great. Once we have those, we need to start the implementation. Uzair, can you handle the frontend dashboard components?",
    "Sure thing. I'll aim to get the initial layout and charts done by Friday.",
    "Perfect. Also, let's not forget the backend API. We need the new analytics endpoints to be stable by next Monday.",
    "I'll take ownership of that. I'll coordinate with the data team as well.",
    "Excellent. Any other blockers? If not, let's wrap this up. Thanks all!",
]


class MockStreamer:
    """
    Simulates a live transcription bot sending chunks to the service.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.live_service = get_live_meeting_service(db)

    async def stream_meeting(self, meeting_id: str, company_id: str):
        """
        Simulates a meeting by sending chunks every few seconds.
        """
        logger.info(f"Starting mock stream for meeting {meeting_id}")
        
        speakers = ["Organizer", "Sarah", "Uzair", "Backend Lead"]
        
        for i, text in enumerate(MOCK_TRANSCRIPT_SCRIPTS):
            speaker = speakers[i % len(speakers)]
            
            # Simulate "typing/streaming" vs "final" chunk
            # 1. Send "thinking" chunk (simulated intermediate result)
            words = text.split()
            if len(words) > 3:
                partial = " ".join(words[:len(words)//2])
                await self.live_service.handle_transcript_chunk(
                    meeting_id=meeting_id,
                    company_id=company_id,
                    speaker_name=speaker,
                    text=partial,
                    start_time=float(i * 10),
                    is_final=False
                )
                await asyncio.sleep(1.5)

            # 2. Send final chunk
            await self.live_service.handle_transcript_chunk(
                meeting_id=meeting_id,
                company_id=company_id,
                speaker_name=speaker,
                text=text,
                start_time=float(i * 10),
                is_final=True
            )
            
            # Wait between turns
            wait_time = random.uniform(2.0, 5.0)
            await asyncio.sleep(wait_time)

        logger.info(f"Mock stream finished for meeting {meeting_id}")


def get_mock_streamer(db: AsyncSession) -> MockStreamer:
    return MockStreamer(db)
