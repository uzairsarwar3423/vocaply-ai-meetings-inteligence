"""
Slack OAuth
Handles Slack OAuth 2.0 flow for bot installation
"""

import os
from typing import Dict
from urllib.parse import urlencode

import httpx


class SlackOAuth:
    """
    Slack OAuth 2.0 implementation.
    
    Supports:
    - Bot token installation
    - User token installation
    - Token refresh
    """

    # Slack OAuth endpoints
    AUTH_URL = "https://slack.com/oauth/v2/authorize"
    TOKEN_URL = "https://slack.com/api/oauth.v2.access"

    # Required bot scopes
    BOT_SCOPES = [
        "chat:write",           # Send messages
        "chat:write.public",    # Send to any channel
        "im:write",             # Send DMs
        "users:read",           # Read user info
        "users:read.email",     # Read user emails
        "channels:read",        # Read channel list
        "groups:read",          # Read private channels
        "commands",             # Slash commands
        "app_mentions:read",    # @mentions
    ]

    # User scopes (optional)
    USER_SCOPES = [
        "identity.basic",
        "identity.email",
    ]

    def __init__(self):
        self.client_id = os.getenv("SLACK_CLIENT_ID")
        self.client_secret = os.getenv("SLACK_CLIENT_SECRET")
        self.signing_secret = os.getenv("SLACK_SIGNING_SECRET")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # OAUTH FLOW
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_oauth_url(self, state: str, redirect_uri: str) -> str:
        """Generate Slack OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "scope": ",".join(self.BOT_SCOPES),
            "redirect_uri": redirect_uri,
            "state": state,
        }
        
        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )
            
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok"):
                raise ValueError(f"Slack OAuth error: {data.get('error')}")
            
            return data

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # VERIFICATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def verify_signature(
        self,
        timestamp: str,
        body: bytes,
        signature: str
    ) -> bool:
        """
        Verify Slack request signature.
        
        Slack signs all requests with your signing secret.
        This prevents replay attacks and ensures authenticity.
        """
        import hmac
        import hashlib
        import time

        # Check timestamp is recent (within 5 minutes)
        current_time = int(time.time())
        if abs(current_time - int(timestamp)) > 60 * 5:
            return False

        # Compute signature
        sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
        computed_sig = "v0=" + hmac.new(
            self.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()

        # Compare signatures (constant-time comparison)
        return hmac.compare_digest(computed_sig, signature)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TOKEN MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def extract_tokens(self, oauth_response: Dict) -> Dict:
        """
        Extract relevant token information from OAuth response.
        
        Returns:
            {
                "bot_token": "xoxb-...",
                "team_id": "T...",
                "team_name": "...",
                "bot_user_id": "U...",
                "app_id": "A...",
            }
        """
        return {
            "bot_token": oauth_response["access_token"],
            "team_id": oauth_response["team"]["id"],
            "team_name": oauth_response["team"]["name"],
            "bot_user_id": oauth_response.get("bot_user_id"),
            "app_id": oauth_response.get("app_id"),
            "scope": oauth_response.get("scope"),
            "token_type": oauth_response.get("token_type"),
        }