"""
Bot Schemas for Backend
Vocaply Platform - Day 15

Mirrors the shared bot models for the main backend.
"""

from enum import Enum
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel

class BotStatus(str, Enum):
    IDLE           = "idle"
    INITIALIZING   = "initializing"
    JOINING        = "joining"
    IN_CALL        = "in_call"
    LEAVING        = "leaving"
    LEFT           = "left"
    FAILED         = "failed"
    RECYCLING      = "recycling"
    TERMINATED     = "terminated"

class BotPlatform(str, Enum):
    ZOOM         = "zoom"
    GOOGLE_MEET  = "google_meet"
    TEAMS        = "teams"

class BotEvent(BaseModel):
    event_type:   str
    bot_id:       str
    meeting_id:   Optional[str] = None
    company_id:   Optional[str] = None
    status:       BotStatus
    platform:     Optional[BotPlatform] = None
    data:         Optional[dict] = None
    timestamp:    datetime = datetime.utcnow()
