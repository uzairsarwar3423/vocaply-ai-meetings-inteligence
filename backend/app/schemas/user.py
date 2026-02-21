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
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    password_hash: str
