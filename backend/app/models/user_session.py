from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import uuid

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token = Column(String(500), nullable=False, unique=True, index=True)
    
    device_info = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String, nullable=True)
    
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    is_revoked = Column(Boolean, nullable=False, server_default='false')
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    last_used_at = Column(TIMESTAMP(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")
