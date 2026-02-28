"""
Bot Scheduler
Orchestrates bot creation, monitoring, and lifecycle
"""

import asyncio
from typing import Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.bot_session import BotSession
from app.models.meeting import Meeting, MeetingStatus
from app.services.bot.bot_client import get_bot_client, BotServiceError
from app.services.realtime.broadcast_service import broadcast_to_meeting


class BotScheduler:
    """
    Manages bot lifecycle for meetings.
    
    Responsibilities:
    - Create bots for meetings
    - Monitor bot health
    - Handle bot failures
    - Retry logic
    - Real-time updates
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # BOT CREATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start_bot_for_meeting(
        self,
        meeting_id: str,
        company_id: str,
    ) -> BotSession:
        """
        Start a bot for a meeting.
        
        Steps:
        1. Create bot session record
        2. Call bot service to create bot
        3. Update meeting status
        4. Send real-time update
        
        Returns:
            BotSession instance
        
        Raises:
            BotServiceError: If bot creation fails
        """
        # Get meeting
        stmt = select(Meeting).where(Meeting.id == meeting_id)
        result = await self.db.execute(stmt)
        meeting = result.scalar_one_or_none()
        
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")
        
        # Check if bot already exists
        existing = await self._get_bot_session(meeting_id)
        if existing and existing.is_active:
            raise ValueError(f"Bot already active for meeting {meeting_id}")
        
        # Determine platform
        platform = self._detect_platform(meeting.meeting_url)
        
        # Create bot session
        bot_session = BotSession(
            meeting_id=meeting_id,
            company_id=company_id,
            bot_platform=platform,
            status="initializing",
        )
        
        self.db.add(bot_session)
        await self.db.commit()
        await self.db.refresh(bot_session)
        
        try:
            # Call bot service
            bot_client = await get_bot_client()
            
            bot_data = await bot_client.create_bot(
                meeting_url=meeting.meeting_url,
                meeting_id=str(meeting_id),
                company_id=str(company_id),
                platform=platform,
            )
            
            # Update bot session
            bot_session.bot_instance_id = bot_data.get("bot_id")
            bot_session.status = "assigned"
            bot_session.assigned_at = datetime.utcnow()
            
            # Update meeting
            meeting.bot_instance_id = bot_data.get("bot_id")
            meeting.bot_status = "assigned"
            
            await self.db.commit()
            await self.db.refresh(bot_session)
            
            # Send real-time update
            await self._broadcast_bot_update(meeting_id, {
                "status": "assigned",
                "bot_id": bot_session.bot_instance_id,
            })
            
            return bot_session
            
        except BotServiceError as e:
            # Update with error
            bot_session.status = "failed"
            bot_session.error = str(e)
            await self.db.commit()
            
            raise

    async def stop_bot_for_meeting(self, meeting_id: str) -> bool:
        """
        Stop bot for a meeting.
        
        Returns:
            True on success
        """
        bot_session = await self._get_bot_session(meeting_id)
        
        if not bot_session or not bot_session.is_active:
            return False
        
        try:
            # Call bot service
            bot_client = await get_bot_client()
            await bot_client.stop_bot(bot_session.bot_instance_id)
            
            # Update status
            bot_session.status = "leaving"
            await self.db.commit()
            
            # Send real-time update
            await self._broadcast_bot_update(meeting_id, {
                "status": "leaving",
            })
            
            return True
            
        except BotServiceError as e:
            print(f"[BotScheduler] Failed to stop bot: {e}")
            return False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # BOT MONITORING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def monitor_active_bots(self):
        """
        Monitor all active bots.
        Called periodically by Celery worker.
        """
        # Get all active bot sessions
        stmt = select(BotSession).where(
            and_(
                BotSession.status.in_(['assigned', 'joining', 'in_meeting', 'recording']),
                BotSession.bot_instance_id.isnot(None),
            )
        )
        
        result = await self.db.execute(stmt)
        bot_sessions = result.scalars().all()
        
        if not bot_sessions:
            return
        
        print(f"[BotScheduler] Monitoring {len(bot_sessions)} active bots")
        
        bot_client = await get_bot_client()
        
        for bot_session in bot_sessions:
            try:
                # Get latest status from bot service
                bot_status = await bot_client.get_bot_status(bot_session.bot_instance_id)
                
                # Update bot session
                await self._update_bot_session_from_status(bot_session, bot_status)
                
                # Check for issues
                await self._check_bot_health(bot_session)
                
            except BotServiceError as e:
                print(f"[BotScheduler] Error monitoring bot {bot_session.bot_instance_id}: {e}")
                
                # Mark as failed if can't reach
                bot_session.status = "failed"
                bot_session.error = str(e)
        
        await self.db.commit()

    async def _update_bot_session_from_status(
        self,
        bot_session: BotSession,
        bot_status: dict,
    ):
        """Update bot session from bot service status"""
        status = bot_status.get("status")
        
        if status and status != bot_session.status:
            bot_session.status = status
            
            # Update timestamps
            if status == "in_meeting" and not bot_session.joined_at:
                bot_session.joined_at = datetime.utcnow()
            elif status == "recording" and not bot_session.recording_started:
                bot_session.recording_started = datetime.utcnow()
            elif status in ["completed", "failed"]:
                bot_session.left_at = datetime.utcnow()
        
        # Update monitoring data
        bot_session.participant_count = bot_status.get("participant_count", 0)
        bot_session.is_alone = bot_session.participant_count <= 1
        bot_session.last_heartbeat = datetime.utcnow()
        
        # Send real-time update
        await self._broadcast_bot_update(str(bot_session.meeting_id), {
            "status": status,
            "participant_count": bot_session.participant_count,
            "is_alone": bot_session.is_alone,
        })

    async def _check_bot_health(self, bot_session: BotSession):
        """Check bot health and handle issues"""
        # Check stuck joining
        if bot_session.status == "joining":
            if bot_session.assigned_at:
                elapsed = (datetime.utcnow() - bot_session.assigned_at).total_seconds()
                if elapsed > 120:  # 2 minutes
                    print(f"[BotScheduler] Bot {bot_session.bot_instance_id} stuck joining")
                    bot_session.status = "failed"
                    bot_session.error = "Timeout joining meeting"
        
        # Check alone too long
        if bot_session.is_alone and bot_session.alone_since:
            elapsed = (datetime.utcnow() - bot_session.alone_since).total_seconds()
            if elapsed > 300:  # 5 minutes
                print(f"[BotScheduler] Bot {bot_session.bot_instance_id} alone too long")
                # Bot service will auto-leave, just log

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HELPERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _get_bot_session(self, meeting_id: str) -> Optional[BotSession]:
        """Get bot session for meeting"""
        stmt = select(BotSession).where(BotSession.meeting_id == meeting_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def _detect_platform(self, meeting_url: str) -> str:
        """Detect platform from meeting URL"""
        url_lower = meeting_url.lower()
        
        if "zoom.us" in url_lower:
            return "zoom"
        elif "meet.google.com" in url_lower:
            return "google_meet"
        elif "teams.microsoft.com" in url_lower or "teams.live.com" in url_lower:
            return "teams"
        else:
            # Default to Google Meet (browser automation)
            return "google_meet"

    async def _broadcast_bot_update(self, meeting_id: str, data: dict):
        """Broadcast bot update to frontend via WebSocket"""
        await broadcast_to_meeting(meeting_id, {
            "type": "bot.update",
            "data": data,
        })