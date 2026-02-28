"""
Auto-Join Scheduler
Schedules bots to auto-join meetings from calendar events
"""

from datetime import datetime, timedelta
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.calendar_event import CalendarEvent
from app.models.meeting import Meeting, MeetingStatus
from app.workers.bot_join_worker import schedule_bot_join_task


class AutoJoinScheduler:
    """
    Schedules bots to auto-join calendar events.
    
    Workflow:
    1. Find upcoming calendar events with auto-join enabled
    2. Create meeting records
    3. Schedule Celery task to start bot 2 minutes before meeting
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def schedule_upcoming_meetings(self, lookahead_minutes: int = 30) -> int:
        """
        Schedule bots for upcoming meetings.
        
        Args:
            lookahead_minutes: Look ahead this many minutes
        
        Returns:
            Number of meetings scheduled
        """
        now = datetime.utcnow()
        window_end = now + timedelta(minutes=lookahead_minutes)

        # Find events that:
        # - Have auto-join enabled
        # - Not already scheduled
        # - Not already executed
        # - Start within lookahead window
        # - Have meeting URL
        stmt = select(CalendarEvent).where(
            and_(
                CalendarEvent.auto_join_enabled == True,
                CalendarEvent.auto_join_scheduled == False,
                CalendarEvent.auto_join_executed == False,
                CalendarEvent.has_meeting_url == True,
                CalendarEvent.start_time > now,
                CalendarEvent.start_time <= window_end,
            )
        )

        result = await self.db.execute(stmt)
        events = result.scalars().all()

        scheduled_count = 0

        for event in events:
            try:
                await self._schedule_event(event)
                scheduled_count += 1
            except Exception as e:
                print(f"[AutoJoin] Failed to schedule event {event.id}: {e}")

        await self.db.commit()
        return scheduled_count

    async def _schedule_event(self, event: CalendarEvent):
        """Schedule bot for a single calendar event"""
        # Check if meeting already exists
        if not event.meeting_id:
            # Create meeting
            meeting = Meeting(
                title=event.title,
                description=event.description,
                meeting_url=event.meeting_url,
                scheduled_time=event.start_time,
                status=MeetingStatus.SCHEDULED,
                company_id=event.company_id,
                created_by_id=event.user_id,
                auto_created=True,  # Flag as auto-created
            )
            self.db.add(meeting)
            await self.db.flush()  # Get meeting.id

            event.meeting_id = meeting.id

        # Calculate when to start bot (2 minutes before meeting)
        join_time = event.start_time - timedelta(minutes=2)

        # Schedule Celery task
        eta = join_time
        schedule_bot_join_task.apply_async(
            args=[str(event.meeting_id), str(event.company_id)],
            eta=eta,
        )

        # Mark as scheduled
        event.auto_join_scheduled = True
        event.auto_join_scheduled_at = datetime.utcnow()

        print(f"[AutoJoin] Scheduled bot for meeting {event.meeting_id} at {eta}")

    async def get_scheduled_events(self, user_id: str) -> List[CalendarEvent]:
        """Get all scheduled events for a user"""
        stmt = select(CalendarEvent).where(
            and_(
                CalendarEvent.user_id == user_id,
                CalendarEvent.auto_join_scheduled == True,
                CalendarEvent.auto_join_executed == False,
            )
        ).order_by(CalendarEvent.start_time)

        result = await self.db.execute(stmt)
        return result.scalars().all()