from sqlalchemy import Column, String, Boolean, ForeignKey, TIMESTAMP, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_email_verified = Column(Boolean, nullable=False, server_default='false')
    email_verification_token = Column(String(255), nullable=True, unique=True)
    
    # Password Reset
    password_reset_token = Column(String(255), nullable=True, unique=True)
    password_reset_expires = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Profile
    full_name = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # Role & Permissions
    role = Column(String(50), nullable=False, server_default='member')
    
    # Status
    is_active = Column(Boolean, nullable=False, server_default='true')
    last_login_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Settings & Preferences
    preferences = Column(JSON, nullable=False, server_default='{"theme": "system", "language": "en", "auto_join_meetings": false}')
    notification_settings = Column(JSON, nullable=False, server_default='{"email_alerts": true, "push_notifications": true, "meeting_reminders": true}')
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="creator", lazy="dynamic")
    platform_connections = relationship("PlatformConnection", back_populates="user", cascade="all, delete-orphan")
