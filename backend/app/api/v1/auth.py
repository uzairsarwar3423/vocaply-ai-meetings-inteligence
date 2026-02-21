from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.services import auth_service
from app.schemas import user as user_schema
from app.schemas import auth as auth_schema
from app.schemas import token as token_schema
from app.db.session import get_db

router = APIRouter()

@router.post("/register", response_model=user_schema.User)
def register(
    user_in: user_schema.UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user and company.
    """
    return auth_service.register_user(db, user_in=user_in)

@router.post("/login", response_model=token_schema.Token)
def login(
    request: Request,
    login_data: auth_schema.Login,
    db: Session = Depends(get_db)
) -> Any:
    """
    Login user and return tokens.
    """
    user = auth_service.authenticate(db, login_data=login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host
    
    return auth_service.create_tokens_for_user(
        db, user_id=user.id, user_agent=user_agent, ip_address=ip_address
    )

@router.post("/refresh", response_model=token_schema.Token)
def refresh_token(
    refresh_in: auth_schema.TokenRefresh,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token.
    """
    return auth_service.refresh_token(db, refresh_in=refresh_in)

@router.post("/logout", response_model=auth_schema.Msg)
def logout(
    refresh_in: auth_schema.TokenRefresh,
    db: Session = Depends(get_db)
) -> Any:
    """
    Logout user (invalidate refresh token).
    """
    auth_service.logout(db, refresh_token=refresh_in.refresh_token)
    return {"msg": "Successfully logged out"}

@router.get("/me", response_model=user_schema.User)
def read_user_me(
    current_user: deps.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

# Placeholder for verification and password reset (logic needs mail service)
@router.post("/verify-email", response_model=auth_schema.Msg)
def verify_email(token: str) -> Any:
    return {"msg": "Email verification logic not implemented yet"}

@router.post("/forgot-password", response_model=auth_schema.Msg)
def forgot_password(email_in: auth_schema.ForgotPassword) -> Any:
    return {"msg": "Password reset email logic not implemented yet"}

@router.post("/reset-password", response_model=auth_schema.Msg)
def reset_password(reset_in: auth_schema.ResetPassword) -> Any:
    return {"msg": "Password reset logic not implemented yet"}
