"""
Shared Bot Status Models
Vocaply AI Meeting Intelligence - Day 15

Canonical definitions shared by bot-service, platform-specific bots,
and the main backend.  Import from here to keep enum values in sync.
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# ── Enums ──────────────────────────────────────────────────────────────────────

class BotStatus(str, Enum):
    """Lifecycle status of a single bot instance."""
    IDLE           = "idle"           # In pool, available for assignment
    INITIALIZING   = "initializing"   # Being set up (Playwright loading)
    JOINING        = "joining"        # Navigating to meeting URL
    IN_CALL        = "in_call"        # Actively in the meeting
    LEAVING        = "leaving"        # Gracefully exiting the meeting
    LEFT           = "left"           # Successfully left, ready to recycle
    FAILED         = "failed"         # Unrecoverable error
    RECYCLING      = "recycling"      # Being cleaned up / re-initialised
    TERMINATED     = "terminated"     # Permanently shut down


class BotPlatform(str, Enum):
    """Supported meeting platforms."""
    ZOOM         = "zoom"
    GOOGLE_MEET  = "google_meet"
    TEAMS        = "teams"


class BotPoolStatus(str, Enum):
    """Pool membership state."""
    AVAILABLE = "available"
    IN_USE    = "in_use"
    DRAINING  = "draining"   # Being removed from pool


# ── Pydantic models ────────────────────────────────────────────────────────────

class BotInfo(BaseModel):
    """Snapshot of a bot instance's current state (stored in Redis)."""
    bot_id:            str
    status:            BotStatus
    platform:          Optional[BotPlatform] = None
    meeting_id:        Optional[str]         = None
    meeting_url:       Optional[str]         = None
    company_id:        Optional[str]         = None
    user_id:           Optional[str]         = None
    participant_count: int                   = 0
    created_at:        datetime              = datetime.utcnow()
    updated_at:        datetime              = datetime.utcnow()
    error_message:     Optional[str]         = None
    retry_count:       int                   = 0


class BotEvent(BaseModel):
    """Webhook event payload sent from bot-service → main backend."""
    event_type:   str                    # e.g. "bot_joined", "bot_left", "error"
    bot_id:       str
    meeting_id:   Optional[str] = None
    company_id:   Optional[str] = None
    status:       BotStatus
    platform:     Optional[BotPlatform] = None
    data:         Optional[dict]        = None
    timestamp:    datetime              = datetime.utcnow()


class CreateBotRequest(BaseModel):
    """Payload to POST /bots/create."""
    meeting_id:   str
    meeting_url:  str
    platform:     BotPlatform
    company_id:   str
    user_id:      str
    display_name: str = "Vocaply Bot"
    record_audio: bool = True


class BotStatusResponse(BaseModel):
    """Response body for GET /bots/{id}/status."""
    bot_id:            str
    status:            BotStatus
    pool_status:       Optional[BotPoolStatus] = None
    meeting_id:        Optional[str]           = None
    platform:          Optional[BotPlatform]   = None
    participant_count: int                     = 0
    created_at:        Optional[datetime]      = None
    updated_at:        Optional[datetime]      = None
    error_message:     Optional[str]           = None
