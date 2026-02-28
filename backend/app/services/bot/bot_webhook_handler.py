"""
Bot Webhook Handler
Processes webhook events from bot service
"""

from datetime import datetime
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.bot_session import BotSession
from app.models.meeting import Meeting, MeetingStatus
from app.workers.transcription_worker import transcribe_meeting_task
from app.services.realtime.broadcast_service import broadcast_to_meeting


class BotWebhookHandler:
    """
    Handles webhook events from bot service.
    
    Events:
    - bot.joined: Bot successfully joined meeting
    - bot.left: Bot left meeting
    - bot.error: Bot encountered error
    - bot.recording.started: Recording started
    - recording.completed: Recording uploaded
    - participant.joined: Participant joined
    - participant.left: Participant left
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def handle_event(self, event_data: Dict[str, Any]):
        """
        Handle webhook event.
        
        Args:
            event_data: {
                "event_type": "bot.joined",
                "bot_id": "...",
                "meeting_id": "...",
                "company_id": "...",
                "timestamp": "...",
                "data": {...}
            }
        """
        event_type = event_data.get("event_type")
        meeting_id = event_data.get("meeting_id")
        
        if not event_type or not meeting_id:
            print("[BotWebhook] Invalid event data")
            return
        
        print(f"[BotWebhook] Handling {event_type} for meeting {meeting_id}")
        
        # Route to handler
        handlers = {
            "bot.joined": self._handle_bot_joined,
            "bot.left": self._handle_bot_left,
            "bot.error": self._handle_bot_error,
            "bot.recording.started": self._handle_recording_started,
            "recording.completed": self._handle_recording_completed,
            "participant.joined": self._handle_participant_joined,
            "participant.left": self._handle_participant_left,
            "participant.count_changed": self._handle_participant_count_changed,
        }
        
        handler = handlers.get(event_type)
        
        if handler:
            await handler(meeting_id, event_data.get("data", {}))
        else:
            print(f"[BotWebhook] Unknown event type: {event_type}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # EVENT HANDLERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _handle_bot_joined(self, meeting_id: str, data: dict):
        """Handle bot joined event"""
        bot_session = await self._get_bot_session(meeting_id)
        
        if bot_session:
            bot_session.status = "in_meeting"
            bot_session.joined_at = datetime.utcnow()
            
            # Update meeting
            meeting = bot_session.meeting
            if meeting:
                meeting.bot_status = "in_meeting"
                meeting.bot_joined_at = bot_session.joined_at
            
            await self.db.commit()
        
        # Broadcast update
        await broadcast_to_meeting(meeting_id, {
            "type": "bot.joined",
            "data": {
                "status": "in_meeting",
                "joined_at": datetime.utcnow().isoformat(),
            },
        })

    async def _handle_bot_left(self, meeting_id: str, data: dict):
        """Handle bot left event"""
        bot_session = await self._get_bot_session(meeting_id)
        
        if bot_session:
            bot_session.status = "completed"
            bot_session.left_at = datetime.utcnow()
            
            # Calculate duration
            if bot_session.joined_at:
                duration = (bot_session.left_at - bot_session.joined_at).total_seconds()
                bot_session.recording_duration = duration
            
            # Update meeting
            meeting = bot_session.meeting
            if meeting:
                meeting.bot_status = "completed"
            
            await self.db.commit()
        
        # Broadcast update
        await broadcast_to_meeting(meeting_id, {
            "type": "bot.left",
            "data": {
                "status": "completed",
                "left_at": datetime.utcnow().isoformat(),
            },
        })

    async def _handle_bot_error(self, meeting_id: str, data: dict):
        """Handle bot error event"""
        bot_session = await self._get_bot_session(meeting_id)
        
        if bot_session:
            bot_session.status = "failed"
            bot_session.error = data.get("error", "Unknown error")
            bot_session.retry_count += 1
            
            # Update meeting
            meeting = bot_session.meeting
            if meeting:
                meeting.bot_status = "failed"
            
            await self.db.commit()
        
        # Broadcast update
        await broadcast_to_meeting(meeting_id, {
            "type": "bot.error",
            "data": {
                "status": "failed",
                "error": data.get("error"),
            },
        })

    async def _handle_recording_started(self, meeting_id: str, data: dict):
        """Handle recording started event"""
        bot_session = await self._get_bot_session(meeting_id)
        
        if bot_session:
            bot_session.status = "recording"
            bot_session.recording_started = datetime.utcnow()
            await self.db.commit()
        
        # Broadcast update
        await broadcast_to_meeting(meeting_id, {
            "type": "recording.started",
            "data": {
                "status": "recording",
                "started_at": datetime.utcnow().isoformat(),
            },
        })

    async def _handle_recording_completed(self, meeting_id: str, data: dict):
        """
        Handle recording completed event.
        
        Triggers transcription job.
        """
        bot_session = await self._get_bot_session(meeting_id)
        
        if bot_session:
            bot_session.recording_completed = datetime.utcnow()
            bot_session.recording_url = data.get("recording_url")
            
            # Store audio info
            audio_info = data.get("audio_info", {})
            if audio_info:
                bot_session.bot_metadata = bot_session.bot_metadata or {}
                bot_session.bot_metadata["audio_info"] = audio_info
            
            # Update meeting
            meeting = bot_session.meeting
            if meeting:
                meeting.recording_url = data.get("recording_url")
                meeting.status = MeetingStatus.TRANSCRIBING
            
            await self.db.commit()
            
            # Trigger transcription
            if meeting and meeting.recording_url:
                print(f"[BotWebhook] Triggering transcription for meeting {meeting_id}")
                
                transcribe_meeting_task.delay(
                    meeting_id=str(meeting_id),
                    recording_url=meeting.recording_url,
                    language="en",  # TODO: detect language
                )
        
        # Broadcast update
        await broadcast_to_meeting(meeting_id, {
            "type": "recording.completed",
            "data": {
                "recording_url": data.get("recording_url"),
                "audio_info": data.get("audio_info", {}),
            },
        })

    async def _handle_participant_joined(self, meeting_id: str, data: dict):
        """Handle participant joined event"""
        # Update participant count
        bot_session = await self._get_bot_session(meeting_id)
        
        if bot_session:
            bot_session.participant_count = data.get("current_count", bot_session.participant_count + 1)
            bot_session.is_alone = bot_session.participant_count <= 1
            
            if not bot_session.is_alone:
                bot_session.alone_since = None
            
            await self.db.commit()
        
        # Broadcast update
        await broadcast_to_meeting(meeting_id, {
            "type": "participant.joined",
            "data": data,
        })

    async def _handle_participant_left(self, meeting_id: str, data: dict):
        """Handle participant left event"""
        bot_session = await self._get_bot_session(meeting_id)
        
        if bot_session:
            bot_session.participant_count = data.get("current_count", bot_session.participant_count - 1)
            bot_session.is_alone = bot_session.participant_count <= 1
            
            if bot_session.is_alone and not bot_session.alone_since:
                bot_session.alone_since = datetime.utcnow()
            
            await self.db.commit()
        
        # Broadcast update
        await broadcast_to_meeting(meeting_id, {
            "type": "participant.left",
            "data": data,
        })

    async def _handle_participant_count_changed(self, meeting_id: str, data: dict):
        """Handle participant count change"""
        bot_session = await self._get_bot_session(meeting_id)
        
        if bot_session:
            count = data.get("current_count", 0)
            bot_session.participant_count = count
            bot_session.is_alone = count <= 1
            await self.db.commit()
        
        # Broadcast update
        await broadcast_to_meeting(meeting_id, {
            "type": "participant.count_changed",
            "data": data,
        })

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HELPERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _get_bot_session(self, meeting_id: str) -> BotSession:
        """Get bot session for meeting"""
        stmt = select(BotSession).where(BotSession.meeting_id == meeting_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()