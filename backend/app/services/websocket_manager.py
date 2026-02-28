"""
WebSocket Connection Manager
Vocaply AI Meeting Intelligence - Day 14

Manages the lifecycle of all active WebSocket connections:
  • Accept / disconnect connections
  • Authenticate connections via JWT
  • Room-based subscriptions (broadcast to all members of a company)
  • Send messages to individual connections or entire company rooms
  • Heartbeat bookkeeping
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from app.core.config import settings
from app.core.logging import logger
from app.core.websocket import (
    ClientEvent,
    ServerEvent,
    SubscriptionChannel,
    WebSocketError,
    WebSocketMessage,
    WSErrorCode,
    WS_HEARTBEAT_INTERVAL,
    WS_QUEUE_SIZE,
)
from app.models.websocket_connection import WebSocketConnection


class WebSocketManager:
    """
    Central registry and dispatcher for all WebSocket connections.

    Internal data layout
    ─────────────────────
    _connections  : Dict[connection_id, WebSocketConnection]
    _user_rooms   : Dict[user_id,       Set[connection_id]]    # one user → N tabs
    _company_rooms: Dict[company_id,    Set[connection_id]]    # all company members
    """

    def __init__(self) -> None:
        self._connections:   Dict[str, WebSocketConnection] = {}
        self._user_rooms:    Dict[str, Set[str]]            = {}
        self._company_rooms: Dict[str, Set[str]]            = {}
        self._lock = asyncio.Lock()

    # ──────────────────────────────────────────────────────────────────────────
    # Connection lifecycle
    # ──────────────────────────────────────────────────────────────────────────

    async def connect(self, websocket: WebSocket) -> WebSocketConnection:
        """Accept the raw WebSocket upgrade and register the connection."""
        await websocket.accept()

        connection_id = str(uuid.uuid4())
        conn = WebSocketConnection(
            connection_id=connection_id,
            websocket=websocket,
        )

        async with self._lock:
            self._connections[connection_id] = conn

        logger.info(f"WS connect: {connection_id} | total={len(self._connections)}")

        # Send a welcome frame so the client knows the socket is live
        await self._send(conn, ServerEvent.CONNECTED, {
            "connection_id": connection_id,
            "message": "Connected. Please authenticate.",
        })
        return conn

    async def disconnect(self, connection_id: str) -> None:
        """Clean up all state for a connection."""
        async with self._lock:
            conn = self._connections.pop(connection_id, None)
            if conn is None:
                return

            conn.is_alive = False

            if conn.user_id:
                self._user_rooms.get(conn.user_id, set()).discard(connection_id)
                if not self._user_rooms.get(conn.user_id):
                    self._user_rooms.pop(conn.user_id, None)

            if conn.company_id:
                self._company_rooms.get(conn.company_id, set()).discard(connection_id)
                if not self._company_rooms.get(conn.company_id):
                    self._company_rooms.pop(conn.company_id, None)

        logger.info(f"WS disconnect: {connection_id} | total={len(self._connections)}")

    # ──────────────────────────────────────────────────────────────────────────
    # Authentication
    # ──────────────────────────────────────────────────────────────────────────

    async def authenticate(self, conn: WebSocketConnection, token: str) -> bool:
        """
        Validate the JWT bearer token sent by the client in the 'authenticate'
        event.  On success the connection is moved into the user / company rooms.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            user_id:    Optional[str] = payload.get("sub")
            company_id: Optional[str] = payload.get("company_id")

            if not user_id:
                raise ValueError("Token missing 'sub' claim")

            conn.user_id        = user_id
            conn.company_id     = company_id
            conn.is_authenticated = True
            conn.touch()

            async with self._lock:
                self._user_rooms.setdefault(user_id, set()).add(conn.connection_id)
                if company_id:
                    self._company_rooms.setdefault(company_id, set()).add(conn.connection_id)

            await self._send(conn, ServerEvent.AUTHENTICATED, {
                "user_id":    user_id,
                "company_id": company_id,
            })
            logger.info(f"WS authenticated: {conn.connection_id} user={user_id}")
            return True

        except (JWTError, ValueError) as exc:
            await self._send_error(conn, WSErrorCode.AUTHENTICATION_FAILED, str(exc))
            return False

    # ──────────────────────────────────────────────────────────────────────────
    # Subscriptions
    # ──────────────────────────────────────────────────────────────────────────

    async def subscribe(
        self,
        conn: WebSocketConnection,
        channel_name: str,
        resource_id: Optional[str] = None,
    ) -> None:
        """Subscribe an authenticated connection to a channel."""
        if not conn.is_authenticated:
            await self._send_error(conn, WSErrorCode.AUTHENTICATION_REQUIRED,
                                   "Authenticate before subscribing.")
            return

        try:
            channel = SubscriptionChannel(channel_name)
        except ValueError:
            await self._send_error(conn, WSErrorCode.SUBSCRIPTION_FAILED,
                                   f"Unknown channel: {channel_name}")
            return

        conn.subscribe(channel, resource_id)
        await self._send(conn, ServerEvent.SUBSCRIBED, {
            "channel":     channel.value,
            "resource_id": resource_id,
        })

    async def unsubscribe(
        self,
        conn: WebSocketConnection,
        channel_name: str,
        resource_id: Optional[str] = None,
    ) -> None:
        """Unsubscribe a connection from a channel."""
        try:
            channel = SubscriptionChannel(channel_name)
            conn.unsubscribe(channel, resource_id)
            await self._send(conn, ServerEvent.UNSUBSCRIBED, {
                "channel":     channel.value,
                "resource_id": resource_id,
            })
        except ValueError:
            await self._send_error(conn, WSErrorCode.SUBSCRIPTION_FAILED,
                                   f"Unknown channel: {channel_name}")

    # ──────────────────────────────────────────────────────────────────────────
    # Sending messages
    # ──────────────────────────────────────────────────────────────────────────

    async def send_to_connection(
        self, connection_id: str, event: ServerEvent, data: Any = None
    ) -> bool:
        conn = self._connections.get(connection_id)
        if conn and conn.is_alive:
            await self._send(conn, event, data)
            return True
        return False

    async def send_to_user(
        self, user_id: str, event: ServerEvent, data: Any = None
    ) -> int:
        """Broadcast to all open tabs of a single user. Returns send count."""
        connection_ids = self._user_rooms.get(user_id, set()).copy()
        count = 0
        for cid in connection_ids:
            if await self.send_to_connection(cid, event, data):
                count += 1
        return count

    async def broadcast_to_company(
        self,
        company_id: str,
        event: ServerEvent,
        data: Any = None,
        channel: Optional[SubscriptionChannel] = None,
        resource_id: Optional[str] = None,
        exclude_user_id: Optional[str] = None,
    ) -> int:
        """
        Broadcast to all active connections of a company.

        If *channel* is given, only connections subscribed to that channel
        receive the message.
        """
        connection_ids = self._company_rooms.get(company_id, set()).copy()
        count = 0
        for cid in connection_ids:
            conn = self._connections.get(cid)
            if not conn or not conn.is_alive:
                continue
            if exclude_user_id and conn.user_id == exclude_user_id:
                continue
            if channel and not conn.is_subscribed(channel, resource_id):
                continue
            await self._send(conn, event, data)
            count += 1
        return count

    # ──────────────────────────────────────────────────────────────────────────
    # Heartbeat
    # ──────────────────────────────────────────────────────────────────────────

    async def handle_ping(self, conn: WebSocketConnection) -> None:
        conn.touch()
        await self._send(conn, ServerEvent.PONG, {"ts": datetime.utcnow().isoformat()})

    async def run_heartbeat(self) -> None:
        """Background task: cull stale connections periodically."""
        while True:
            await asyncio.sleep(WS_HEARTBEAT_INTERVAL)
            now = datetime.utcnow()
            stale_ids: List[str] = []

            for cid, conn in list(self._connections.items()):
                elapsed = (now - conn.last_seen_at).total_seconds()
                if elapsed > WS_HEARTBEAT_INTERVAL * 3:
                    stale_ids.append(cid)

            for cid in stale_ids:
                logger.warning(f"WS heartbeat timeout, closing: {cid}")
                conn = self._connections.get(cid)
                if conn:
                    try:
                        await conn.websocket.close(code=1001)
                    except Exception:
                        pass
                await self.disconnect(cid)

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    async def _send(
        self,
        conn: WebSocketConnection,
        event: ServerEvent,
        data: Any = None,
        request_id: Optional[str] = None,
    ) -> None:
        if not conn.is_alive:
            return
        payload = WebSocketMessage(event=event.value, data=data, request_id=request_id)
        try:
            await conn.websocket.send_text(payload.model_dump_json())
        except Exception as exc:
            logger.error(f"WS send failed {conn.connection_id}: {exc}")
            conn.is_alive = False

    async def _send_error(
        self,
        conn: WebSocketConnection,
        code: WSErrorCode,
        message: str,
        detail: Any = None,
        request_id: Optional[str] = None,
    ) -> None:
        error = WebSocketError(code=code.value, message=message, detail=detail)
        await self._send(conn, ServerEvent.ERROR, error.model_dump(), request_id)

    # ──────────────────────────────────────────────────────────────────────────
    # Diagnostics
    # ──────────────────────────────────────────────────────────────────────────

    @property
    def total_connections(self) -> int:
        return len(self._connections)

    def get_company_connection_count(self, company_id: str) -> int:
        return len(self._company_rooms.get(company_id, set()))

    def get_stats(self) -> dict:
        return {
            "total_connections":   self.total_connections,
            "total_users":         len(self._user_rooms),
            "total_companies":     len(self._company_rooms),
        }


# Global singleton – import this everywhere instead of instantiating locally
ws_manager = WebSocketManager()
