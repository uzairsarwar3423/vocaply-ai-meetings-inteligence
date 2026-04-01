"""
Notifications API
Vocaply Platform - Day 26: Notifications & Reminders

Endpoints:
  GET    /notifications               List paginated notifications
  GET    /notifications/unread-count  Unread count
  POST   /notifications/{id}/read     Mark single as read
  POST   /notifications/read-all      Mark all as read
"""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_async_db
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import (
    MarkReadResponse,
    NotificationListItem,
    NotificationResponse,
    UnreadCountResponse,
)
from app.schemas.pagination import OffsetPaginationMeta, PaginatedResponse

router = APIRouter(tags=["Notifications"])


# ── Dependency ──────────────────────────────────────────────────────

async def get_repo(db: AsyncSession = Depends(get_async_db)) -> NotificationRepository:
    return NotificationRepository(db)


# ============================================
# GET /notifications/unread-count
# (must be registered BEFORE /{id} routes)
# ============================================

@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
    summary="Get unread notification count",
)
async def get_unread_count(
    current_user = Depends(get_current_user),
    repo: NotificationRepository = Depends(get_repo),
):
    count = await repo.get_unread_count(user_id=str(current_user.id))
    return UnreadCountResponse(count=count)


# ============================================
# GET /notifications
# ============================================

@router.get(
    "",
    response_model=PaginatedResponse[NotificationListItem],
    summary="List notifications for the current user",
)
async def list_notifications(
    page:        int  = Query(default=1, ge=1),
    per_page:    int  = Query(default=20, ge=1, le=100),
    unread_only: bool = Query(default=False),
    current_user = Depends(get_current_user),
    repo: NotificationRepository = Depends(get_repo),
):
    skip = (page - 1) * per_page
    items, total = await repo.list_for_user(
        user_id     = str(current_user.id),
        company_id  = str(current_user.company_id),
        skip        = skip,
        limit       = per_page,
        unread_only = unread_only,
    )
    return PaginatedResponse[NotificationListItem](
        data       = [NotificationListItem.model_validate(n) for n in items],
        pagination = OffsetPaginationMeta.create(
            page        = page,
            per_page    = per_page,
            total_items = total,
        ),
    )


# ============================================
# POST /notifications/read-all
# (must be before /{id} routes to avoid conflict)
# ============================================

@router.post(
    "/read-all",
    response_model=MarkReadResponse,
    summary="Mark all notifications as read",
)
async def mark_all_read(
    current_user = Depends(get_current_user),
    repo: NotificationRepository = Depends(get_repo),
):
    count = await repo.mark_all_as_read(user_id=str(current_user.id))
    return MarkReadResponse(
        success = True,
        message = f"Marked {count} notification(s) as read.",
    )


# ============================================
# POST /notifications/{id}/read
# ============================================

@router.post(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark a single notification as read",
)
async def mark_single_read(
    notification_id: uuid.UUID,
    current_user = Depends(get_current_user),
    repo: NotificationRepository = Depends(get_repo),
):
    notification = await repo.mark_as_read(
        notification_id = notification_id,
        user_id         = str(current_user.id),
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found.",
        )
    return NotificationResponse.model_validate(notification)
