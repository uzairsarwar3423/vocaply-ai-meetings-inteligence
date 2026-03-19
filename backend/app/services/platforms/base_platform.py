"""
Base Platform Interface
Abstract base class for platform integrations
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime


class BasePlatform(ABC):
    """
    Abstract base class for platform integrations.
    
    All platform integrations (Zoom, Google, Microsoft) should inherit
    from this class and implement the required methods.
    """

    def __init__(self, platform_connection):
        self.connection = platform_connection

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # OAUTH
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @abstractmethod
    async def refresh_access_token(self) -> str:
        """
        Refresh access token using refresh token.
        
        Returns:
            New access token
        """
        pass

    @abstractmethod
    def get_oauth_url(self, state: str, redirect_uri: str) -> str:
        """
        Get OAuth authorization URL.
        
        Args:
            state: CSRF protection state
            redirect_uri: Callback URL
        
        Returns:
            Authorization URL
        """
        pass

    @abstractmethod
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code
            redirect_uri: Callback URL
        
        Returns:
            Token response dict
        """
        pass

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MEETINGS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @abstractmethod
    async def list_meetings(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        List user's meetings.
        
        Args:
            start_time: Filter by start time
            end_time: Filter by end time
        
        Returns:
            List of meeting dicts
        """
        pass

    @abstractmethod
    async def get_meeting(self, meeting_id: str) -> Dict:
        """
        Get meeting details.
        
        Args:
            meeting_id: Platform meeting ID
        
        Returns:
            Meeting dict
        """
        pass

    @abstractmethod
    async def create_meeting(
        self,
        topic: str,
        start_time: datetime,
        duration_minutes: int,
        **kwargs
    ) -> Dict:
        """
        Create a new meeting.
        
        Args:
            topic: Meeting title
            start_time: Meeting start time
            duration_minutes: Meeting duration
            **kwargs: Platform-specific options
        
        Returns:
            Created meeting dict
        """
        pass

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # USER INFO
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @abstractmethod
    async def get_user_info(self) -> Dict:
        """
        Get authenticated user's profile.
        
        Returns:
            User profile dict
        """
        pass

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WEBHOOKS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @abstractmethod
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature.
        
        Args:
            payload: Webhook payload bytes
            signature: Signature header
        
        Returns:
            True if valid, False otherwise
        """
        pass

    @abstractmethod
    async def handle_webhook_event(self, event: Dict):
        """
        Handle webhook event.
        
        Args:
            event: Webhook event dict
        """
        pass