"""
WebSocket Connection Model
Vocaply AI Meeting Intelligence - Day 14

In-memory model (not a DB table) that describes a live WebSocket connection
and the subscriptions it holds.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Set
import asyncio

from fastapi import WebSocket

from app.core.websocket import SubscriptionChannel


@dataclass
class WebSocketConnection:
    """Represents a single authenticated WebSocket session."""

    # Connection basics
    connection_id: str                          # uuid4 string
    websocket: WebSocket                        # FastAPI WebSocket object

    # Auth state
    user_id: Optional[str]    = None
    company_id: Optional[str] = None
    is_authenticated: bool    = False

    # Subscriptions
    subscriptions: Set[SubscriptionChannel] = field(default_factory=set)
    # Extra resource IDs subscribed to (e.g. specific meeting IDs per channel)
    subscribed_resources: dict = field(default_factory=dict)   # channel → set[resource_id]

    # Lifecycle
    connected_at: datetime  = field(default_factory=datetime.utcnow)
    last_seen_at: datetime  = field(default_factory=datetime.utcnow)
    is_alive: bool          = True

    # Message queue for reliable delivery during transient errors
    message_queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=100))

    def touch(self) -> None:
        """Update last-seen timestamp (called on every message / pong)."""
        self.last_seen_at = datetime.utcnow()

    def subscribe(self, channel: SubscriptionChannel, resource_id: Optional[str] = None) -> None:
        self.subscriptions.add(channel)
        if resource_id:
            self.subscribed_resources.setdefault(channel, set()).add(resource_id)

    def unsubscribe(self, channel: SubscriptionChannel, resource_id: Optional[str] = None) -> None:
        if resource_id:
            resources = self.subscribed_resources.get(channel, set())
            resources.discard(resource_id)
            if not resources:
                self.subscriptions.discard(channel)
                self.subscribed_resources.pop(channel, None)
        else:
            self.subscriptions.discard(channel)
            self.subscribed_resources.pop(channel, None)

    def is_subscribed(self, channel: SubscriptionChannel, resource_id: Optional[str] = None) -> bool:
        if channel not in self.subscriptions:
            return False
        if resource_id:
            return resource_id in self.subscribed_resources.get(channel, set())
        return True

    def to_dict(self) -> dict:
        return {
            "connection_id":  self.connection_id,
            "user_id":        self.user_id,
            "company_id":     self.company_id,
            "is_authenticated": self.is_authenticated,
            "subscriptions":  [s.value for s in self.subscriptions],
            "connected_at":   self.connected_at.isoformat(),
            "last_seen_at":   self.last_seen_at.isoformat(),
        }
