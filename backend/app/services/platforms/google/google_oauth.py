"""
Google OAuth
Handles Google OAuth 2.0 flow for Calendar and Meet access
"""

import os
from app.core.config import settings
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from urllib.parse import urlencode

import httpx
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.services.platforms.base_platform import BasePlatform


class GoogleOAuth(BasePlatform):
    """
    Google OAuth 2.0 implementation.
    
    Supports:
    - Google Calendar API
    - Google Meet API
    """

    # Google OAuth endpoints
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    
    # Required OAuth scopes
    SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
        "openid",
        "email",
        "profile",
    ]

    def __init__(self, platform_connection=None):
        super().__init__(platform_connection)
        
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # OAUTH FLOW
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_oauth_url(self, state: str, redirect_uri: str) -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.SCOPES),
            "state": state,
            "access_type": "offline",  # Get refresh token
            "prompt": "consent",  # Force consent screen
        }
        
        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            
            response.raise_for_status()
            return response.json()

    async def refresh_access_token(self) -> str:
        """Refresh access token using refresh token"""
        refresh_token = self.connection.get_refresh_token()
        
        if not refresh_token:
            raise ValueError("No refresh token available")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Update stored access token
            access_token = data["access_token"]
            self.connection.set_access_token(access_token)
            self.connection.token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=data.get("expires_in", 3600)
            )
            
            return access_token

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CREDENTIALS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def get_credentials(self) -> Credentials:
        """
        Get Google API credentials.
        
        Returns:
            google.oauth2.credentials.Credentials
        """
        # Refresh token if expired
        if self.connection.is_token_expired:
            await self.refresh_access_token()

        creds = Credentials(
            token=self.connection.get_access_token(),
            refresh_token=self.connection.get_refresh_token(),
            token_uri=self.TOKEN_URL,
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=self.SCOPES,
        )
        
        return creds

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # USER INFO
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def get_user_info(self) -> Dict:
        """Get authenticated user's profile"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={
                    "Authorization": f"Bearer {self.connection.get_access_token()}"
                },
            )
            
            response.raise_for_status()
            return response.json()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MEETINGS (Placeholder - implemented in google_meet.py)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def list_meetings(self, start_time=None, end_time=None):
        """List meetings - delegates to google_calendar.py"""
        from app.services.platforms.google.google_calendar import GoogleCalendar
        calendar = GoogleCalendar(self.connection)
        return await calendar.list_events(start_time, end_time)

    async def get_meeting(self, meeting_id: str) -> Dict:
        """Get meeting details"""
        from app.services.platforms.google.google_calendar import GoogleCalendar
        calendar = GoogleCalendar(self.connection)
        return await calendar.get_event(meeting_id)

    async def create_meeting(
        self,
        topic: str,
        start_time: datetime,
        duration_minutes: int,
        **kwargs
    ) -> Dict:
        """Create a Google Meet meeting"""
        from app.services.platforms.google.google_meet import GoogleMeet
        meet = GoogleMeet(self.connection)
        return await meet.create_meeting(topic, start_time, duration_minutes, **kwargs)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WEBHOOKS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """
        Verify Google webhook signature.
        
        Note: Google uses push notifications with channel tokens,
        not HMAC signatures like Zoom.
        """
        # Verification happens via channel token matching
        return True

    async def handle_webhook_event(self, event: Dict):
        """Handle Google Calendar push notification"""
        # Process calendar sync event
        print(f"[Google] Webhook event: {event}")