"""
Google Meet API
Handles Google Meet meeting operations
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, List

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi.concurrency import run_in_threadpool


class GoogleMeet:
    """
    Google Meet API client.
    
    Note: Google Meet doesn't have a dedicated REST API.
    Meetings are created via Calendar API with conferenceData.
    """

    def __init__(self, platform_connection):
        self.connection = platform_connection

    async def _get_calendar_service(self):
        """Get Google Calendar API service"""
        from app.services.platforms.google.google_oauth import GoogleOAuth
        
        oauth = GoogleOAuth(self.connection)
        credentials = await oauth.get_credentials()
        
        return build("calendar", "v3", credentials=credentials)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MEETINGS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def create_meeting(
        self,
        topic: str,
        start_time: datetime,
        duration_minutes: int,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
    ) -> Dict:
        """
        Create a Google Meet meeting.
        
        This creates a Calendar event with a Google Meet conference attached.
        
        Args:
            topic: Meeting title
            start_time: Meeting start time
            duration_minutes: Meeting duration
            description: Meeting description
            attendees: List of attendee emails
        
        Returns:
            Calendar event dict with Meet link
        """
        service = await self._get_calendar_service()
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        event = {
            "summary": topic,
            "description": description or "",
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC",
            },
            "conferenceData": {
                "createRequest": {
                    "requestId": f"meet-{start_time.timestamp()}",
                    "conferenceSolutionKey": {
                        "type": "hangoutsMeet"
                    },
                }
            },
        }
        
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]
        
        try:
            request = service.events().insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1,  # Required for conferenceData
                sendUpdates="all",  # Send invites to attendees
            )
            created_event = await run_in_threadpool(request.execute)
            
            return self._format_meeting_response(created_event)
            
        except HttpError as e:
            print(f"[GoogleMeet] Error creating meeting: {e}")
            raise

    async def get_meeting(self, event_id: str) -> Dict:
        """
        Get Google Meet meeting details.
        
        Args:
            event_id: Calendar event ID
        
        Returns:
            Meeting dict
        """
        service = await self._get_calendar_service()
        
        try:
            request = service.events().get(
                calendarId="primary",
                eventId=event_id,
            )
            event = await run_in_threadpool(request.execute)
            
            return self._format_meeting_response(event)
            
        except HttpError as e:
            print(f"[GoogleMeet] Error getting meeting: {e}")
            raise

    async def list_upcoming_meetings(self) -> List[Dict]:
        """
        List upcoming Google Meet meetings.
        
        Returns:
            List of meetings with Meet links
        """
        service = await self._get_calendar_service()
        
        now = datetime.utcnow()
        time_min = now.isoformat() + "Z"
        time_max = (now + timedelta(days=7)).isoformat() + "Z"
        
        try:
            request = service.events().list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            events_result = await run_in_threadpool(request.execute)
            
            events = events_result.get("items", [])
            
            # Filter for events with Google Meet links
            meetings = []
            for event in events:
                if self._has_meet_link(event):
                    meetings.append(self._format_meeting_response(event))
            
            return meetings
            
        except HttpError as e:
            print(f"[GoogleMeet] Error listing meetings: {e}")
            raise

    async def add_meet_to_event(self, event_id: str) -> Dict:
        """
        Add Google Meet link to existing calendar event.
        
        Args:
            event_id: Calendar event ID
        
        Returns:
            Updated event dict
        """
        service = await self._get_calendar_service()
        
        try:
            # Get existing event
            request = service.events().get(
                calendarId="primary",
                eventId=event_id,
            )
            event = await run_in_threadpool(request.execute)
            
            # Add conferenceData if not present
            if not event.get("conferenceData"):
                event["conferenceData"] = {
                    "createRequest": {
                        "requestId": f"meet-{datetime.utcnow().timestamp()}",
                        "conferenceSolutionKey": {
                            "type": "hangoutsMeet"
                        },
                    }
                }
                
                # Update event
                request = service.events().update(
                    calendarId="primary",
                    eventId=event_id,
                    body=event,
                    conferenceDataVersion=1,
                )
                updated_event = await run_in_threadpool(request.execute)
                
                return self._format_meeting_response(updated_event)
            
            return self._format_meeting_response(event)
            
        except HttpError as e:
            print(f"[GoogleMeet] Error adding Meet link: {e}")
            raise

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HELPERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _has_meet_link(self, event: Dict) -> bool:
        """Check if event has Google Meet link"""
        if event.get("conferenceData"):
            entry_points = event["conferenceData"].get("entryPoints", [])
            return any(ep.get("entryPointType") == "video" for ep in entry_points)
        return False

    def _extract_meet_url(self, event: Dict) -> Optional[str]:
        """Extract Google Meet URL from event"""
        if event.get("conferenceData"):
            entry_points = event["conferenceData"].get("entryPoints", [])
            for entry in entry_points:
                if entry.get("entryPointType") == "video":
                    return entry.get("uri")
        return None

    def _format_meeting_response(self, event: Dict) -> Dict:
        """Format calendar event as meeting response"""
        meet_url = self._extract_meet_url(event)
        
        # Parse times
        start = event["start"].get("dateTime") or event["start"].get("date")
        end = event["end"].get("dateTime") or event["end"].get("date")
        
        return {
            "id": event["id"],
            "event_id": event["id"],
            "topic": event.get("summary", "Untitled Meeting"),
            "description": event.get("description"),
            "start_time": start,
            "end_time": end,
            "meet_url": meet_url,
            "join_url": meet_url,
            "has_meet_link": meet_url is not None,
            "status": event.get("status"),
            "creator": event.get("creator"),
            "organizer": event.get("organizer"),
            "attendees": event.get("attendees", []),
            "html_link": event.get("htmlLink"),
            "raw_event": event,
        }