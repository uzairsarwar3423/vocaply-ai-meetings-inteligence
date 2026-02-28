"""
Zoom Auth Service
Generates JWT tokens for Zoom Meeting SDK authentication
"""

import time
import base64
from typing import Dict
import jwt

from config.zoom_config import settings


class ZoomAuthService:
    """
    Generates JWT tokens for Zoom Meeting SDK.
    
    Token format required by Zoom:
    {
      "appKey": "sdk_key",
      "iat": issued_at_timestamp,
      "exp": expiration_timestamp,
      "tokenExp": expiration_timestamp
    }
    """

    def __init__(self):
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET
        
        if not self.client_id or not self.client_secret:
            raise ValueError("ZOOM_CLIENT_ID and ZOOM_CLIENT_SECRET must be set")

    def generate_sdk_jwt(self, meeting_number: str, role: int = 0) -> str:
        """
        Generate JWT for Zoom Meeting SDK.
        
        Args:
            meeting_number: Zoom meeting number (not the join URL)
            role: 0 = participant, 1 = host
        
        Returns:
            JWT token string
        """
        now = int(time.time())
        exp = now + settings.JWT_EXPIRATION
        
        payload = {
            "appKey": self.client_id,
            "sdkKey": self.client_id,
            "mn": meeting_number,  # Meeting number
            "role": role,
            "iat": now,
            "exp": exp,
            "tokenExp": exp,
        }
        
        token = jwt.encode(
            payload,
            self.client_secret,
            algorithm=settings.JWT_ALGORITHM,
        )
        
        return token

    def generate_signature(self, meeting_number: str, role: int = 0) -> str:
        """
        Alternative: Generate signature for SDK (legacy method).
        Modern SDK uses JWT, but this is kept for compatibility.
        """
        timestamp = int(time.time() * 1000) - 30000  # 30 seconds ago
        
        message = f"{self.client_id}{meeting_number}{timestamp}{role}"
        
        # HMAC SHA-256
        import hmac
        import hashlib
        
        signature = hmac.new(
            self.client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Base64 encode
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return signature_b64

    def extract_meeting_number(self, meeting_url: str) -> str:
        """
        Extract meeting number from Zoom URL.
        
        Examples:
        - https://zoom.us/j/1234567890 → 1234567890
        - https://zoom.us/j/1234567890?pwd=abc → 1234567890
        """
        import re
        
        # Match meeting number in URL
        match = re.search(r'/j/(\d+)', meeting_url)
        if match:
            return match.group(1)
        
        # Direct number
        if meeting_url.isdigit():
            return meeting_url
        
        raise ValueError(f"Could not extract meeting number from: {meeting_url}")

    def extract_password(self, meeting_url: str) -> str:
        """
        Extract meeting password from URL.
        
        Example:
        - https://zoom.us/j/123?pwd=abc123 → abc123
        """
        import re
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(meeting_url)
        query_params = parse_qs(parsed.query)
        
        # Check pwd parameter
        if 'pwd' in query_params:
            return query_params['pwd'][0]
        
        return ""

    def validate_token(self, token: str) -> Dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.client_secret,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")