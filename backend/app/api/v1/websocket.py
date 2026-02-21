"""
WebSocket API Endpoint
Vocaply AI Meeting Intelligence - Day 14

Mounts the single WebSocket endpoint at /api/v1/ws and drives the
per-connection event loop: receive → dispatch → send.
"""

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.core.logging import logger
from app.core.websocket import (
    ClientEvent,
    ServerEvent,
    WSErrorCode,
    WebSocketMessage,
)
from app.services.websocket_manager import ws_manager

router = APIRouter()


# ── Diagnostics endpoint ────────────────────────────────────────────────────────

@router.get("/ws/stats", tags=["WebSocket"])
async def websocket_stats():
    """Return current WebSocket server stats (admin / monitoring)."""
    return ws_manager.get_stats()


# ── Main WebSocket endpoint ─────────────────────────────────────────────────────

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Primary WebSocket endpoint.

    Protocol (all messages are JSON with shape WebSocketMessage):

    Client → Server
    ────────────────
    authenticate   { token: str }
    subscribe      { channel: str, resource_id?: str }
    unsubscribe    { channel: str, resource_id?: str }
    ping           {}

    Server → Client
    ────────────────
    connected      { connection_id }
    authenticated  { user_id, company_id }
    subscribed     { channel, resource_id }
    unsubscribed   { channel, resource_id }
    pong           { ts }
    error          { code, message, detail? }
    … plus all broadcast events
    """
    conn = await ws_manager.connect(websocket)

    try:
        while True:
            # Receive raw text (raises WebSocketDisconnect on close)
            raw = await websocket.receive_text()

            # Parse envelope
            try:
                payload = json.loads(raw)
                event   = payload.get("event", "")
                data    = payload.get("data") or {}
                req_id  = payload.get("request_id")
            except (json.JSONDecodeError, AttributeError):
                await _send_error(conn, WSErrorCode.INVALID_MESSAGE,
                                  "Message must be valid JSON.")
                continue

            conn.touch()

            # ── Dispatch ────────────────────────────────────────────────────
            try:
                if event == ClientEvent.AUTHENTICATE:
                    token = data.get("token", "")
                    if not token:
                        await _send_error(conn, WSErrorCode.AUTHENTICATION_FAILED,
                                          "token is required.")
                    else:
                        await ws_manager.authenticate(conn, token)

                elif event == ClientEvent.SUBSCRIBE:
                    if not conn.is_authenticated:
                        await _send_error(conn, WSErrorCode.AUTHENTICATION_REQUIRED,
                                          "Authenticate first.")
                    else:
                        channel     = data.get("channel", "")
                        resource_id = data.get("resource_id")
                        await ws_manager.subscribe(conn, channel, resource_id)

                elif event == ClientEvent.UNSUBSCRIBE:
                    channel     = data.get("channel", "")
                    resource_id = data.get("resource_id")
                    await ws_manager.unsubscribe(conn, channel, resource_id)

                elif event == ClientEvent.PING:
                    await ws_manager.handle_ping(conn)

                else:
                    await _send_error(conn, WSErrorCode.UNKNOWN_EVENT,
                                      f"Unknown event: {event!r}")

            except Exception as exc:
                logger.exception(f"WS dispatch error [{conn.connection_id}]: {exc}")
                await _send_error(conn, WSErrorCode.INTERNAL_ERROR,
                                  "An unexpected server error occurred.")

    except WebSocketDisconnect:
        logger.info(f"WS client disconnected: {conn.connection_id}")
    except Exception as exc:
        logger.exception(f"WS unexpected error [{conn.connection_id}]: {exc}")
    finally:
        await ws_manager.disconnect(conn.connection_id)


# ── Internal helper ─────────────────────────────────────────────────────────────

async def _send_error(conn, code: WSErrorCode, message: str) -> None:
    """Convenience wrapper so the dispatch block stays readable."""
    from app.core.websocket import WebSocketError
    error = WebSocketError(code=code.value, message=message)
    msg   = WebSocketMessage(event=ServerEvent.ERROR.value, data=error.model_dump())
    try:
        await conn.websocket.send_text(msg.model_dump_json())
    except Exception:
        pass
