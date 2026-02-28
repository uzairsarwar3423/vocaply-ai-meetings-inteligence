"""
Meeting Controller
Orchestrates Zoom meeting lifecycle
"""

import asyncio
from typing import Optional
from datetime import datetime, timedelta

from bot.zoom_sdk_wrapper import create_sdk, MeetingStatus
from bot.auth_service import ZoomAuthService
from bot.audio_handler import AudioHandler, AudioCallback
from bot.participant_tracker import ParticipantTracker
from bot.event_handler import ZoomEventHandler
from config.zoom_config import settings


class MeetingController:
    """
    Controls a single Zoom meeting session.
    
    Lifecycle:
    1. Initialize SDK
    2. Generate JWT token
    3. Join meeting
    4. Start audio capture
    5. Monitor participants
    6. Leave when done
    """

    def __init__(self, meeting_id: str, meeting_url: str):
        self.meeting_id = meeting_id
        self.meeting_url = meeting_url
        
        # Services
        self.sdk = create_sdk(use_mock=False)
        self.auth = ZoomAuthService()
        self.audio = AudioHandler(meeting_id)
        self.participants = ParticipantTracker(meeting_id)
        self.events = ZoomEventHandler(meeting_id, self.participants, self.audio)
        
        # State
        self.joined_at: Optional[datetime] = None
        self.left_at: Optional[datetime] = None
        self.is_running = False
        
        # Monitoring task
        self._monitor_task: Optional[asyncio.Task] = None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start(self):
        """Initialize and join meeting"""
        print(f"[Bot] Starting for meeting {self.meeting_id}")
        
        # Initialize SDK
        if not self.sdk.initialize():
            raise RuntimeError("Failed to initialize Zoom SDK")
        
        # Extract meeting info
        meeting_number = self.auth.extract_meeting_number(self.meeting_url)
        password = self.auth.extract_password(self.meeting_url)
        
        # Generate JWT token
        jwt_token = self.auth.generate_sdk_jwt(meeting_number, role=0)
        
        # Register SDK callbacks
        self._register_callbacks()
        
        # Join meeting
        result = self.sdk.join_meeting(
            meeting_number=meeting_number,
            display_name=settings.BOT_NAME,
            password=password,
            jwt_token=jwt_token,
        )
        
        if result != 0:  # ZoomSDKError.SUCCESS
            raise RuntimeError(f"Failed to join meeting: {result}")
        
        self.is_running = True
        self.joined_at = datetime.utcnow()
        
        # Wait for meeting to connect
        await self._wait_for_connection()
        
        # Configure bot
        await self._configure_bot()
        
        # Start audio capture
        await self.audio.start()
        
        # Start monitoring
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        
        print(f"[Bot] Successfully joined meeting {self.meeting_id}")

    async def stop(self):
        """Leave meeting and cleanup"""
        if not self.is_running:
            return
        
        print(f"[Bot] Stopping for meeting {self.meeting_id}")
        
        self.is_running = False
        
        # Stop monitoring
        if self._monitor_task:
            self._monitor_task.cancel()
        
        # Stop audio
        await self.audio.stop()
        
        # Leave meeting
        self.sdk.leave_meeting()
        
        # Cleanup SDK
        self.sdk.cleanup()
        
        self.left_at = datetime.utcnow()
        
        print(f"[Bot] Stopped")

    async def _wait_for_connection(self, timeout: int = 60):
        """Wait for meeting to connect"""
        start = datetime.utcnow()
        
        while (datetime.utcnow() - start).total_seconds() < timeout:
            status = self.sdk.get_meeting_status()
            
            if status == MeetingStatus.INMEETING:
                return
            
            if status == MeetingStatus.FAILED:
                raise RuntimeError("Meeting connection failed")
            
            await asyncio.sleep(0.5)
        
        raise TimeoutError("Timeout waiting for meeting connection")

    async def _configure_bot(self):
        """Configure bot settings"""
        # Join audio
        if settings.AUTO_JOIN_AUDIO:
            self.sdk.start_audio()
        
        # Mute audio
        if settings.AUTO_MUTE:
            self.sdk.mute_audio()
        
        # Hide video
        if settings.AUTO_HIDE_VIDEO:
            self.sdk.hide_video()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CALLBACKS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _register_callbacks(self):
        """Register SDK callbacks"""
        # Meeting events
        self.sdk.register_callback("meeting_status_changed", self.events.on_meeting_status_changed)
        
        # Participant events
        self.sdk.register_callback("user_join", self.events.on_user_join)
        self.sdk.register_callback("user_leave", self.events.on_user_leave)
        
        # Audio events
        self.sdk.register_callback("user_audio_status_change", self.events.on_user_audio_status_change)
        
        # Audio data callback
        audio_callback = AudioCallback(self.audio)
        self.sdk.register_callback("mixed_audio_raw_data", audio_callback.on_mixed_audio_raw_data_received)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MONITORING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _monitor_loop(self):
        """Background monitoring loop"""
        alone_since: Optional[datetime] = None
        
        while self.is_running:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Get participant count
                count = self.sdk.get_participant_count()
                
                # Check if bot is alone (only bot in meeting)
                if count <= 1:
                    if not alone_since:
                        alone_since = datetime.utcnow()
                        print(f"[Bot] Alone in meeting")
                    
                    # Check timeout
                    if (datetime.utcnow() - alone_since).total_seconds() > settings.ALONE_TIMEOUT:
                        print(f"[Bot] Alone timeout exceeded, leaving")
                        await self.stop()
                        return
                else:
                    alone_since = None
                
                # Check max duration
                if self.joined_at:
                    duration = (datetime.utcnow() - self.joined_at).total_seconds()
                    if duration > settings.MAX_MEETING_DURATION:
                        print(f"[Bot] Max duration exceeded, leaving")
                        await self.stop()
                        return
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Monitor] Error: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stats(self) -> dict:
        """Get meeting statistics"""
        duration = 0
        if self.joined_at:
            end = self.left_at or datetime.utcnow()
            duration = (end - self.joined_at).total_seconds()
        
        return {
            "meeting_id": self.meeting_id,
            "is_running": self.is_running,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "left_at": self.left_at.isoformat() if self.left_at else None,
            "duration_seconds": duration,
            "participants": self.participants.get_stats(),
            "audio": self.audio.get_stats(),
            "events": self.events.get_stats(),
        }