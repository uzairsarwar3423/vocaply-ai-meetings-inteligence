"""
Action Item Schemas
Vocaply Platform - Day 10: Action Item Extraction Logic
File: backend/app/schemas/action_item.py

Pydantic v2-compatible schemas for action items (tasks extracted from meetings).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr, field_validator


# ============================================
# ENUMS (string literals kept for compatibility)
# ============================================

STATUS_VALUES   = ["pending", "in_progress", "completed", "cancelled"]
PRIORITY_VALUES = ["low", "medium", "high", "urgent"]


# ============================================
# BASE
# ============================================

class ActionItemBase(BaseModel):
    title:                 str   = Field(..., min_length=1, max_length=500)
    description:           Optional[str]      = None
    assignee_name:         Optional[str]      = None
    assignee_email:        Optional[EmailStr] = None
    status:                str               = Field(default="pending")
    priority:              str               = Field(default="medium")
    due_date:              Optional[datetime] = None
    is_ai_generated:       bool              = True
    confidence_score:      Optional[float]   = Field(default=None, ge=0.0, le=1.0)
    transcript_quote:      Optional[str]     = None
    transcript_start_time: Optional[float]   = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in STATUS_VALUES:
            raise ValueError(f"Invalid status '{v}'. Must be one of {STATUS_VALUES}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in PRIORITY_VALUES:
            raise ValueError(f"Invalid priority '{v}'. Must be one of {PRIORITY_VALUES}")
        return v


# ============================================
# CREATE (internal / Celery use)
# ============================================

class ActionItemCreate(ActionItemBase):
    meeting_id:     uuid.UUID
    company_id:     str
    assigned_to_id: Optional[str] = None


# ============================================
# UPDATE (PATCH body — all optional)
# ============================================

class ActionItemUpdate(BaseModel):
    title:          Optional[str]       = Field(default=None, min_length=1, max_length=500)
    description:    Optional[str]       = None
    assignee_name:  Optional[str]       = None
    assignee_email: Optional[EmailStr]  = None
    status:         Optional[str]       = None
    priority:       Optional[str]       = None
    due_date:       Optional[datetime]  = None
    assigned_to_id: Optional[str]       = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in STATUS_VALUES:
            raise ValueError(f"Invalid status '{v}'. Must be one of {STATUS_VALUES}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in PRIORITY_VALUES:
            raise ValueError(f"Invalid priority '{v}'. Must be one of {PRIORITY_VALUES}")
        return v


# ============================================
# RESPONSE — full representation
# ============================================

class ActionItemResponse(ActionItemBase):
    id:             uuid.UUID
    meeting_id:     uuid.UUID
    company_id:     str
    assigned_to_id: Optional[str]      = None
    completed_at:   Optional[datetime] = None
    created_at:     datetime
    updated_at:     datetime

    model_config = {"from_attributes": True}


# ============================================
# LIST ITEM — lighter representation for lists
# ============================================

class ActionItemListItem(BaseModel):
    id:                    uuid.UUID
    meeting_id:            uuid.UUID
    title:                 str
    assignee_name:         Optional[str]      = None
    assignee_email:        Optional[str]      = None
    status:                str
    priority:              str
    due_date:              Optional[datetime] = None
    confidence_score:      Optional[float]   = None
    is_ai_generated:       bool
    created_at:            datetime

    model_config = {"from_attributes": True}


# ============================================
# STATS
# ============================================

class ActionItemStats(BaseModel):
    total:       int
    by_status:   dict
    by_priority: dict


# ============================================
# ACCEPT / REJECT RESPONSE
# ============================================

class AcceptRejectResponse(BaseModel):
    success: bool
    message: str
    item:    ActionItemResponse
