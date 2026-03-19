"""
Zoom API
Handles Zoom meeting management and reporting.
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.services.platforms.zoom.zoom_oauth import ZoomOAuth
from app.models.platform_connection import PlatformConnection


class ZoomAPI:
    """
    Zoom-specific API client for meeting management.
    """

    def __init__(self, connection: PlatformConnection):
        self.connection = connection
        self.oauth = ZoomOAuth(connection)

    async def list_upcoming_meetings(self) -> List[Dict]:
        """
        List user's upcoming Zoom meetings.
        """
        # Delegating to OAuth client which already has request logic
        meetings = await self.oauth.list_meetings()
        # Sort by start_time
        return sorted(meetings, key=lambda x: x.get("start_time", ""))

    async def get_meeting_details(self, meeting_id: str) -> Dict:
        """
        Get details for a specific Zoom meeting.
        """
        return await self.oauth.get_meeting(meeting_id)

    async def schedule_meeting(
        self,
        topic: str,
        start_time: datetime,
        duration_minutes: int,
        timezone: str = "UTC",
        password: Optional[str] = None,
        agenda: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Schedule a new Zoom meeting.
        """
        meeting_settings = {
            "timezone": timezone,
            "password": password,
            "agenda": agenda,
        }
        meeting_settings.update(kwargs)
        
        return await self.oauth.create_meeting(
            topic=topic,
            start_time=start_time,
            duration_minutes=duration_minutes,
            **meeting_settings
        )

    async def delete_meeting(self, meeting_id: str) -> None:
        """
        Delete a Zoom meeting.
        """
        await self.oauth._make_request("DELETE", f"/meetings/{meeting_id}")
