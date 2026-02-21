"""
Bot Session Model
Vocaply AI Meeting Intelligence - Day 15

Tracks the binding between a bot instance and a specific meeting.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from shared.models.bot_status import BotPlatform

class BotSession(BaseModel):
    session_id: str
    bot_id: str
    meeting_id: str
    company_id: str
    platform: BotPlatform
    started_at: datetime = datetime.utcnow()
    ended_at: Optional[datetime] = None
    transcript_s3_key: Optional[str] = None
    audio_s3_key: Optional[str] = None
