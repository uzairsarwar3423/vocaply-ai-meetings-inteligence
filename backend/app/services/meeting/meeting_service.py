"""
Meeting Service
Vocaply Platform - Day 4

Business logic layer for meetings.
Sits between API layer and Repository layer.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status

from app.models.meeting import Meeting, MeetingStatus, VALID_STATUS_TRANSITIONS
from app.repositories.meeting_repository import MeetingRepository
from app.schemas.meeting import (
    MeetingCreate, MeetingUpdate, MeetingPatch,
    MeetingFilters, MeetingStatusUpdate,
    UploadRecordingResponse, MeetingResponse, MeetingListItem
)
from app.schemas.pagination import (
    PaginationParams, CursorPaginationParams,
    PaginatedResponse, CursorPaginatedResponse,
    PaginationMeta, CursorPaginationMeta
)


class MeetingService:
    """
    Business logic for meeting management.
    Handles validation, authorization, and orchestration.
    """

    def __init__(self, repository: MeetingRepository):
        self.repo = repository

    # ============================================
    # CREATE
    # ============================================

    async def create_meeting(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        data: MeetingCreate,
    ) -> Meeting:
        """
        Create a new meeting.
        Validates business rules before persisting.
        """
        # Business rule: can't schedule a meeting in the past (with 5 min buffer)
        if data.scheduled_start:
            buffer = 5 * 60  # 5 minutes in seconds
            now_ts = datetime.utcnow().timestamp()
            start_ts = data.scheduled_start.timestamp()
            if start_ts < (now_ts - buffer):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Cannot schedule a meeting in the past"
                )

        # Business rule: max duration 8 hours
        if data.scheduled_start and data.scheduled_end:
            diff_hours = (data.scheduled_end - data.scheduled_start).total_seconds() / 3600
            if diff_hours > 8:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Meeting duration cannot exceed 8 hours"
                )

        return await self.repo.create(company_id, user_id, data)

    # ============================================
    # READ
    # ============================================

    async def get_meeting(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> Meeting:
        """Get a single meeting, raise 404 if not found"""
        meeting = await self.repo.get_by_id(meeting_id, company_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting {meeting_id} not found"
            )
        return meeting

    async def list_meetings(
        self,
        company_id: uuid.UUID,
        pagination: PaginationParams,
        filters: Optional[MeetingFilters] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> PaginatedResponse[MeetingListItem]:
        """
        Get paginated meeting list.
        Returns structured pagination response.
        """
        # Validate sort field
        allowed_sort_fields = [
            "created_at", "updated_at", "scheduled_start", "title",
            "status", "participant_count", "action_items_count"
        ]
        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"

        meetings, total = await self.repo.list_meetings(
            company_id=company_id,
            page=pagination.page,
            per_page=pagination.per_page,
            sort_by=sort_by,
            sort_order=sort_dir,
            **(filters.dict() if filters else {})
        )

        total_pages = max(1, -(-total // pagination.per_page))  # ceiling division

        return PaginatedResponse(
            data=[MeetingListItem.from_orm(m) for m in meetings],
            pagination=PaginationMeta(
                page=pagination.page,
                per_page=pagination.per_page,
                total_items=total,
                total_pages=total_pages,
                has_next=pagination.page < total_pages,
                has_prev=pagination.page > 1,
            )
        )

    async def list_meetings_cursor(
        self,
        company_id: uuid.UUID,
        pagination: CursorPaginationParams,
        filters: Optional[MeetingFilters] = None,
    ) -> CursorPaginatedResponse[MeetingListItem]:
        """Cursor-based pagination (better for live updating lists)"""
        meetings, next_cursor, prev_cursor = await self.repo.list_meetings_cursor(
            company_id=company_id,
            cursor=pagination.cursor,
            limit=pagination.limit,
            direction=pagination.direction,
            **(filters.dict() if filters else {})
        )

        return CursorPaginatedResponse(
            data=[MeetingListItem.from_orm(m) for m in meetings],
            pagination=CursorPaginationMeta(
                next_cursor=next_cursor,
                prev_cursor=prev_cursor,
                has_next=next_cursor is not None,
                has_prev=prev_cursor is not None,
                limit=pagination.limit,
                count=len(meetings),
            )
        )

    async def search_meetings(
        self,
        company_id: uuid.UUID,
        query: str,
        pagination: PaginationParams,
        filters: Optional[MeetingFilters] = None,
    ) -> PaginatedResponse[MeetingListItem]:
        """Search meetings by title/description"""
        if not query or len(query.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Search query must be at least 2 characters"
            )

        from app.schemas.meeting import MeetingSearchParams
        search_params = MeetingSearchParams(
            q=query.strip(),
            page=pagination.page,
            per_page=pagination.per_page,
            **(filters.dict(exclude_none=True) if filters else {}),
        )

        meetings, total = await self.repo.search(
            company_id=company_id,
            params=search_params,
        )

        total_pages = max(1, -(-total // pagination.per_page))

        return PaginatedResponse(
            data=[MeetingListItem.from_orm(m) for m in meetings],
            pagination=PaginationMeta(
                page=pagination.page,
                per_page=pagination.per_page,
                total_items=total,
                total_pages=total_pages,
                has_next=pagination.page < total_pages,
                has_prev=pagination.page > 1,
            )
        )

    # ============================================
    # UPDATE
    # ============================================

    async def update_meeting(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
        data: MeetingUpdate,
    ) -> Meeting:
        """Full meeting update (PUT)"""
        meeting = await self.get_meeting(meeting_id, company_id)
        self._assert_editable(meeting)
        return await self.repo.update(meeting, data)

    async def patch_meeting(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
        data: MeetingPatch,
    ) -> Meeting:
        """Partial meeting update (PATCH)"""
        meeting = await self.get_meeting(meeting_id, company_id)
        self._assert_editable(meeting)
        return await self.repo.patch(meeting, data)

    async def transition_status(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
        payload: MeetingStatusUpdate,
    ) -> Meeting:
        """
        Transition meeting to a new status.
        Validates the transition is allowed.
        """
        meeting = await self.get_meeting(meeting_id, company_id)

        if meeting.status == payload.status:
            return meeting  # No-op, already in this status

        if not meeting.can_transition_to(payload.status):
            current = meeting.status
            allowed = [s.value for s in VALID_STATUS_TRANSITIONS.get(MeetingStatus(current), [])]
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": f"Cannot transition from '{current}' to '{payload.status}'",
                    "current_status": current,
                    "allowed_transitions": allowed,
                }
            )

        return await self.repo.update_status(meeting, payload.status)

    # ============================================
    # ATTENDEE MANAGEMENT
    # ============================================

    async def add_attendee(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
        name: str,
        email: str,
        role: str = "attendee",
    ) -> Meeting:
        """Add an attendee to a meeting"""
        meeting = await self.get_meeting(meeting_id, company_id)
        self._assert_editable(meeting)

        if email in meeting.attendee_emails:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Attendee with email {email!r} is already in this meeting"
            )

        meeting.add_attendee(name=name, email=email, role=role)
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(meeting, "attendees")

        meeting.updated_at = datetime.utcnow()
        await self.repo.db.commit()
        await self.repo.db.refresh(meeting)
        return meeting

    async def remove_attendee(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
        email: str,
    ) -> Meeting:
        """Remove an attendee from a meeting"""
        meeting = await self.get_meeting(meeting_id, company_id)
        self._assert_editable(meeting)

        if email not in meeting.attendee_emails:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attendee {email!r} not found in this meeting"
            )

        meeting.remove_attendee(email)
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(meeting, "attendees")

        meeting.updated_at = datetime.utcnow()
        await self.repo.db.commit()
        await self.repo.db.refresh(meeting)
        return meeting

    # ============================================
    # RECORDING UPLOAD
    # ============================================

    async def get_upload_url(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
        file_name: str,
        file_size: int,
        content_type: str,
    ) -> UploadRecordingResponse:
        """
        Generate a presigned URL for direct recording upload to Backblaze B2.
        The frontend uploads directly to storage — not through our API.
        """
        meeting = await self.get_meeting(meeting_id, company_id)

        # Validate file size (500 MB max)
        max_size = 500 * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"File size exceeds maximum allowed size of 500 MB"
            )

        # Validate content type
        allowed_types = {
            "audio/mpeg", "audio/mp3", "audio/wav", "audio/m4a",
            "video/mp4", "video/webm", "audio/webm", "audio/ogg",
        }
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Content type '{content_type}' is not allowed"
            )

        # Build S3 key
        ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else "mp4"
        s3_key = f"companies/{company_id}/meetings/{meeting_id}/recording.{ext}"

        # Generate presigned URL (implementation depends on storage service)
        # In a real app, inject StorageService here
        presigned_url = self._generate_presigned_url(s3_key, content_type)

        return UploadRecordingResponse(
            upload_url=presigned_url,
            s3_key=s3_key,
            meeting_id=meeting_id,
            expires_in=3600,
        )

    async def confirm_recording_upload(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
        s3_key: str,
        recording_url: str,
        size_bytes: Optional[int] = None,
        duration_seconds: Optional[int] = None,
        format: Optional[str] = None,
    ) -> Meeting:
        """
        Called after frontend confirms upload complete.
        Updates meeting record and triggers transcription.
        """
        meeting = await self.get_meeting(meeting_id, company_id)

        meeting = await self.repo.update_recording(
            meeting=meeting,
            recording_url=recording_url,
            s3_key=s3_key,
            size_bytes=size_bytes,
            duration_seconds=duration_seconds,
            format=format,
        )

        # Trigger async transcription job
        # In a real app: celery_app.send_task("tasks.transcribe_meeting", args=[str(meeting_id)])

        return meeting

    # ============================================
    # STATISTICS
    # ============================================

    async def get_stats(self, company_id: uuid.UUID) -> Dict[str, Any]:
        """Get meeting statistics for a company"""
        return await self.repo.get_stats(company_id)

    async def get_upcoming(
        self,
        company_id: uuid.UUID,
        limit: int = 5,
    ) -> List[Meeting]:
        """Get next N upcoming meetings"""
        return await self.repo.get_upcoming(company_id, limit)

    # ============================================
    # DELETE
    # ============================================

    async def delete_meeting(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
        deleted_by_id: uuid.UUID,
    ) -> None:
        """Soft delete a meeting"""
        meeting = await self.get_meeting(meeting_id, company_id)

        if meeting.status == MeetingStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete a meeting that is currently in progress"
            )

        await self.repo.soft_delete(meeting, deleted_by_id)

    # ============================================
    # PRIVATE HELPERS
    # ============================================

    def _assert_editable(self, meeting: Meeting) -> None:
        """Raise 409 if meeting cannot be edited"""
        non_editable = {MeetingStatus.COMPLETED, MeetingStatus.CANCELLED}
        if MeetingStatus(meeting.status) in non_editable:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot edit a meeting with status '{meeting.status}'"
            )

    def _generate_presigned_url(self, s3_key: str, content_type: str) -> str:
        """
        Generate a presigned URL for Backblaze B2.
        Placeholder — in production, inject StorageService.
        """
        # TODO: Replace with actual Backblaze B2 presigned URL generation
        # from app.services.storage.backblaze_service import BackblazeService
        # return await storage.generate_presigned_url(s3_key, content_type)
        return f"https://s3.us-west-004.backblazeb2.com/vocaply-meetings/{s3_key}?X-Amz-Expires=3600"