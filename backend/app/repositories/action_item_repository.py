"""
Action Item Repository
Vocaply Platform - Day 10: Action Item Extraction Logic
File: backend/app/repositories/action_item_repository.py

All database operations for action items (read, write, filter, paginate).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.action_item import ActionItem, ActionItemStatus
from app.schemas.pagination import PaginationParams


class ActionItemRepository:
    """Handles all action item database operations"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ============================================
    # CREATE
    # ============================================

    async def create(self, action_item: ActionItem) -> ActionItem:
        """Create a new action item"""
        self.db.add(action_item)
        await self.db.commit()
        await self.db.refresh(action_item)
        return action_item

    async def bulk_create(self, items: List[ActionItem]) -> int:
        """Bulk insert action items and return count saved"""
        if not items:
            return 0
        self.db.add_all(items)
        await self.db.commit()
        return len(items)

    # ============================================
    # READ – single
    # ============================================

    async def get_by_id(
        self,
        item_id:    uuid.UUID,
        company_id: str,
    ) -> Optional[ActionItem]:
        """Get a single action item by id (company-scoped)"""
        stmt = select(ActionItem).where(
            and_(
                ActionItem.id         == item_id,
                ActionItem.company_id == company_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ============================================
    # READ – lists
    # ============================================

    async def list_by_meeting(
        self,
        meeting_id: uuid.UUID,
        company_id: Optional[uuid.UUID | str] = None,
    ) -> List[ActionItem]:
        """Get all action items for a meeting (ordered by creation time)"""
        conditions = [ActionItem.meeting_id == meeting_id]
        if company_id is not None:
            conditions.append(ActionItem.company_id == str(company_id))

        stmt = (
            select(ActionItem)
            .where(and_(*conditions))
            .order_by(ActionItem.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_by_company(
        self,
        company_id:    str,
        status:        Optional[str]       = None,
        priority:      Optional[str]       = None,
        assignee_id:   Optional[str]       = None,
        meeting_id:    Optional[uuid.UUID] = None,
        due_before:    Optional[datetime]  = None,
        is_ai_generated: Optional[bool]   = None,
        pagination:    Optional[PaginationParams] = None,
        sort_by:       str = "created_at",
        sort_dir:      str = "desc",
    ) -> Tuple[List[ActionItem], int]:
        """
        Paginated list of action items across a company with rich filtering.

        Returns:
            (items, total_count)
        """
        stmt = select(ActionItem).where(ActionItem.company_id == company_id)

        # Filters
        if status:
            stmt = stmt.where(ActionItem.status == status)
        if priority:
            stmt = stmt.where(ActionItem.priority == priority)
        if assignee_id:
            stmt = stmt.where(ActionItem.assigned_to_id == assignee_id)
        if meeting_id:
            stmt = stmt.where(ActionItem.meeting_id == meeting_id)
        if due_before:
            stmt = stmt.where(ActionItem.due_date <= due_before)
        if is_ai_generated is not None:
            stmt = stmt.where(ActionItem.is_ai_generated == is_ai_generated)

        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        # Sort
        sort_col = getattr(ActionItem, sort_by, ActionItem.created_at)
        stmt = stmt.order_by(
            sort_col.desc() if sort_dir == "desc" else sort_col.asc()
        )

        # Paginate
        if pagination:
            stmt = stmt.offset(pagination.offset).limit(pagination.limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def list_by_assignee(
        self,
        assignee_id: str,
        company_id:  str,
        status:      Optional[str] = None,
    ) -> List[ActionItem]:
        """Get all action items assigned to a user"""
        stmt = select(ActionItem).where(
            and_(
                ActionItem.assigned_to_id == assignee_id,
                ActionItem.company_id     == company_id,
            )
        )
        if status:
            stmt = stmt.where(ActionItem.status == status)

        stmt = stmt.order_by(ActionItem.due_date.asc().nulls_last())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def search(
        self,
        company_id:  str,
        query:       str,
        pagination:  Optional[PaginationParams] = None,
    ) -> Tuple[List[ActionItem], int]:
        """Search action items by title or description (case-insensitive)"""
        stmt = select(ActionItem).where(
            and_(
                ActionItem.company_id == company_id,
                or_(
                    ActionItem.title.ilike(f"%{query}%"),
                    ActionItem.description.ilike(f"%{query}%"),
                ),
            )
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        if pagination:
            stmt = stmt.offset(pagination.offset).limit(pagination.limit)

        stmt = stmt.order_by(ActionItem.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_overdue(
        self,
        company_id: str,
    ) -> List[ActionItem]:
        """Return all non-completed items past their due date."""
        now = datetime.now(tz=timezone.utc)
        stmt = select(ActionItem).where(
            and_(
                ActionItem.company_id == company_id,
                ActionItem.due_date   <= now,
                ActionItem.status.notin_([
                    ActionItemStatus.COMPLETED.value,
                    ActionItemStatus.CANCELLED.value,
                ]),
            )
        ).order_by(ActionItem.due_date.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ============================================
    # UPDATE
    # ============================================

    async def update(self, item: ActionItem) -> ActionItem:
        """Persist an in-memory ActionItem change to the database."""
        item.updated_at = datetime.now(tz=timezone.utc)
        if (
            item.status == ActionItemStatus.COMPLETED.value
            and not item.completed_at
        ):
            item.completed_at = datetime.now(tz=timezone.utc)
        elif item.status != ActionItemStatus.COMPLETED.value:
            item.completed_at = None

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def accept(
        self,
        item:       ActionItem,
        user_id:    Optional[str] = None,
    ) -> ActionItem:
        """
        Accept an AI-generated action item.
        Keeps it in 'pending' status but locks in the assignee.
        Optionally records who accepted it in meta_data.
        """
        item.updated_at = datetime.now(tz=timezone.utc)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def reject(
        self,
        item:    ActionItem,
        user_id: Optional[str] = None,
    ) -> ActionItem:
        """Mark an action item as cancelled (rejected)."""
        item.status     = ActionItemStatus.CANCELLED.value
        item.updated_at = datetime.now(tz=timezone.utc)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def bulk_update_status(
        self,
        item_ids:   List[uuid.UUID],
        company_id: str,
        status:     str,
    ) -> int:
        """Bulk-update all items matching the ids to a new status."""
        stmt = (
            update(ActionItem)
            .where(
                and_(
                    ActionItem.id.in_(item_ids),
                    ActionItem.company_id == company_id,
                )
            )
            .values(
                status     = status,
                updated_at = datetime.now(tz=timezone.utc),
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    # ============================================
    # DELETE
    # ============================================

    async def delete(
        self,
        item_id:    uuid.UUID,
        company_id: str,
    ) -> bool:
        """Hard-delete an action item. Returns True if a row was deleted."""
        stmt = delete(ActionItem).where(
            and_(
                ActionItem.id         == item_id,
                ActionItem.company_id == company_id,
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def delete_by_meeting(
        self,
        meeting_id: uuid.UUID,
        company_id: str,
    ) -> int:
        """Delete all action items for a meeting (used during re-analysis)."""
        stmt = delete(ActionItem).where(
            and_(
                ActionItem.meeting_id == meeting_id,
                ActionItem.company_id == company_id,
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    # ============================================
    # STATISTICS
    # ============================================

    async def get_stats(
        self,
        company_id: str,
        meeting_id: Optional[uuid.UUID] = None,
    ) -> dict:
        """Return aggregate stats for action items."""
        conds = [ActionItem.company_id == company_id]
        if meeting_id:
            conds.append(ActionItem.meeting_id == meeting_id)

        base = select(ActionItem).where(and_(*conds))

        total_result = await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()

        status_rows = await self.db.execute(
            select(ActionItem.status, func.count(ActionItem.id))
            .where(and_(*conds))
            .group_by(ActionItem.status)
        )
        by_status = {row[0]: row[1] for row in status_rows.all()}

        priority_rows = await self.db.execute(
            select(ActionItem.priority, func.count(ActionItem.id))
            .where(and_(*conds))
            .group_by(ActionItem.priority)
        )
        by_priority = {row[0]: row[1] for row in priority_rows.all()}

        return {
            "total":       total,
            "by_status":   by_status,
            "by_priority": by_priority,
        }
