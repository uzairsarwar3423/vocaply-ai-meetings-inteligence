"""
Calendar Sync Service
Syncs calendar events from Google Calendar and Outlook
"""

from datetime import datetime, timedelta
from typing import List, Optional
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.models.calendar_event import CalendarEvent
from app.models.user import User
from app.services.calendar.meeting_detector import MeetingDetector


class CalendarSyncService:
    """
    Syncs calendar events from external providers.
    
    Supports:
    - Google Calendar
    - Microsoft Outlook (via Microsoft Graph API)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # GOOGLE CALENDAR
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def sync_google_calendar(
        self,
        user_id: str,
        access_token: str,
        days_ahead: int = 7,
    ) -> int:
        """
        Sync Google Calendar events.
        
        Args:
            user_id: User ID
            access_token: Google OAuth access token
            days_ahead: Number of days to sync ahead
        
        Returns:
            Number of events synced
        """
        # Get user
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one()

        # Build Google Calendar API client
        credentials = Credentials(token=access_token)
        service = build('calendar', 'v3', credentials=credentials)

        # Get events
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'

        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        synced_count = 0

        for event in events:
            await self._process_google_event(user, event)
            synced_count += 1

        await self.db.commit()
        return synced_count

    async def _process_google_event(self, user: User, event: dict):
        """Process a single Google Calendar event"""
        external_id = event.get('id')

        # Check if already exists
        stmt = select(CalendarEvent).where(
            and_(
                CalendarEvent.user_id == user.id,
                CalendarEvent.external_event_id == external_id,
                CalendarEvent.calendar_provider == 'google'
            )
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        # Parse event data
        start = event.get('start', {})
        end = event.get('end', {})
        
        start_time = self._parse_datetime(start.get('dateTime') or start.get('date'))
        end_time = self._parse_datetime(end.get('dateTime') or end.get('date'))
        
        title = event.get('summary', 'Untitled Event')
        description = event.get('description', '')
        location = event.get('location', '')

        # Detect meeting URL
        meeting_info = MeetingDetector.detect_from_event(title, description, location)

        if existing:
            # Update existing
            existing.title = title
            existing.description = description
            existing.location = location
            existing.start_time = start_time
            existing.end_time = end_time
            existing.has_meeting_url = meeting_info is not None
            existing.meeting_url = meeting_info.url if meeting_info else None
            existing.meeting_platform = meeting_info.platform if meeting_info else None
            existing.last_synced_at = datetime.utcnow()
            existing.sync_version += 1
        else:
            # Create new
            calendar_event = CalendarEvent(
                user_id=user.id,
                company_id=user.company_id,
                calendar_provider='google',
                external_event_id=external_id,
                title=title,
                description=description,
                location=location,
                start_time=start_time,
                end_time=end_time,
                timezone=start.get('timeZone'),
                all_day='date' in start,
                has_meeting_url=meeting_info is not None,
                meeting_url=meeting_info.url if meeting_info else None,
                meeting_platform=meeting_info.platform if meeting_info else None,
                raw_event_data=event,
                attendees=event.get('attendees'),
                organizer=event.get('organizer'),
            )
            self.db.add(calendar_event)

    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parse datetime from ISO format"""
        if 'T' in dt_str:
            # DateTime
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        else:
            # Date only
            return datetime.fromisoformat(dt_str + 'T00:00:00+00:00')

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CLEANUP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def cleanup_old_events(self, days_old: int = 30) -> int:
        """Delete calendar events older than N days"""
        cutoff = datetime.utcnow() - timedelta(days=days_old)

        stmt = select(CalendarEvent).where(CalendarEvent.end_time < cutoff)
        result = await self.db.execute(stmt)
        events = result.scalars().all()

        count = len(events)
        for event in events:
            await self.db.delete(event)

        await self.db.commit()
        return count