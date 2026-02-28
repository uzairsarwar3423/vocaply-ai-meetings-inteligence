"""
Event Handler
Processes events from Zoom Meeting SDK
"""

import asyncio
from typing import Callable, Dict, Any, Optional
from datetime import datetime

from bot.participant_tracker import ParticipantTracker
from bot.audio_handler import AudioHandler


class ZoomEventHandler:
    """
    Handles all events from Zoom Meeting SDK.
    
    Events include:
    - Meeting connection (connecting, connected, disconnected)
    - Participants (join, leave)
    - Audio (mute, unmute)
    - Recording (start, stop, paused)
    - Chat messages
    - Screen sharing
    """

    def __init__(
        self,
        meeting_id: str,
        participant_tracker: ParticipantTracker,
        audio_handler: AudioHandler,
    ):
        self.meeting_id = meeting_id
        self.participant_tracker = participant_tracker
        self.audio_handler = audio_handler
        
        # Webhook callbacks
        self.webhooks: Dict[str, Callable] = {}
        
        # Event stats
        self.events_received = 0
        self.last_event_at: Optional[datetime] = None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WEBHOOK REGISTRATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def register_webhook(self, event_type: str, callback: Callable):
        """Register webhook callback for specific event"""
        self.webhooks[event_type] = callback

    async def _trigger_webhook(self, event_type: str, data: Dict[str, Any]):
        """Trigger webhook callback"""
        if event_type in self.webhooks:
            try:
                callback = self.webhooks[event_type]
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                print(f"Webhook error for {event_type}: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MEETING EVENTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def on_meeting_status_changed(self, status: int, result: int):
        """
        Called when meeting connection status changes.
        
        Status codes:
        0 = IDLE
        1 = CONNECTING
        2 = WAITING_FOR_HOST
        3 = IN_MEETING
        4 = DISCONNECTING
        5 = RECONNECTING
        6 = FAILED
        7 = ENDED
        """
        self._record_event()
        
        print(f"[Meeting] Status changed: {status} (result: {result})")
        
        await self._trigger_webhook("meeting.status_changed", {
            "meeting_id": self.meeting_id,
            "status": status,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Status-specific handling
        if status == 3:  # IN_MEETING
            await self.on_meeting_connected()
        elif status == 7:  # ENDED
            await self.on_meeting_ended()

    async def on_meeting_connected(self):
        """Called when successfully joined meeting"""
        print(f"[Meeting] Connected to meeting {self.meeting_id}")
        
        await self._trigger_webhook("bot.joined", {
            "meeting_id": self.meeting_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

    async def on_meeting_ended(self):
        """Called when meeting ends"""
        print(f"[Meeting] Meeting {self.meeting_id} ended")
        
        await self._trigger_webhook("bot.left", {
            "meeting_id": self.meeting_id,
            "timestamp": datetime.utcnow().isoformat(),
            "stats": {
                "participants": self.participant_tracker.get_stats(),
                "audio": self.audio_handler.get_stats(),
            },
        })

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PARTICIPANT EVENTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def on_user_join(self, user_list: list):
        """
        Called when participants join.
        
        Args:
            user_list: List of user IDs that joined
        """
        self._record_event()
        
        for user_id in user_list:
            # Get user info (would come from SDK)
            user_name = f"User {user_id}"
            is_host = False  # Would check via SDK
            
            self.participant_tracker.on_user_join(user_id, user_name, is_host)
            
            await self._trigger_webhook("participant.joined", {
                "meeting_id": self.meeting_id,
                "user_id": user_id,
                "user_name": user_name,
                "is_host": is_host,
                "timestamp": datetime.utcnow().isoformat(),
            })

    async def on_user_leave(self, user_list: list):
        """Called when participants leave"""
        self._record_event()
        
        for user_id in user_list:
            participant = self.participant_tracker.get_participant(user_id)
            user_name = participant.user_name if participant else f"User {user_id}"
            
            self.participant_tracker.on_user_leave(user_id)
            
            await self._trigger_webhook("participant.left", {
                "meeting_id": self.meeting_id,
                "user_id": user_id,
                "user_name": user_name,
                "timestamp": datetime.utcnow().isoformat(),
            })

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AUDIO EVENTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def on_user_audio_status_change(self, user_id: str, muted: bool):
        """Called when participant mutes/unmutes"""
        self._record_event()
        self.participant_tracker.on_audio_status_change(user_id, muted)
        
        await self._trigger_webhook("participant.audio_changed", {
            "meeting_id": self.meeting_id,
            "user_id": user_id,
            "muted": muted,
            "timestamp": datetime.utcnow().isoformat(),
        })

    async def on_audio_device_error(self, error_code: int):
        """Called when audio device error occurs"""
        self._record_event()
        
        print(f"[Audio] Device error: {error_code}")
        
        await self._trigger_webhook("bot.error", {
            "meeting_id": self.meeting_id,
            "error_type": "audio_device",
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat(),
        })

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # RECORDING EVENTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def on_recording_status_changed(self, status: int):
        """
        Called when cloud recording status changes.
        
        Status:
        0 = Not recording
        1 = Recording
        2 = Paused
        """
        self._record_event()
        
        status_map = {0: "stopped", 1: "recording", 2: "paused"}
        status_str = status_map.get(status, "unknown")
        
        print(f"[Recording] Status changed: {status_str}")
        
        await self._trigger_webhook("recording.status_changed", {
            "meeting_id": self.meeting_id,
            "status": status_str,
            "timestamp": datetime.utcnow().isoformat(),
        })

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _record_event(self):
        """Record event received"""
        self.events_received += 1
        self.last_event_at = datetime.utcnow()

    def get_stats(self) -> dict:
        """Get event handler statistics"""
        return {
            "events_received": self.events_received,
            "last_event_at": self.last_event_at.isoformat() if self.last_event_at else None,
        }