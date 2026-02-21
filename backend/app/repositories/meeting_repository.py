"""
Meeting Repository
Vocaply Platform - Day 4
File: backend/app/repositories/meeting_repository.py

All DB access for meetings lives here.
The service layer calls this — never the API directly.
"""
from __future__ import annotations
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update, delete, func, or_, and_, desc, asc, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.meeting import Meeting, MeetingStatus, MeetingPlatform
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingPatch, MeetingSearchParams
from app.schemas.pagination import encode_cursor, decode_cursor


class MeetingRepository:
    """
    Data access layer for meetings.
    - All queries are scoped to company_id (multi-tenancy).
    - Soft deletes: deleted_at IS NULL filter applied everywhere.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==========================================
    # BASE QUERY HELPER
    # ==========================================

    def _base_query(self, company_id: UUID):
        """Base query with company_id isolation + soft-delete filter"""
        return (
            select(Meeting)
            .where(
                Meeting.company_id == company_id,
                Meeting.deleted_at.is_(None),
            )
        )

    # ==========================================
    # CREATE
    # ==========================================

    async def create(
        self,
        company_id:  UUID,
        created_by:  UUID,
        data:        MeetingCreate,
    ) -> Meeting:
        """Create a new meeting"""
        meeting = Meeting(
            company_id       = company_id,
            created_by       = created_by,
            title            = data.title,
            description      = data.description,
            meeting_url      = data.meeting_url,
            meeting_password = data.meeting_password,
            notes            = data.notes,
            platform         = data.platform.value if data.platform else None,
            platform_meeting_id = data.platform_meeting_id,
            platform_join_url   = data.platform_join_url,
            scheduled_start  = data.scheduled_start,
            scheduled_end    = data.scheduled_end,
            timezone         = data.timezone,
            attendees        = [a.dict() for a in data.attendees],
            organizer_email  = data.organizer_email,
            participant_count= len(data.attendees),
            bot_enabled      = data.bot_enabled,
            tags             = data.tags,
            meta_data        = data.meta_data,
            status           = MeetingStatus.SCHEDULED.value,
        )
        self.db.add(meeting)
        await self.db.flush()
        await self.db.commit()  # Persist to DB
        await self.db.refresh(meeting)
        return meeting

    # ==========================================
    # READ - SINGLE
    # ==========================================

    async def get_by_id(
        self,
        meeting_id: UUID,
        company_id: UUID,
    ) -> Optional[Meeting]:
        """Get single meeting by ID, scoped to company"""
        stmt = self._base_query(company_id).where(Meeting.id == meeting_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_platform_id(
        self,
        platform:           str,
        platform_meeting_id: str,
        company_id:         UUID,
    ) -> Optional[Meeting]:
        """Find meeting by platform-specific ID (e.g., Zoom meeting ID)"""
        stmt = (
            self._base_query(company_id)
            .where(
                Meeting.platform            == platform,
                Meeting.platform_meeting_id == platform_meeting_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ==========================================
    # READ - LIST (OFFSET PAGINATION)
    # ==========================================

    async def list_meetings(
        self,
        company_id:  UUID,
        page:        int  = 1,
        per_page:    int  = 20,
        sort_by:     str  = "created_at",
        sort_order:  str  = "desc",
        **filters,
    ) -> Tuple[List[Meeting], int]:
        """
        List meetings with filters + offset pagination.
        Returns (items, total_count).
        """
        stmt = self._base_query(company_id)
        stmt = self._apply_filters(stmt, **filters)

        # Count total (before pagination)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        # Apply sort
        sort_col = getattr(Meeting, sort_by, Meeting.created_at)
        stmt = stmt.order_by(
            desc(sort_col) if sort_order == "desc" else asc(sort_col)
        )

        # Apply pagination
        offset = (page - 1) * per_page
        stmt   = stmt.offset(offset).limit(per_page)

        result = await self.db.execute(stmt)
        return result.scalars().all(), total

    # ==========================================
    # READ - LIST (CURSOR PAGINATION)
    # ==========================================

    async def list_meetings_cursor(
        self,
        company_id: UUID,
        cursor:     Optional[str] = None,
        limit:      int = 20,
        direction:  str = "next",
        **filters,
    ) -> Tuple[List[Meeting], Optional[str], Optional[str]]:
        """
        Cursor-based pagination (for infinite scroll).
        Returns (items, next_cursor, prev_cursor).
        """
        stmt = self._base_query(company_id)
        stmt = self._apply_filters(stmt, **filters)
        stmt = stmt.order_by(desc(Meeting.created_at))

        if cursor:
            try:
                cursor_data = decode_cursor(cursor)
                cursor_dt   = datetime.fromisoformat(cursor_data["created_at"])
                cursor_id   = UUID(cursor_data["id"])
                if direction == "next":
                    stmt = stmt.where(
                        or_(
                            Meeting.created_at < cursor_dt,
                            and_(
                                Meeting.created_at == cursor_dt,
                                Meeting.id < cursor_id,
                            ),
                        )
                    )
                else:
                    stmt = stmt.where(
                        or_(
                            Meeting.created_at > cursor_dt,
                            and_(
                                Meeting.created_at == cursor_dt,
                                Meeting.id > cursor_id,
                            ),
                        )
                    )
            except (ValueError, KeyError):
                pass  # Invalid cursor — start from beginning

        # Fetch limit + 1 to detect if there are more
        stmt   = stmt.limit(limit + 1)
        result = await self.db.execute(stmt)
        items  = result.scalars().all()

        has_more   = len(items) > limit
        items      = items[:limit]
        next_cursor = None
        prev_cursor = None

        if has_more and items:
            last = items[-1]
            next_cursor = encode_cursor({
                "created_at": last.created_at.isoformat(),
                "id":         str(last.id),
            })

        if items and cursor:
            first = items[0]
            prev_cursor = encode_cursor({
                "created_at": first.created_at.isoformat(),
                "id":         str(first.id),
            })

        return items, next_cursor, prev_cursor

    # ==========================================
    # SEARCH (Full-text)
    # ==========================================

    async def search(
        self,
        company_id: UUID,
        params:     MeetingSearchParams,
    ) -> Tuple[List[Meeting], int]:
        """Full-text search on title + description + filters"""
        stmt = self._base_query(company_id)

        # Full-text search
        if params.q:
            search_term = params.q.strip()
            stmt = stmt.where(
                or_(
                    Meeting.title.ilike(f"%{search_term}%"),
                    Meeting.description.ilike(f"%{search_term}%"),
                    # PostgreSQL full-text search
                    func.to_tsvector("english", Meeting.title).bool_op("@@")(
                        func.plainto_tsquery("english", search_term)
                    ),
                )
            )

        # Filters
        if params.status:
            stmt = stmt.where(Meeting.status.in_([s.value for s in params.status]))
        if params.platform:
            stmt = stmt.where(Meeting.platform.in_([p.value for p in params.platform]))
        if params.date_from:
            stmt = stmt.where(Meeting.scheduled_start >= params.date_from)
        if params.date_to:
            stmt = stmt.where(Meeting.scheduled_start <= params.date_to)
        if params.created_by:
            stmt = stmt.where(Meeting.created_by == params.created_by)
        if params.has_recording is not None:
            if params.has_recording:
                stmt = stmt.where(Meeting.recording_url.isnot(None))
            else:
                stmt = stmt.where(Meeting.recording_url.is_(None))
        if params.has_transcript is not None:
            if params.has_transcript:
                stmt = stmt.where(Meeting.transcript_status == TranscriptStatus.COMPLETED.value)
            else:
                stmt = stmt.where(
                    or_(
                        Meeting.transcript_status.is_(None),
                        Meeting.transcript_status != "completed",
                    )
                )
        if params.tags:
            stmt = stmt.where(Meeting.tags.contains(params.tags))

        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total      = (await self.db.execute(count_stmt)).scalar_one()

        # Sort
        sort_col = getattr(Meeting, params.sort_by, Meeting.created_at)
        stmt     = stmt.order_by(
            desc(sort_col) if params.sort_order == "desc" else asc(sort_col)
        )

        # Paginate
        offset = (params.page - 1) * params.per_page
        stmt   = stmt.offset(offset).limit(params.per_page)

        result = await self.db.execute(stmt)
        return result.scalars().all(), total

    # ==========================================
    # UPDATE
    # ==========================================

    async def update(
        self,
        meeting:    Meeting,
        data:       MeetingUpdate,
    ) -> Meeting:
        """Full update — replace all provided fields"""
        update_data = data.dict(exclude_unset=False, exclude_none=True)
        for field, value in update_data.items():
            if hasattr(meeting, field):
                if field == "attendees" and value is not None:
                    value            = [a.dict() if hasattr(a, "dict") else a for a in value]
                    meeting.participant_count = len(value)
                if field == "platform" and value is not None:
                    value = value.value if hasattr(value, "value") else value
                setattr(meeting, field, value)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(meeting)
        return meeting

    async def patch(
        self,
        meeting:    Meeting,
        data:       MeetingPatch,
    ) -> Meeting:
        """Partial update — only update fields explicitly set"""
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(meeting, field):
                if field == "attendees" and value is not None:
                    value            = [a.dict() if hasattr(a, "dict") else a for a in value]
                    meeting.participant_count = len(value)
                if field == "platform" and value is not None:
                    value = value.value if hasattr(value, "value") else value
                if field == "status" and value is not None:
                    value = value.value if hasattr(value, "value") else value
                setattr(meeting, field, value)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(meeting)
        return meeting

    async def update_status(
        self,
        meeting:    Meeting,
        new_status: str,
    ) -> Meeting:
        """Update meeting status (validates transition via model)"""
        meeting.status = new_status
        if new_status == MeetingStatus.IN_PROGRESS.value:
            meeting.actual_start = datetime.utcnow()
        elif new_status in (MeetingStatus.COMPLETED.value, MeetingStatus.CANCELLED.value, MeetingStatus.FAILED.value):
            if not meeting.actual_end:
                meeting.actual_end = datetime.utcnow()
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(meeting)
        return meeting

    async def update_recording(
        self,
        meeting:            Meeting,
        s3_key:             str,
        recording_url:      str,
        size_bytes:         int,
        duration_seconds:   Optional[int] = None,
        format:             Optional[str] = None,
    ) -> Meeting:
        """Update meeting with recording details after upload"""
        meeting.recording_s3_key           = s3_key
        meeting.recording_url              = recording_url
        meeting.recording_size_bytes       = size_bytes
        meeting.recording_duration_seconds = duration_seconds
        meeting.recording_uploaded_at      = datetime.utcnow()
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(meeting)
        return meeting

    async def increment_action_items_count(self, meeting_id: UUID, company_id: UUID) -> None:
        """Increment action items counter atomically"""
        stmt = (
            update(Meeting)
            .where(Meeting.id == meeting_id, Meeting.company_id == company_id)
            .values(action_items_count=Meeting.action_items_count + 1)
        )
        await self.db.execute(stmt)

    # ==========================================
    # DELETE
    # ==========================================

    async def soft_delete(self, meeting: Meeting, deleted_by: Optional[UUID] = None) -> Meeting:
        """Soft delete — set deleted_at timestamp"""
        meeting.soft_delete()
        await self.db.flush()
        await self.db.commit()
        return meeting

    async def hard_delete(self, meeting: Meeting) -> None:
        """Permanent delete — use with caution"""
        await self.db.delete(meeting)
        await self.db.flush()

    async def restore(self, meeting: Meeting) -> Meeting:
        """Restore a soft-deleted meeting"""
        meeting.restore()
        await self.db.flush()
        await self.db.refresh(meeting)
        return meeting

    # ==========================================
    # ANALYTICS / AGGREGATIONS
    # ==========================================

    async def count_by_status(self, company_id: UUID) -> Dict[str, int]:
        """Count meetings grouped by status"""
        stmt = (
            select(Meeting.status, func.count(Meeting.id).label("count"))
            .where(Meeting.company_id == company_id, Meeting.deleted_at.is_(None))
            .group_by(Meeting.status)
        )
        result = await self.db.execute(stmt)
        return {row.status: row.count for row in result}

    async def count_this_month(self, company_id: UUID) -> int:
        """Count meetings created this calendar month"""
        stmt = (
            select(func.count(Meeting.id))
            .where(
                Meeting.company_id == company_id,
                Meeting.deleted_at.is_(None),
                func.date_trunc("month", Meeting.created_at) == func.date_trunc("month", func.now()),
            )
        )
        return (await self.db.execute(stmt)).scalar_one()

    async def get_stats(self, company_id: UUID) -> Dict[str, Any]:
        """Get aggregated meeting statistics for a company"""
        # 1. Total count
        total_stmt = select(func.count(Meeting.id)).where(
            Meeting.company_id == company_id,
            Meeting.deleted_at.is_(None)
        )
        total = (await self.db.execute(total_stmt)).scalar_one()

        # 2. Count by status
        status_stmt = (
            select(Meeting.status, func.count(Meeting.id))
            .where(Meeting.company_id == company_id, Meeting.deleted_at.is_(None))
            .group_by(Meeting.status)
        )
        status_results = await self.db.execute(status_stmt)
        by_status = {r[0]: r[1] for r in status_results.all()}

        # 3. Total recording hours (estimated)
        duration_stmt = select(func.sum(Meeting.recording_duration_seconds)).where(
            Meeting.company_id == company_id,
            Meeting.deleted_at.is_(None)
        )
        total_seconds = (await self.db.execute(duration_stmt)).scalar_one() or 0
        total_hours = total_seconds / 3600

        return {
            "total_meetings": total,
            "by_status": by_status,
            "total_recording_hours": round(total_hours, 1),
            "upcoming_count": by_status.get(MeetingStatus.SCHEDULED.value, 0)
        }

    async def get_upcoming(
        self,
        company_id: UUID,
        limit:      int = 5,
    ) -> List[Meeting]:
        """Get next N upcoming meetings"""
        stmt = (
            self._base_query(company_id)
            .where(
                Meeting.status         == MeetingStatus.SCHEDULED.value,
                Meeting.scheduled_start >= datetime.utcnow(),
            )
            .order_by(asc(Meeting.scheduled_start))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ==========================================
    # PRIVATE FILTER HELPERS
    # ==========================================

    def _apply_filters(self, stmt, **kwargs):
        """Apply common filters to a query"""
        if kwargs.get("status"):
            statuses = kwargs["status"]
            values   = [s.value if hasattr(s, "value") else s for s in statuses]
            stmt     = stmt.where(Meeting.status.in_(values))

        if kwargs.get("platform"):
            platforms = kwargs["platform"]
            values    = [p.value if hasattr(p, "value") else p for p in platforms]
            stmt      = stmt.where(Meeting.platform.in_(values))

        if kwargs.get("date_from"):
            stmt = stmt.where(Meeting.scheduled_start >= kwargs["date_from"])

        if kwargs.get("date_to"):
            stmt = stmt.where(Meeting.scheduled_start <= kwargs["date_to"])

        if kwargs.get("created_by"):
            stmt = stmt.where(Meeting.created_by == kwargs["created_by"])

        if kwargs.get("has_recording") is True:
            stmt = stmt.where(Meeting.recording_url.isnot(None))
        elif kwargs.get("has_recording") is False:
            stmt = stmt.where(Meeting.recording_url.is_(None))

        if kwargs.get("tags"):
            stmt = stmt.where(Meeting.tags.contains(kwargs["tags"]))

        return stmt