"""
Real-time Broadcast Service
Vocaply AI Meeting Intelligence - Day 14

High-level helpers called by API endpoints, Celery workers, and other
services to push live events to connected clients.  All permission
checks and channel filtering are centralised here so callers only need
to provide the data.
"""

from typing import Any, Optional

from app.core.logging import logger
from app.core.websocket import ServerEvent, SubscriptionChannel
from app.services.websocket_manager import ws_manager


# ── Meeting events ─────────────────────────────────────────────────────────────

async def broadcast_meeting_updated(
    company_id: str,
    meeting_data: dict,
    exclude_user_id: Optional[str] = None,
) -> None:
    """Notify all company members that a meeting was updated."""
    count = await ws_manager.broadcast_to_company(
        company_id=company_id,
        event=ServerEvent.MEETING_UPDATED,
        data=meeting_data,
        channel=SubscriptionChannel.MEETING,
        exclude_user_id=exclude_user_id,
    )
    logger.debug(f"broadcast_meeting_updated → {count} connections (company={company_id})")


# ── Action item events ─────────────────────────────────────────────────────────

async def broadcast_action_item_created(
    company_id: str,
    action_item_data: dict,
    exclude_user_id: Optional[str] = None,
) -> None:
    """Notify company members that a new action item was created."""
    count = await ws_manager.broadcast_to_company(
        company_id=company_id,
        event=ServerEvent.ACTION_ITEM_CREATED,
        data=action_item_data,
        channel=SubscriptionChannel.ACTION_ITEMS,
        exclude_user_id=exclude_user_id,
    )
    logger.debug(f"broadcast_action_item_created → {count} connections (company={company_id})")


async def broadcast_action_item_updated(
    company_id: str,
    action_item_data: dict,
    exclude_user_id: Optional[str] = None,
) -> None:
    """Notify company members that an action item was updated."""
    count = await ws_manager.broadcast_to_company(
        company_id=company_id,
        event=ServerEvent.ACTION_ITEM_UPDATED,
        data=action_item_data,
        channel=SubscriptionChannel.ACTION_ITEMS,
        exclude_user_id=exclude_user_id,
    )
    logger.debug(f"broadcast_action_item_updated → {count} connections (company={company_id})")


# ── Notification events ────────────────────────────────────────────────────────

async def send_notification_to_user(
    user_id: str,
    notification_data: dict,
) -> None:
    """Push a personal notification to a specific user (all tabs)."""
    count = await ws_manager.send_to_user(
        user_id=user_id,
        event=ServerEvent.NOTIFICATION_RECEIVED,
        data=notification_data,
    )
    logger.debug(f"send_notification_to_user → {count} connections (user={user_id})")


async def broadcast_notification_to_company(
    company_id: str,
    notification_data: dict,
) -> None:
    """Push a notification to every member of a company."""
    count = await ws_manager.broadcast_to_company(
        company_id=company_id,
        event=ServerEvent.NOTIFICATION_RECEIVED,
        data=notification_data,
        channel=SubscriptionChannel.NOTIFICATIONS,
    )
    logger.debug(f"broadcast_notification_to_company → {count} connections (company={company_id})")


# ── Bot / transcription events ────────────────────────────────────────────────

async def broadcast_bot_status_changed(
    company_id: str,
    meeting_id: str,
    status: str,
    detail: Optional[str] = None,
) -> None:
    """Inform clients that a meeting bot changed its status."""
    count = await ws_manager.broadcast_to_company(
        company_id=company_id,
        event=ServerEvent.BOT_STATUS_CHANGED,
        data={
            "meeting_id": meeting_id,
            "status":     status,
            "detail":     detail,
        },
        channel=SubscriptionChannel.MEETING,
    )
    logger.debug(f"broadcast_bot_status_changed ({status}) → {count} connections")


async def broadcast_transcript_chunk(
    company_id: str,
    meeting_id: str,
    chunk: dict,
) -> None:
    """
    Stream a live transcript chunk to all subscribers of the meeting channel.

    chunk is expected to contain at minimum:
      {
        "speaker": str | None,
        "text": str,
        "start_time": float,
        "is_final": bool,
      }
    """
    count = await ws_manager.broadcast_to_company(
        company_id=company_id,
        event=ServerEvent.TRANSCRIPT_CHUNK,
        data={"meeting_id": meeting_id, **chunk},
        channel=SubscriptionChannel.MEETING,
    )
    logger.debug(f"broadcast_transcript_chunk → {count} connections (meeting={meeting_id})")


async def broadcast_to_meeting(
    meeting_id: str,
    event_data: dict,
) -> None:
    """
    Day 19: Broadcaster for bot events.
    Sends raw event data to all users in the company who are viewing the meeting.
    
    This is a simpler wrapper that uses the raw dict structure from Day 19 components.
    """
    # We need the company_id to use broadcast_to_company.
    # In Day 19, we'll fetch it from the meeting or just broadcast to everyone 
    # if company_id is not available (but it's better to have it).
    
    # For now, we'll try to find a connection for this meeting to get company_id
    # or just use a placeholder if needed. 
    # Real implementation should probably have company_id passed in.
    
    # Let's iterate over connections to find company_id for this meeting_id
    company_id = None
    for conn in ws_manager._connections.values():
        if conn.is_subscribed(SubscriptionChannel.MEETING, meeting_id):
            company_id = conn.company_id
            break
            
    if not company_id:
        return

    await ws_manager.broadcast_to_company(
        company_id=company_id,
        event=event_data.get("type", ServerEvent.MEETING_UPDATED),
        data=event_data.get("data"),
        channel=SubscriptionChannel.MEETING,
        resource_id=meeting_id
    )
