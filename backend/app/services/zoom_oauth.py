import httpx
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.config import settings
from app.models.user import User
from app.repositories import user_repo
from app.schemas.token import Token
from app.utils.jwt import create_access_token, create_refresh_token
from app.repositories.session_repository import SessionCreate
from app.repositories import session_repo

class ZoomOAuthService:
    """Handle Zoom OAuth2 flow and token management"""
    
    ZOOM_TOKEN_URL = "https://zoom.us/oauth/token"
    ZOOM_USER_URL = "https://api.zoom.us/v2/users/me"
    
    def __init__(self):
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET
        self.redirect_uri = settings.ZOOM_REDIRECT_URI
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange Zoom authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from Zoom OAuth callback
            
        Returns:
            Dict with zoom access_token, refresh_token, expires_in, etc.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.ZOOM_TOKEN_URL,
                auth=(self.client_id, self.client_secret),
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_zoom_user_info(self, zoom_access_token: str) -> Dict[str, Any]:
        """
        Get Zoom user information using access token.
        
        Args:
            zoom_access_token: Zoom OAuth access token
            
        Returns:
            Dict with user_id, email, first_name, last_name, etc.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.ZOOM_USER_URL,
                headers={"Authorization": f"Bearer {zoom_access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def handle_zoom_oauth_callback(
        self, 
        db: AsyncSession, 
        code: str,
        user_agent: str = None,
        ip_address: str = None
    ) -> tuple[Token, User]:
        """
        Complete OAuth flow: exchange code for tokens, get user info, 
        create/update user, and return app tokens.
        
        Args:
            db: Database session
            code: Authorization code from Zoom
            user_agent: User agent from request
            ip_address: IP address from request
            
        Returns:
            Tuple of (Token dict with app access/refresh tokens, User object)
        """
        # Exchange code for Zoom tokens
        zoom_tokens = await self.exchange_code_for_tokens(code)
        
        # Get Zoom user info
        zoom_user = await self.get_zoom_user_info(zoom_tokens["access_token"])
        
        # Find or create user in our system
        user_email = zoom_user.get("email")
        user = await user_repo.get_by_email_async(db, email=user_email)
        
        if not user:
            # Create new user from Zoom info
            from app.schemas.user import UserCreate
            user_data = UserCreate(
                email=user_email,
                full_name=f"{zoom_user.get('first_name', '')} {zoom_user.get('last_name', '')}".strip(),
                password="",  # OAuth users don't have passwords
                company_name=zoom_user.get("company", "Zoom User"),
            )
            # Create a temporary password (won't be used for OAuth users)
            user_data.password = str(zoom_user.get("user_id", ""))[:32]
            user = user_repo.create(db, obj_in=user_data)
        
        # Store Zoom tokens for this user (you may want to add a zoom_integration table)
        # For now, we'll create app tokens and user should manage Zoom integration separately
        
        # Create app tokens for the user
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        # Save session
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        session_repo.create(db, obj_in=SessionCreate(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        ))
        
        app_token = Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        return app_token, user
    
    async def refresh_zoom_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh expired Zoom access token using refresh token.
        
        Args:
            refresh_token: Zoom refresh token
            
        Returns:
            Dict with new zoom access_token and expiry info
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.ZOOM_TOKEN_URL,
                auth=(self.client_id, self.client_secret),
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                }
            )
            response.raise_for_status()
            return response.json()


# Export singleton instance
zoom_oauth_service = ZoomOAuthService()
