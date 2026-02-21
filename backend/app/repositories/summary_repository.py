"""
Summary Repository
Vocaply Platform - Day 13

Database operations for meeting summaries.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting_summary import MeetingSummary
from app.schemas.summary import MeetingSummaryUpdate


class SummaryRepository:
    """Handles all meeting summary database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_or_update(self, summary: MeetingSummary) -> MeetingSummary:
        """Create a new summary or update existing one for a meeting"""
        stmt = select(MeetingSummary).where(MeetingSummary.meeting_id == summary.meeting_id)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.short_summary    = summary.short_summary
            existing.detailed_summary = summary.detailed_summary
            existing.key_points       = summary.key_points
            existing.decisions        = summary.decisions
            existing.topics           = summary.topics
            existing.sentiment        = summary.sentiment
            existing.model_version    = summary.model_version
            existing.token_usage      = summary.token_usage
            existing.updated_at       = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            self.db.add(summary)
            await self.db.commit()
            await self.db.refresh(summary)
            return summary

    async def get_by_meeting(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> Optional[MeetingSummary]:
        """Get summary for a specific meeting"""
        stmt = select(MeetingSummary).where(
            and_(
                MeetingSummary.meeting_id == meeting_id,
                MeetingSummary.company_id == str(company_id),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        summary_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> Optional[MeetingSummary]:
        """Get summary by its own primary key"""
        stmt = select(MeetingSummary).where(
            and_(
                MeetingSummary.id         == summary_id,
                MeetingSummary.company_id == str(company_id),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(
        self,
        summary: MeetingSummary,
        data: MeetingSummaryUpdate,
    ) -> MeetingSummary:
        """Partial update from user edits"""
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(summary, field):
                setattr(summary, field, value)
        summary.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(summary)
        return summary

    async def delete(self, meeting_id: uuid.UUID, company_id: uuid.UUID) -> bool:
        """Delete summary for a meeting"""
        stmt = delete(MeetingSummary).where(
            and_(
                MeetingSummary.meeting_id == meeting_id,
                MeetingSummary.company_id == str(company_id),
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
