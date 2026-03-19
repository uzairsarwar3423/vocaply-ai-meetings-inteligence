from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.repositories import user_repo
from app.schemas.token import TokenPayload
from app.utils.jwt import create_access_token, create_refresh_token, decode_token

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


def encrypt_token(token: str) -> str:
    """Encrypt a token using Fernet symmetric encryption"""
    from cryptography.fernet import Fernet
    import base64
    
    # Use SECRET_KEY to derive a valid Fernet key if ENCRYPTION_KEY is missing
    key = settings.ENCRYPTION_KEY
    if not key:
        # Fernet keys must be 32 URL-safe base64-encoded bytes
        # We'll just take the first 32 chars of SECRET_KEY and base64 it
        key = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].ljust(32, '0').encode())
    else:
        key = key.encode()
        
    f = Fernet(key)
    return f.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token using Fernet symmetric encryption"""
    from cryptography.fernet import Fernet
    import base64
    
    key = settings.ENCRYPTION_KEY
    if not key:
        key = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].ljust(32, '0').encode())
    else:
        key = key.encode()
        
    f = Fernet(key)
    return f.decrypt(encrypted_token.encode()).decode()
