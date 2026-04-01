"""
WebSocket Core Configuration
Vocaply AI Meeting Intelligence - Day 14

Defines WebSocket event types, message schemas, error codes, and
shared constants used across the WebSocket infrastructure.
"""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel


# ── Event Types ────────────────────────────────────────────────────────────────

class ClientEvent(str, Enum):
    """Events sent from client → server."""
    AUTHENTICATE        = "authenticate"
    SUBSCRIBE           = "subscribe"
    UNSUBSCRIBE         = "unsubscribe"
    PING                = "ping"
    CHAT_MESSAGE        = "chat_message"


class ServerEvent(str, Enum):
    """Events sent from server → client."""
    # Connection lifecycle
    CONNECTED           = "connected"
    AUTHENTICATED       = "authenticated"
    SUBSCRIBED          = "subscribed"
    UNSUBSCRIBED        = "unsubscribed"
    PONG                = "pong"
    ERROR               = "error"

    # Meeting events
    MEETING_UPDATED     = "meeting_updated"

    # Action item events
    ACTION_ITEM_CREATED = "action_item_created"
    ACTION_ITEM_UPDATED = "action_item_updated"

    # Notification events
    NOTIFICATION_RECEIVED = "notification_received"

    # Bot/transcription events
    BOT_STATUS_CHANGED  = "bot_status_changed"
    TRANSCRIPT_CHUNK    = "transcript_chunk"
    CHAT_RESPONSE       = "chat_response"
    LIVE_ACTION_ITEM    = "live_action_item"


# ── Subscription Channels ──────────────────────────────────────────────────────

class SubscriptionChannel(str, Enum):
    """Available subscription channels."""
    MEETING       = "meeting"
    MEETING_LIVE  = "meeting_live"
    ACTION_ITEMS  = "action_items"
    NOTIFICATIONS = "notifications"


# ── Message Schemas ────────────────────────────────────────────────────────────

class WebSocketMessage(BaseModel):
    """Base WebSocket message envelope."""
    event: str
    data: Optional[Any] = None
    request_id: Optional[str] = None   # client-supplied correlation ID


class WebSocketError(BaseModel):
    """Error payload sent to client."""
    code: str
    message: str
    detail: Optional[Any] = None


# ── Error Codes ────────────────────────────────────────────────────────────────

class WSErrorCode(str, Enum):
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    AUTHENTICATION_FAILED   = "AUTHENTICATION_FAILED"
    INVALID_MESSAGE         = "INVALID_MESSAGE"
    UNKNOWN_EVENT           = "UNKNOWN_EVENT"
    SUBSCRIPTION_FAILED     = "SUBSCRIPTION_FAILED"
    PERMISSION_DENIED       = "PERMISSION_DENIED"
    RATE_LIMITED            = "RATE_LIMITED"
    INTERNAL_ERROR          = "INTERNAL_ERROR"


# ── Constants ──────────────────────────────────────────────────────────────────

WS_HEARTBEAT_INTERVAL   = 30    # seconds between server pings
WS_AUTH_TIMEOUT         = 10    # seconds to send authenticate after connect
WS_MAX_CONNECTIONS      = 1000  # global connection ceiling
WS_MAX_MESSAGE_SIZE     = 64 * 1024  # 64 KB per message
WS_QUEUE_SIZE           = 100   # max queued messages per connection
