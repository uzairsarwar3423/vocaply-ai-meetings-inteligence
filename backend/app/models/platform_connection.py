"""
Platform Connection Model
Stores OAuth connections to external platforms (Zoom, Google, Teams)
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column, String, DateTime, ForeignKey,
    Boolean, Text, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.core.security import encrypt_token, decrypt_token


class PlatformConnection(Base):
    """
    OAuth connection to external platform.
    
    Platforms:
    - Zoom
    - Google (Meet, Calendar)
    - Microsoft (Teams, Outlook)
    """
    __tablename__ = "platform_connections"

    # ── Primary Key ──────────────────────────────
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4()
    )

    # ── Foreign Keys ─────────────────────────────
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    company_id = Column(
        String,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # ── Platform Info ────────────────────────────
    platform = Column(String(50), nullable=False)  # zoom, google, microsoft
    platform_user_id = Column(String(255), nullable=True)  # User ID on platform
    platform_email = Column(String(255), nullable=True)  # Email on platform
    
    # ── OAuth Tokens (Encrypted) ─────────────────
    access_token_encrypted = Column(Text, nullable=False)
    refresh_token_encrypted = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # ── Status ───────────────────────────────────
    is_active = Column(Boolean, nullable=False, default=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    
    # ── Scopes & Permissions ─────────────────────
    scopes = Column(JSONB, nullable=True)  # OAuth scopes granted
    
    # ── Metadata ─────────────────────────────────
    platform_metadata = Column(JSONB, nullable=True, default=dict)
    # Store: user profile, account info, etc.
    
    # ── Timestamps ───────────────────────────────
    connected_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # ── Relationships ────────────────────────────
    user = relationship("User", back_populates="platform_connections")
    company = relationship("Company")

    # ── Indexes ──────────────────────────────────
    __table_args__ = (
        Index("idx_platform_connections_user_platform", "user_id", "platform", unique=True),
        Index("idx_platform_connections_platform", "platform"),
    )

    # ── Token Management ─────────────────────────
    
    def set_access_token(self, token: str):
        """Encrypt and store access token"""
        self.access_token_encrypted = encrypt_token(token)

    def get_access_token(self) -> str:
        """Decrypt and return access token"""
        return decrypt_token(self.access_token_encrypted)

    def set_refresh_token(self, token: str):
        """Encrypt and store refresh token"""
        self.refresh_token_encrypted = encrypt_token(token)

    def get_refresh_token(self) -> Optional[str]:
        """Decrypt and return refresh token"""
        if not self.refresh_token_encrypted:
            return None
        return decrypt_token(self.refresh_token_encrypted)

    @property
    def is_token_expired(self) -> bool:
        """Check if access token is expired"""
        if not self.token_expires_at:
            return False
        return datetime.now(timezone.utc) >= self.token_expires_at

    def __repr__(self) -> str:
        return f"<PlatformConnection platform={self.platform} user={self.user_id}>"