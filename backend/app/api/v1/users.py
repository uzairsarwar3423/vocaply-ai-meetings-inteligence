from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas import user as user_schema
from app.db.session import get_async_db
from app.utils.password import get_password_hash_async, verify_password_async

router = APIRouter()

@router.get("/me", response_model=user_schema.User)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user_async),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.patch("/me", response_model=user_schema.User)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_async_db),
    user_in: user_schema.UserUpdate,
    current_user: User = Depends(deps.get_current_active_user_async),
) -> Any:
    """
    Update own user profile.
    """
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.avatar_url is not None:
        # Empty string means "remove avatar"
        current_user.avatar_url = user_in.avatar_url if user_in.avatar_url else None
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.patch("/me/preferences", response_model=user_schema.User)
async def update_user_preferences(
    *,
    db: AsyncSession = Depends(get_async_db),
    preferences_in: user_schema.UserPreferencesUpdate,
    current_user: User = Depends(deps.get_current_active_user_async),
) -> Any:
    """
    Update user preferences.
    """
    # Create a copy of existing preferences to ensure proper JSONB update
    new_prefs = dict(current_user.preferences or {})
    
    if preferences_in.theme is not None:
        new_prefs["theme"] = preferences_in.theme
    if preferences_in.language is not None:
        new_prefs["language"] = preferences_in.language
    if preferences_in.auto_join_meetings is not None:
        new_prefs["auto_join_meetings"] = preferences_in.auto_join_meetings
    
    current_user.preferences = new_prefs
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.patch("/me/notifications", response_model=user_schema.User)
async def update_notification_settings(
    *,
    db: AsyncSession = Depends(get_async_db),
    notifications_in: user_schema.NotificationSettingsUpdate,
    current_user: User = Depends(deps.get_current_active_user_async),
) -> Any:
    """
    Update notification settings.
    """
    new_settings = dict(current_user.notification_settings or {})
    
    if notifications_in.email_alerts is not None:
        new_settings["email_alerts"] = notifications_in.email_alerts
    if notifications_in.push_notifications is not None:
        new_settings["push_notifications"] = notifications_in.push_notifications
    if notifications_in.meeting_reminders is not None:
        new_settings["meeting_reminders"] = notifications_in.meeting_reminders
    
    current_user.notification_settings = new_settings
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.post("/me/change-password", response_model=dict)
async def change_password(
    *,
    db: AsyncSession = Depends(get_async_db),
    password_in: user_schema.UserPasswordUpdate,
    current_user: User = Depends(deps.get_current_active_user_async),
) -> Any:
    """
    Change password.
    """
    if not await verify_password_async(password_in.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )
    
    new_password_hash = await get_password_hash_async(password_in.new_password)
    current_user.password_hash = new_password_hash
    db.add(current_user)
    await db.commit()
    
    return {"message": "Password updated successfully"}
