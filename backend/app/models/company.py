from sqlalchemy import Column, String, Boolean, JSON, TIMESTAMP, Integer, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import uuid

class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    
    # Subscription
    plan = Column(String(50), nullable=False, server_default='trial')
    subscription_status = Column(String(50), nullable=False, server_default='active')
    
    # Quotas
    meeting_quota_monthly = Column(Integer, nullable=False, server_default='25')
    meetings_used_current_month = Column(Integer, nullable=False, server_default='0')
    
    # Settings
    settings = Column(JSON, nullable=False, server_default='{}')
    timezone = Column(String(50), nullable=False, server_default='UTC')
    
    # Metadata
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="company", cascade="all, delete-orphan")
