from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.repositories import user_repo, company_repo, session_repo
from app.repositories.company_repository import CompanyCreate
from app.repositories.session_repository import SessionCreate
from app.schemas.user import UserCreate
from app.schemas.auth import Login, TokenRefresh
from app.schemas.token import Token
from app.utils.password import verify_password, verify_password_async
from app.utils.jwt import create_access_token, create_refresh_token, decode_token
from app.core.config import settings

class AuthService:
    def register_user(self, db: Session, *, user_in: UserCreate):
        # Check if user exists
        user = user_repo.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
        
        # Create company
        slug = user_in.company_name.lower().replace(" ", "-")
        # Ensure slug unique (simplified)
        company = company_repo.get_by_slug(db, slug=slug)
        if company:
            slug = f"{slug}-{datetime.now().timestamp()}"
            
        company = company_repo.create(db, obj_in=CompanyCreate(name=user_in.company_name, slug=slug))
        
        # Create user
        user = user_repo.create(db, obj_in=user_in, company_id=company.id)
        return user

    def authenticate(self, db: Session, *, login_data: Login):
        user = user_repo.get_by_email(db, email=login_data.email)
        if not user:
            return None
        if not verify_password(login_data.password, user.password_hash):
            return None
        return user

    def create_tokens_for_user(self, db: Session, *, user_id: Union[str, uuid.UUID], user_agent: str = None, ip_address: str = None) -> Token:
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        
        # Save session
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        session_repo.create(db, obj_in=SessionCreate(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        ))
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def refresh_token(self, db: Session, *, refresh_in: TokenRefresh) -> Token:
        # Verify refresh token in DB
        session = session_repo.get_by_refresh_token(db, refresh_token=refresh_in.refresh_token)
        if not session or session.is_revoked or session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        
        # Create new tokens
        access_token = create_access_token(subject=session.user_id)
        new_refresh_token = create_refresh_token(subject=session.user_id)
        
        # Invalidate old session and create new one
        session_repo.update(db, db_obj=session, obj_in={"is_revoked": True})
        
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        session_repo.create(db, obj_in=SessionCreate(
            user_id=session.user_id,
            refresh_token=new_refresh_token,
            expires_at=expires_at,
            user_agent=session.user_agent,
            ip_address=session.ip_address
        ))
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token
        )

    def logout(self, db: Session, *, refresh_token: str):
        session = session_repo.get_by_refresh_token(db, refresh_token=refresh_token)
        if session:
            session_repo.update(db, db_obj=session, obj_in={"is_revoked": True})

    # ============================================
    # ASYNC METHODS (for FastAPI async endpoints)
    # ============================================

    async def authenticate_async(self, db: AsyncSession, *, login_data: Login) -> Optional[User]:
        """Async user authentication with non-blocking password verification"""
        stmt = select(User).where(User.email == login_data.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Use async password verification to avoid blocking
        if not await verify_password_async(login_data.password, user.password_hash):
            return None
        
        return user

    async def create_tokens_for_user_async(
        self, 
        db: AsyncSession, 
        *, 
        user_id: Union[str, uuid.UUID], 
        user_agent: str = None, 
        ip_address: str = None
    ) -> Token:
        """Async token creation"""
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        
        # Save session (using async repository)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        from app.models.user_session import UserSession
        
        session = UserSession(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            is_revoked=False
        )
        db.add(session)
        await db.commit()
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

auth_service = AuthService()
