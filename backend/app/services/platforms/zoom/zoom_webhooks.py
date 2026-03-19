"""
Zoom Webhooks Handler
Processes webhook events from Zoom
"""

from typing import Dict
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.meeting import Meeting, MeetingStatus
from app.models.platform_connection import PlatformConnection
from app.services.bot import BotScheduler


class ZoomWebhooksHandler:
    """
    Handles Zoom webhook events.
    
    Events:
    - meeting.started - Auto-create bot session
    - meeting.ended - Finalize recordings
    - recording.completed - Import recording
    - participant.joined/left - Track participants
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def handle_event(self, event_data: Dict):
        """
        Route webhook event to appropriate handler.
        
        Args:
            event_data: Zoom webhook payload
        """
        event_type = event_data.get("event")
        
        print(f"[ZoomWebhook] Received event: {event_type}")
        
        # Route to handler
        handlers = {
            "meeting.started": self._handle_meeting_started,
            "meeting.ended": self._handle_meeting_ended,
            "recording.completed": self._handle_recording_completed,
            "participant.joined": self._handle_participant_joined,
            "participant.left": self._handle_participant_left,
        }
        
        handler = handlers.get(event_type)
        
        if handler:
            await handler(event_data)
        else:
            print(f"[ZoomWebhook] Unhandled event: {event_type}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # EVENT HANDLERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _handle_meeting_started(self, event_data: Dict):
        """
        Handle meeting.started event.
        
        Auto-creates bot session if meeting is tracked in platform.
        """
        payload = event_data.get("payload", {})
        object_data = payload.get("object", {})
        
        zoom_meeting_id = str(object_data.get("id"))
        host_id = object_data.get("host_id")
        topic = object_data.get("topic")
        start_time = object_data.get("start_time")
        
        print(f"[ZoomWebhook] Meeting started: {zoom_meeting_id} - {topic}")
        
        # Find meeting in our database
        stmt = select(Meeting).where(
            Meeting.platform_meeting_id == zoom_meeting_id
        )
        result = await self.db.execute(stmt)
        meeting = result.scalar_one_or_none()
        
        if meeting:
            # Update status
            meeting.status = MeetingStatus.IN_PROGRESS.value
            meeting.actual_start = datetime.fromisoformat(
                start_time.replace("Z", "+00:00")
            )
            
            await self.db.commit()
            
            # Check if auto-join is enabled
            if meeting.bot_enabled:
                print(f"[ZoomWebhook] Auto-starting bot for meeting {meeting.id}")
                
                bot_scheduler = BotScheduler(self.db)
                await bot_scheduler.start_bot_for_meeting(
                    meeting_id=str(meeting.id),
                    company_id=str(meeting.company_id),
                )
        else:
            print(f"[ZoomWebhook] Meeting {zoom_meeting_id} not found in database")

    async def _handle_meeting_ended(self, event_data: Dict):
        """Handle meeting.ended event"""
        payload = event_data.get("payload", {})
        object_data = payload.get("object", {})
        
        zoom_meeting_id = str(object_data.get("id"))
        duration = object_data.get("duration")
        
        print(f"[ZoomWebhook] Meeting ended: {zoom_meeting_id}, duration: {duration}min")
        
        # Find meeting
        stmt = select(Meeting).where(
            Meeting.platform_meeting_id == zoom_meeting_id
        )
        result = await self.db.execute(stmt)
        meeting = result.scalar_one_or_none()
        
        if meeting:
            meeting.status = MeetingStatus.COMPLETED.value
            meeting.actual_end = datetime.utcnow()
            meeting.duration_minutes = duration
            
            await self.db.commit()

    async def _handle_recording_completed(self, event_data: Dict):
        """
        Handle recording.completed event.
        
        Import Zoom cloud recording to platform.
        """
        payload = event_data.get("payload", {})
        object_data = payload.get("object", {})
        
        zoom_meeting_id = str(object_data.get("id"))
        recording_files = object_data.get("recording_files", [])
        
        print(f"[ZoomWebhook] Recording completed: {zoom_meeting_id}")
        
        # Find meeting
        stmt = select(Meeting).where(
            Meeting.platform_meeting_id == zoom_meeting_id
        )
        result = await self.db.execute(stmt)
        meeting = result.scalar_one_or_none()
        
        if meeting and recording_files:
            # Get first video recording
            video_recording = next(
                (f for f in recording_files if f.get("file_type") == "MP4"),
                None
            )
            
            if video_recording:
                # Store recording URL (requires download_url token)
                meeting.meta_data = meeting.meta_data or {}
                meeting.meta_data["zoom_recording"] = {
                    "download_url": video_recording.get("download_url"),
                    "file_size": video_recording.get("file_size"),
                    "recording_start": video_recording.get("recording_start"),
                    "recording_end": video_recording.get("recording_end"),
                }
                
                await self.db.commit()
                
                print(f"[ZoomWebhook] Recording URL saved for meeting {meeting.id}")

    async def _handle_participant_joined(self, event_data: Dict):
        """Handle participant.joined event"""
        payload = event_data.get("payload", {})
        object_data = payload.get("object", {})
        
        participant = object_data.get("participant", {})
        user_name = participant.get("user_name")
        
        print(f"[ZoomWebhook] Participant joined: {user_name}")

    async def _handle_participant_left(self, event_data: Dict):
        """Handle participant.left event"""
        payload = event_data.get("payload", {})
        object_data = payload.get("object", {})
        
        participant = object_data.get("participant", {})
        user_name = participant.get("user_name")
        
        print(f"[ZoomWebhook] Participant left: {user_name}")