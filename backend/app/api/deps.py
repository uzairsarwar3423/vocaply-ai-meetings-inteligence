from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db, get_async_db
from app.models.user import User
from app.repositories import user_repo
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True, "leeway": 60}
        )
        token_data = TokenPayload(**payload)
    except (JWTError, Exception) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if token_data.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_repo.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
    
get_current_active_user = get_current_user

def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    # Basic role check if needed, but the current schema has a 'role' string
    if current_user.role != "owner" and current_user.role != "admin":
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

# ============================================
# ASYNC DEPENDENCY FUNCTIONS
# ============================================

async def get_current_user_async(
    db: AsyncSession = Depends(get_async_db), token: str = Depends(reusable_oauth2)
) -> User:
    print(f"DEBUG: token = {token[:10]}...")
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True, "leeway": 60}
        )
        token_data = TokenPayload(**payload)
    except (JWTError, Exception) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if token_data.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = select(User).where(User.id == token_data.sub)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
    
get_current_active_user_async = get_current_user_async

async def get_current_active_superuser_async(
    current_user: User = Depends(get_current_user_async),
) -> User:
    """Async version of get_current_active_superuser"""
    if current_user.role != "owner" and current_user.role != "admin":
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
