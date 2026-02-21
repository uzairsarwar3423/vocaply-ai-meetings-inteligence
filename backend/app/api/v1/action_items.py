"""
Action Items API Router
Vocaply Platform - Day 10: Action Item Extraction Logic
File: backend/app/api/v1/action_items.py

Endpoints:
  POST   /meetings/{id}/analyze          Trigger AI extraction (background)
  GET    /action-items                   List with filtering & pagination
  GET    /action-items/{id}              Get single item
  PATCH  /action-items/{id}              Update item (manual edit)
  DELETE /action-items/{id}              Hard delete
  POST   /action-items/{id}/accept       Accept an AI-generated item
  POST   /action-items/{id}/reject       Reject (cancel) an AI-generated item
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import (
    APIRouter, BackgroundTasks, Depends, HTTPException,
    Query, status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_async_db
from app.models.action_item import ActionItem, ActionItemStatus
from app.repositories.action_item_repository import ActionItemRepository
from app.repositories.meeting_repository import MeetingRepository
from app.schemas.action_item import (
    AcceptRejectResponse,
    ActionItemListItem,
    ActionItemResponse,
    ActionItemStats,
    ActionItemUpdate,
)
from app.schemas.extraction import (
    AnalysisStatusResponse,
    AnalyzeMeetingRequest,
    ExtractionSummary,
)
from app.schemas.pagination import OffsetPaginationMeta, PaginatedResponse, PaginationParams


# ── Router instances ────────────────────────────────────────────────────────

# Mounted under /meetings/{id}/analyze in the router config
analysis_router = APIRouter(tags=["AI Analysis"])

# Mounted under /action-items
router = APIRouter(tags=["Action Items"])


# ── Dependency helpers ──────────────────────────────────────────────────────

async def get_repo(db: AsyncSession = Depends(get_async_db)) -> ActionItemRepository:
    return ActionItemRepository(db)


async def get_meeting_repo(db: AsyncSession = Depends(get_async_db)) -> MeetingRepository:
    return MeetingRepository(db)


async def _get_item_or_404(
    item_id:    uuid.UUID,
    repo:       ActionItemRepository,
    company_id: str,
) -> ActionItem:
    item = await repo.get_by_id(item_id=item_id, company_id=company_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action item {item_id} not found.",
        )
    return item


# ============================================
# TRIGGER ANALYSIS
# ============================================

@analysis_router.post(
    "/{meeting_id}/analyze",
    response_model=AnalysisStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger AI action item extraction",
    description=(
        "Queues a background Celery task that runs GPT-4o-mini on the "
        "meeting transcript to extract action items, decisions, and summaries. "
        "Returns immediately with a task_id you can poll."
    ),
)
async def analyze_meeting(
    meeting_id:   uuid.UUID,
    body:         AnalyzeMeetingRequest = None,
    background:   BackgroundTasks = BackgroundTasks(),
    current_user  = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    if body is None:
        body = AnalyzeMeetingRequest()

    # Verify the meeting exists and belongs to the user's company
    meeting_repo = MeetingRepository(db)
    meeting      = await meeting_repo.get_by_id(
        meeting_id = meeting_id,
        company_id = uuid.UUID(str(current_user.company_id)),
    )
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found.",
        )

    # Guard: don't re-run unless forced
    if meeting.ai_analysis_status == "completed" and not body.force_rerun:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This meeting has already been analyzed. "
                "Set force_rerun=true to re-extract."
            ),
        )

    # Dispatch to Celery
    try:
        from app.workers.ai_analysis_worker import analyze_meeting_task
        task = analyze_meeting_task.delay(
            meeting_id       = str(meeting_id),
            company_id       = str(current_user.company_id),
            user_id          = str(current_user.id),
            features         = body.features,
            force_rerun      = body.force_rerun,
            chunk_size_words = body.chunk_size_words,
            min_confidence   = body.min_confidence,
        )
        task_id = task.id
    except Exception as exc:
        # Celery unavailable — run inline as background task
        task_id = None

        async def _inline_extract():
            from app.services.ai.action_item_extractor import ActionItemExtractor
            extractor = ActionItemExtractor(db)
            await extractor.extract(
                meeting = meeting,
                request = body,
                user_id = str(current_user.id),
            )

        background.add_task(_inline_extract)

    return AnalysisStatusResponse(
        meeting_id        = meeting_id,
        task_id           = task_id,
        status            = "queued",
        message           = (
            "AI analysis queued. "
            "Action items will appear in GET /action-items shortly."
        ),
        estimated_seconds = 30,
    )


# ============================================
# LIST ACTION ITEMS
# ============================================

@router.get(
    "",
    response_model=PaginatedResponse[ActionItemListItem],
    summary="List action items",
    description="Get a paginated, filterable list of action items for the company.",
)
async def list_action_items(
    # Filters
    meeting_id:       Optional[uuid.UUID] = Query(None, description="Filter by meeting"),
    status_filter:    Optional[str]       = Query(None, alias="status",   description="Filter by status"),
    priority_filter:  Optional[str]       = Query(None, alias="priority", description="Filter by priority"),
    assignee_id:      Optional[str]       = Query(None, description="Filter by assigned user ID"),
    is_ai_generated:  Optional[bool]      = Query(None, description="Filter AI vs manual items"),
    # Pagination
    page:     int = Query(default=1,  ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    # Sort
    sort_by:  str = Query(default="created_at"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    # Auth
    current_user = Depends(get_current_user),
    repo:         ActionItemRepository = Depends(get_repo),
):
    pagination = PaginationParams(page=page, per_page=per_page)
    items, total = await repo.list_by_company(
        company_id      = str(current_user.company_id),
        status          = status_filter,
        priority        = priority_filter,
        assignee_id     = assignee_id,
        meeting_id      = meeting_id,
        is_ai_generated = is_ai_generated,
        pagination      = pagination,
        sort_by         = sort_by,
        sort_dir        = sort_dir,
    )

    return PaginatedResponse[ActionItemListItem](
        data       = [ActionItemListItem.model_validate(i) for i in items],
        pagination = OffsetPaginationMeta.create(
            page        = page,
            per_page    = per_page,
            total_items = total,
        ),
    )


# ============================================
# GET SINGLE ITEM
# ============================================

@router.get(
    "/{item_id}",
    response_model=ActionItemResponse,
    summary="Get a single action item",
)
async def get_action_item(
    item_id:     uuid.UUID,
    current_user = Depends(get_current_user),
    repo:        ActionItemRepository = Depends(get_repo),
):
    item = await _get_item_or_404(
        item_id    = item_id,
        repo       = repo,
        company_id = str(current_user.company_id),
    )
    return ActionItemResponse.model_validate(item)


# ============================================
# UPDATE (PATCH)
# ============================================

@router.patch(
    "/{item_id}",
    response_model=ActionItemResponse,
    summary="Update an action item",
    description="Partial update — only fields present in the body are modified.",
)
async def update_action_item(
    item_id:     uuid.UUID,
    body:        ActionItemUpdate,
    current_user = Depends(get_current_user),
    repo:        ActionItemRepository = Depends(get_repo),
):
    item = await _get_item_or_404(
        item_id    = item_id,
        repo       = repo,
        company_id = str(current_user.company_id),
    )

    # Apply only the fields that were explicitly set
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    updated = await repo.update(item)
    return ActionItemResponse.model_validate(updated)


# ============================================
# DELETE
# ============================================

@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an action item",
)
async def delete_action_item(
    item_id:     uuid.UUID,
    current_user = Depends(get_current_user),
    repo:        ActionItemRepository = Depends(get_repo),
):
    deleted = await repo.delete(
        item_id    = item_id,
        company_id = str(current_user.company_id),
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action item {item_id} not found.",
        )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# ============================================
# ACCEPT
# ============================================

@router.post(
    "/{item_id}/accept",
    response_model=AcceptRejectResponse,
    summary="Accept an AI-generated action item",
    description=(
        "Marks the item as accepted by the current user. "
        "Status remains 'pending' so it can be worked on normally."
    ),
)
async def accept_action_item(
    item_id:     uuid.UUID,
    current_user = Depends(get_current_user),
    repo:        ActionItemRepository = Depends(get_repo),
):
    item = await _get_item_or_404(
        item_id    = item_id,
        repo       = repo,
        company_id = str(current_user.company_id),
    )

    if item.status == ActionItemStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot accept a cancelled action item.",
        )

    updated = await repo.accept(item, user_id=str(current_user.id))
    return AcceptRejectResponse(
        success = True,
        message = "Action item accepted.",
        item    = ActionItemResponse.model_validate(updated),
    )


# ============================================
# REJECT
# ============================================

@router.post(
    "/{item_id}/reject",
    response_model=AcceptRejectResponse,
    summary="Reject (cancel) an AI-generated action item",
    description="Marks the item as 'cancelled'. It will no longer appear in active lists.",
)
async def reject_action_item(
    item_id:     uuid.UUID,
    current_user = Depends(get_current_user),
    repo:        ActionItemRepository = Depends(get_repo),
):
    item = await _get_item_or_404(
        item_id    = item_id,
        repo       = repo,
        company_id = str(current_user.company_id),
    )

    if item.status == ActionItemStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Action item is already cancelled.",
        )

    updated = await repo.reject(item, user_id=str(current_user.id))
    return AcceptRejectResponse(
        success = True,
        message = "Action item rejected and cancelled.",
        item    = ActionItemResponse.model_validate(updated),
    )


# ============================================
# STATS
# ============================================

@router.get(
    "/stats/summary",
    response_model=ActionItemStats,
    summary="Get action item statistics",
    description="Returns aggregate counts by status and priority for the company.",
)
async def get_action_item_stats(
    meeting_id:  Optional[uuid.UUID] = Query(None, description="Scope to a specific meeting"),
    current_user = Depends(get_current_user),
    repo:        ActionItemRepository = Depends(get_repo),
):
    return await repo.get_stats(
        company_id = str(current_user.company_id),
        meeting_id = meeting_id,
    )
