import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import settings
from app.models.user import User
from app.repositories import user_repo, session_repo
from app.schemas.token import Token
from app.utils.jwt import create_access_token, create_refresh_token
from app.repositories.session_repository import SessionCreate

class GoogleOAuthService:
    """Handle Google OAuth2 flow and token management"""
    
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_AUTH_REDIRECT_URI
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange Google authorization code for access and refresh tokens.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.GOOGLE_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get Google user information using access token.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.GOOGLE_USER_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def handle_google_oauth_callback(
        self, 
        db: AsyncSession, 
        code: str,
        user_agent: str = None,
        ip_address: str = None
    ) -> tuple[Token, User]:
        """
        Complete OAuth flow: exchange code for tokens, get user info, 
        create/update user, and return app tokens.
        """
        # Exchange code for Google tokens
        google_tokens = await self.exchange_code_for_tokens(code)
        
        # Get Google user info
        google_user = await self.get_google_user_info(google_tokens["access_token"])
        
        # Find or create user in our system
        user_email = google_user.get("email")
        from sqlalchemy import select
        stmt = select(User).where(User.email == user_email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user from Google info
            from app.schemas.user import UserCreate
            from app.models.company import Company
            
            # Create a default company for social users
            company_name = f"{google_user.get('given_name', 'User')}'s Team"
            slug = company_name.lower().replace(" ", "-")
            
            # Ensure slug uniqueness (simple check)
            from sqlalchemy import select
            stmt = select(Company).where(Company.slug == slug)
            res = await db.execute(stmt)
            if res.scalar_one_or_none():
                slug = f"{slug}-{int(datetime.now().timestamp())}"
            
            company = Company(name=company_name, slug=slug)
            db.add(company)
            await db.commit()
            await db.refresh(company)
            
            # Create user
            user_data = UserCreate(
                email=user_email,
                full_name=google_user.get("name", ""),
                password="", # OAuth users don't have passwords
                company_name=company_name,
            )
            # Create dummy password
            from app.utils.password import get_password_hash_async
            dummy_password = str(UUID(int=0)) # Or any random string
            user_password_hash = await get_password_hash_async(dummy_password)
            
            user = User(
                email=user_email,
                password_hash=user_password_hash,
                full_name=google_user.get("name", ""),
                company_id=company.id,
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # Create app tokens for the user
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        # Save session
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        from app.models.user_session import UserSession
        session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            is_revoked=False
        )
        db.add(session)
        await db.commit()
        
        app_token = Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        return app_token, user

google_oauth_service = GoogleOAuthService()
