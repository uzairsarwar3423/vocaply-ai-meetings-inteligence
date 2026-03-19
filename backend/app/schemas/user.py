from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
import uuid

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: Optional[str] = "member"

class UserCreate(UserBase):
    email: EmailStr
    password: str
    company_name: str  # For initial registration

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: uuid.UUID
    company_id: uuid.UUID
    is_email_verified: bool
    avatar_url: Optional[str] = None
    preferences: dict = {"theme": "system", "language": "en", "auto_join_meetings": False}
    notification_settings: dict = {"email_alerts": True, "push_notifications": True, "meeting_reminders": True}
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class User(UserInDBBase):
    pass

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserPreferencesUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    auto_join_meetings: Optional[bool] = None

class NotificationSettingsUpdate(BaseModel):
    email_alerts: Optional[bool] = None
    push_notifications: Optional[bool] = None
    meeting_reminders: Optional[bool] = None

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class UserInDB(UserInDBBase):
    password_hash: str
