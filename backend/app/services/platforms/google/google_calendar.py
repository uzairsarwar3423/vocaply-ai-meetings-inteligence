"""
Google Calendar API
Handles Google Calendar operations
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi.concurrency import run_in_threadpool


class GoogleCalendar:
    """
    Google Calendar API client.
    
    Operations:
    - List calendar events
    - Get event details
    - Create events
    - Detect Google Meet links
    """

    def __init__(self, platform_connection):
        self.connection = platform_connection

    async def _get_service(self):
        """Get Google Calendar API service"""
        from app.services.platforms.google.google_oauth import GoogleOAuth
        
        oauth = GoogleOAuth(self.connection)
        credentials = await oauth.get_credentials()
        
        return build("calendar", "v3", credentials=credentials)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # EVENTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def list_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_results: int = 100,
    ) -> List[Dict]:
        """
        List calendar events.
        
        Args:
            start_time: Start time filter (default: now)
            end_time: End time filter (default: now + 7 days)
            max_results: Maximum events to return
        
        Returns:
            List of calendar event dicts
        """
        service = await self._get_service()
        
        # Default time range: next 7 days
        if not start_time:
            start_time = datetime.utcnow()
        
        if not end_time:
            end_time = start_time + timedelta(days=7)
        
        # Format as RFC3339
        time_min = start_time.isoformat() + "Z"
        time_max = end_time.isoformat() + "Z"
        
        try:
            request = service.events().list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            events_result = await run_in_threadpool(request.execute)
            
            events = events_result.get("items", [])
            
            # Enrich events with Google Meet detection
            for event in events:
                event["has_meet_link"] = self._has_google_meet_link(event)
                event["meet_url"] = self._extract_meet_url(event)
            
            return events
            
        except HttpError as e:
            print(f"[GoogleCalendar] Error listing events: {e}")
            raise

    async def get_event(self, event_id: str) -> Dict:
        """
        Get calendar event by ID.
        
        Args:
            event_id: Google Calendar event ID
        
        Returns:
            Event dict
        """
        service = await self._get_service()
        
        try:
            request = service.events().get(
                calendarId="primary",
                eventId=event_id,
            )
            event = await run_in_threadpool(request.execute)
            
            # Enrich with Meet link detection
            event["has_meet_link"] = self._has_google_meet_link(event)
            event["meet_url"] = self._extract_meet_url(event)
            
            return event
            
        except HttpError as e:
            print(f"[GoogleCalendar] Error getting event: {e}")
            raise

    async def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        add_meet_link: bool = True,
    ) -> Dict:
        """
        Create a calendar event.
        
        Args:
            summary: Event title
            start_time: Start time
            end_time: End time
            description: Event description
            location: Event location
            attendees: List of attendee emails
            add_meet_link: Add Google Meet conference link
        
        Returns:
            Created event dict
        """
        service = await self._get_service()
        
        event = {
            "summary": summary,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC",
            },
        }
        
        if description:
            event["description"] = description
        
        if location:
            event["location"] = location
        
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]
        
        # Add Google Meet conference
        if add_meet_link:
            event["conferenceData"] = {
                "createRequest": {
                    "requestId": f"meet-{start_time.timestamp()}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            }
        
        try:
            request = service.events().insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1 if add_meet_link else 0,
            )
            created_event = await run_in_threadpool(request.execute)
            
            return created_event
            
        except HttpError as e:
            print(f"[GoogleCalendar] Error creating event: {e}")
            raise

    async def update_event(
        self,
        event_id: str,
        updates: Dict,
    ) -> Dict:
        """Update calendar event"""
        service = await self._get_service()
        
        try:
            # Get existing event
            request = service.events().get(
                calendarId="primary",
                eventId=event_id,
            )
            event = await run_in_threadpool(request.execute)
            
            # Apply updates
            event.update(updates)
            
            # Update event
            request = service.events().update(
                calendarId="primary",
                eventId=event_id,
                body=event,
            )
            updated_event = await run_in_threadpool(request.execute)
            
            return updated_event
            
        except HttpError as e:
            print(f"[GoogleCalendar] Error updating event: {e}")
            raise

    async def delete_event(self, event_id: str) -> bool:
        """Delete calendar event"""
        service = await self._get_service()
        
        try:
            request = service.events().delete(
                calendarId="primary",
                eventId=event_id,
            )
            await run_in_threadpool(request.execute)
            
            return True
            
        except HttpError as e:
            print(f"[GoogleCalendar] Error deleting event: {e}")
            return False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MEET LINK DETECTION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _has_google_meet_link(self, event: Dict) -> bool:
        """Check if event has Google Meet link"""
        # Check conferenceData
        if event.get("conferenceData"):
            entry_points = event["conferenceData"].get("entryPoints", [])
            for entry in entry_points:
                if entry.get("entryPointType") == "video":
                    return True
        
        # Check description/location for Meet URL
        text = f"{event.get('description', '')} {event.get('location', '')}"
        return "meet.google.com" in text.lower()

    def _extract_meet_url(self, event: Dict) -> Optional[str]:
        """Extract Google Meet URL from event"""
        # From conferenceData
        if event.get("conferenceData"):
            entry_points = event["conferenceData"].get("entryPoints", [])
            for entry in entry_points:
                if entry.get("entryPointType") == "video":
                    return entry.get("uri")
        
        # From description/location (regex)
        text = f"{event.get('description', '')} {event.get('location', '')}"
        match = re.search(
            r'https?://meet\.google\.com/[a-z]{3}-[a-z]{4}-[a-z]{3}',
            text,
            re.IGNORECASE
        )
        
        if match:
            return match.group(0)
        
        return None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WEBHOOKS (Push Notifications)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def setup_push_notifications(
        self,
        webhook_url: str,
        channel_id: str,
    ) -> Dict:
        """
        Set up push notifications for calendar changes.
        
        Args:
            webhook_url: Your webhook endpoint
            channel_id: Unique channel identifier
        
        Returns:
            Channel info dict
        """
        service = await self._get_service()
        
        try:
            request = service.events().watch(
                calendarId="primary",
                body={
                    "id": channel_id,
                    "type": "web_hook",
                    "address": webhook_url,
                }
            )
            channel = await run_in_threadpool(request.execute)
            
            return channel
            
        except HttpError as e:
            print(f"[GoogleCalendar] Error setting up push notifications: {e}")
            raise

    async def stop_push_notifications(
        self,
        channel_id: str,
        resource_id: str,
    ) -> bool:
        """Stop push notifications"""
        service = await self._get_service()
        
        try:
            request = service.channels().stop(
                body={
                    "id": channel_id,
                    "resourceId": resource_id,
                }
            )
            await run_in_threadpool(request.execute)
            
            return True
            
        except HttpError as e:
            print(f"[GoogleCalendar] Error stopping push notifications: {e}")
            return False