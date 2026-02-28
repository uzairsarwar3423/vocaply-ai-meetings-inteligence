import re
from typing import Optional, NamedTuple

class MeetingInfo(NamedTuple):
    url: str
    platform: str

class MeetingDetector:
    """
    Detects meeting URLs (Zoom, Google Meet, Teams, etc.) from calendar event fields.
    """
    
    # Patterns for different meeting platforms
    PATTERNS = {
        "zoom": r"https?://(?:[a-z0-9-]+\.)?zoom\.us/(?:j|my)/[^\?\"\s]+",
        "google_meet": r"https?://meet\.google\.com/[a-z-]+",
        "teams": r"https?://teams\.microsoft\.com/l/meetup-join/[^\?\"\s]+",
        "webex": r"https?://(?:[a-z0-9-]+\.)?webex\.com/[^\?\"\s]+",
    }

    @classmethod
    def detect_from_event(cls, title: str, description: str, location: str) -> Optional[MeetingInfo]:
        """
        Scan title, description, and location for meeting URLs.
        Returns MeetingInfo if found, else None.
        """
        combined_text = f"{title}\n{location}\n{description}"
        
        for platform, pattern in cls.PATTERNS.items():
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                return MeetingInfo(url=match.group(0), platform=platform)
        
        return None
