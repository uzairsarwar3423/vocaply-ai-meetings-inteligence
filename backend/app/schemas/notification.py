"""
Notification Schemas
Vocaply Platform - Day 26: Notifications & Reminders

Pydantic models for request/response serialization.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


# ============================================
# BASE / SHARED
# ============================================

class NotificationBase(BaseModel):
    type:  str
    title: str
    body:  Optional[str] = None


# ============================================
# READ MODELS
# ============================================

class NotificationResponse(NotificationBase):
    """Full notification record returned to the client."""
    id:            uuid.UUID
    user_id:       str
    company_id:    str
    is_read:       bool
    read_at:       Optional[datetime]
    metadata_:     Optional[Dict[str, Any]] = None
    sent_channels: List[str]               = []
    scheduled_at:  Optional[datetime]      = None
    sent_at:       Optional[datetime]      = None
    created_at:    datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class NotificationListItem(BaseModel):
    """Lightweight row for paginated lists."""
    id:         uuid.UUID
    type:       str
    title:      str
    body:       Optional[str]
    is_read:    bool
    metadata_:  Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


# ============================================
# COUNT / UTILITY
# ============================================

class UnreadCountResponse(BaseModel):
    count: int


class MarkReadResponse(BaseModel):
    success: bool
    message: str


# ============================================
# PREFERENCES (mirrors User.notification_settings JSON)
# ============================================

class NotificationPreferences(BaseModel):
    email_alerts:        bool = True
    push_notifications:  bool = True
    meeting_reminders:   bool = True
    slack_notifications: bool = False
