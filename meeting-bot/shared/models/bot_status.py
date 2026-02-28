"""
Bot Status Models
Shared across bot service and platform backend

State machine for bot lifecycle.
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BotStatus(str, Enum):
    """Bot lifecycle states"""
    # Pool states
    INITIALIZING = "initializing"    # Starting up browser
    AVAILABLE    = "available"       # Ready in pool
    
    # Active states
    ASSIGNED     = "assigned"        # Assigned to meeting
    JOINING      = "joining"         # Navigating to meeting
    IN_MEETING   = "in_meeting"      # Successfully joined
    RECORDING    = "recording"       # Actively recording
    
    # Terminal states
    LEAVING      = "leaving"         # Exiting meeting
    COMPLETED    = "completed"       # Session ended successfully
    FAILED       = "failed"          # Error occurred
    TERMINATED   = "terminated"      # Manually stopped


class BotPlatform(str, Enum):
    """Supported meeting platforms"""
    ZOOM         = "zoom"
    GOOGLE_MEET  = "google_meet"
    TEAMS        = "teams"
    WEBEX        = "webex"


class BotInstance(BaseModel):
    """Bot instance data structure"""
    bot_id:            str
    status:            BotStatus
    platform:          Optional[BotPlatform] = None
    meeting_id:        Optional[str] = None
    meeting_url:       Optional[str] = None
    company_id:        Optional[str] = None
    
    # Metadata
    created_at:        datetime
    assigned_at:       Optional[datetime] = None
    joined_at:         Optional[datetime] = None
    left_at:           Optional[datetime] = None
    
    # Monitoring
    last_heartbeat:    Optional[datetime] = None
    participant_count: int = 0
    is_alone:          bool = False
    alone_since:       Optional[datetime] = None
    
    # Recording
    recording_started: Optional[datetime] = None
    recording_path:    Optional[str] = None
    recording_size_mb: float = 0.0
    
    # Error tracking
    error:             Optional[str] = None
    retry_count:       int = 0

    class Config:
        use_enum_values = True


class BotEvent(BaseModel):
    """Event emitted by bot for webhook delivery"""
    event_type:   str  # bot.joined, bot.recording.started, bot.left, bot.error
    bot_id:       str
    meeting_id:   str
    company_id:   str
    timestamp:    datetime
    data:         dict = Field(default_factory=dict)


# ============================================
# STATE TRANSITIONS
# ============================================

VALID_TRANSITIONS = {
    BotStatus.INITIALIZING: [BotStatus.AVAILABLE, BotStatus.FAILED],
    BotStatus.AVAILABLE:    [BotStatus.ASSIGNED, BotStatus.TERMINATED],
    BotStatus.ASSIGNED:     [BotStatus.JOINING, BotStatus.FAILED],
    BotStatus.JOINING:      [BotStatus.IN_MEETING, BotStatus.FAILED],
    BotStatus.IN_MEETING:   [BotStatus.RECORDING, BotStatus.LEAVING, BotStatus.FAILED],
    BotStatus.RECORDING:    [BotStatus.LEAVING, BotStatus.FAILED],
    BotStatus.LEAVING:      [BotStatus.COMPLETED, BotStatus.FAILED],
    BotStatus.COMPLETED:    [],
    BotStatus.FAILED:       [BotStatus.TERMINATED],
    BotStatus.TERMINATED:   [],
}


def can_transition(from_status: BotStatus, to_status: BotStatus) -> bool:
    """Check if state transition is valid"""
    return to_status in VALID_TRANSITIONS.get(from_status, [])