"""
Zoom OAuth
Handles Zoom OAuth 2.0 flow and token management
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Dict
from urllib.parse import urlencode

import httpx
from app.core.config import settings
from app.services.platforms.base_platform import BasePlatform


class ZoomOAuth(BasePlatform):
    """
    Zoom OAuth 2.0 implementation.
    
    OAuth Flow:
    1. Redirect to Zoom authorization URL
    2. User grants permission
    3. Zoom redirects to callback with code
    4. Exchange code for access token
    5. Store tokens securely
    """

    # Zoom OAuth endpoints
    AUTH_URL = "https://zoom.us/oauth/authorize"
    TOKEN_URL = "https://zoom.us/oauth/token"
    API_BASE = "https://api.zoom.us/v2"

    # Required OAuth scopes (You must add these Granular Scopes in your Zoom Marketplace App Settings under "Scopes")
    SCOPES = [
        # Base/Classic scopes
        "meeting:read",
        "meeting:write",
        "user:read",
        "webhook:read",
        
        # REQUIRED Granular Scopes for API v2
        "meeting:read:list_meetings",    # Required for GET /users/me/meetings
        "meeting:read:meeting",          # Required for GET /meetings/{meetingId}
        "meeting:write:meeting",         # Required for POST /users/me/meetings and DELETE
        "user:read:user",                # Required for GET /users/me
    ]

    def __init__(self, platform_connection=None):
        super().__init__(platform_connection)
        
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # OAUTH FLOW
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_oauth_url(self, state: str, redirect_uri: str) -> str:
        """Generate Zoom OAuth authorization URL"""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": state,
        }
        
        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.TOKEN_URL,
                auth=(self.client_id, self.client_secret),
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )
            
            if not response.is_success:
                print("ZOOM TOKEN API ERROR:", response.status_code, response.text)
            response.raise_for_status()
            return response.json()

    async def refresh_access_token(self) -> str:
        """Refresh access token using refresh token"""
        refresh_token = self.connection.get_refresh_token()
        
        if not refresh_token:
            raise ValueError("No refresh token available")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.TOKEN_URL,
                auth=(self.client_id, self.client_secret),
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )
            
            if not response.is_success:
                print("ZOOM REFRESH TOKEN API ERROR:", response.status_code, response.text)
            response.raise_for_status()
            data = response.json()
            
            # Update stored tokens
            access_token = data["access_token"]
            self.connection.set_access_token(access_token)
            self.connection.token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=data.get("expires_in", 3600)
            )
            
            return access_token

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # API REQUESTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict:
        """Make authenticated API request"""
        # Refresh token if expired
        if self.connection.is_token_expired:
            await self.refresh_access_token()

        access_token = self.connection.get_access_token()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method,
                f"{self.API_BASE}{endpoint}",
                headers={"Authorization": f"Bearer {access_token}"},
                **kwargs
            )
            
            if not response.is_success:
                print("ZOOM API ERROR:", response.status_code, response.text)
            response.raise_for_status()
            return response.json()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # USER INFO
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def get_user_info(self) -> Dict:
        """Get authenticated user's profile"""
        return await self._make_request("GET", "/users/me")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MEETINGS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def list_meetings(self, start_time=None, end_time=None):
        """List user's Zoom meetings"""
        data = await self._make_request("GET", "/users/me/meetings")
        return data.get("meetings", [])

    async def get_meeting(self, meeting_id: str) -> Dict:
        """Get Zoom meeting details"""
        return await self._make_request("GET", f"/meetings/{meeting_id}")

    async def create_meeting(
        self,
        topic: str,
        start_time: datetime,
        duration_minutes: int,
        **kwargs
    ) -> Dict:
        """Create a new Zoom meeting"""
        payload = {
            "topic": topic,
            "type": 2,  # Scheduled meeting
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration": duration_minutes,
            "timezone": "UTC",
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": True,
                "waiting_room": False,
                "audio": "both",
                "auto_recording": "none",
            },
        }
        
        payload.update(kwargs)
        
        return await self._make_request(
            "POST",
            "/users/me/meetings",
            json=payload
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WEBHOOKS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify Zoom webhook signature"""
        import hmac
        import hashlib

        webhook_secret = settings.ZOOM_WEBHOOK_SECRET or ""
        
        expected = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)

    async def handle_webhook_event(self, event: Dict):
        """Handle Zoom webhook event"""
        event_type = event.get("event")
        
        # Meeting started - auto-create bot session
        if event_type == "meeting.started":
            await self._on_meeting_started(event)
        
        # Meeting ended - finalize recordings
        elif event_type == "meeting.ended":
            await self._on_meeting_ended(event)

    async def _on_meeting_started(self, event: Dict):
        """Handle meeting started event"""
        meeting_data = event.get("payload", {}).get("object", {})
        meeting_id = meeting_data.get("id")
        
        print(f"[Zoom] Meeting started: {meeting_id}")
        # TODO: Auto-create bot session

    async def _on_meeting_ended(self, event: Dict):
        """Handle meeting ended event"""
        meeting_data = event.get("payload", {}).get("object", {})
        meeting_id = meeting_data.get("id")
        
        print(f"[Zoom] Meeting ended: {meeting_id}")