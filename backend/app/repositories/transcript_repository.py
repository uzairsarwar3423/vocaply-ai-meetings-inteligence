"""
Transcript Repository
Vocaply Platform - Day 7

Database operations for transcripts and metadata.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select, update, delete, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcript import Transcript, TranscriptMetadata
from app.schemas.pagination import PaginationParams


class TranscriptRepository:
    """Handles all transcript database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================
    # CREATE
    # ============================================

    async def create_chunk(self, chunk: Transcript) -> Transcript:
        """Create a single transcript chunk"""
        self.db.add(chunk)
        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    async def bulk_create_chunks(self, chunks: List[Transcript]) -> int:
        """Bulk insert transcript chunks"""
        self.db.add_all(chunks)
        await self.db.commit()
        return len(chunks)

    async def create_metadata(self, metadata: TranscriptMetadata) -> TranscriptMetadata:
        """Create transcript metadata"""
        self.db.add(metadata)
        await self.db.commit()
        await self.db.refresh(metadata)
        return metadata

    # ============================================
    # READ - Single
    # ============================================

    async def get_chunk_by_id(
        self,
        chunk_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> Optional[Transcript]:
        """Get a single transcript chunk"""
        stmt = select(Transcript).where(
            and_(
                Transcript.id == chunk_id,
                Transcript.company_id == company_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_chunks_by_ids(self, chunk_ids: List[uuid.UUID]) -> List[Transcript]:
        """Get multiple chunks by IDs"""
        stmt = select(Transcript).where(Transcript.id.in_(chunk_ids))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_metadata(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> Optional[TranscriptMetadata]:
        """Get transcript metadata for a meeting"""
        stmt = select(TranscriptMetadata).where(
            and_(
                TranscriptMetadata.meeting_id == meeting_id,
                TranscriptMetadata.company_id == company_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ============================================
    # READ - List
    # ============================================

    async def get_meeting_transcript(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
        include_words: bool = False,
    ) -> List[Transcript]:
        """Get all transcript chunks for a meeting, ordered by sequence"""
        stmt = select(Transcript).where(
            and_(
                Transcript.meeting_id == meeting_id,
                Transcript.company_id == company_id,
            )
        ).order_by(Transcript.sequence_number)

        if not include_words:
            stmt = stmt.options()

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_meeting_id(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> Optional["_TranscriptText"]:
        """
        Return a lightweight object with .content (full concatenated text)
        for use by the summarizer. Returns None if no chunks exist.
        """
        chunks = await self.get_meeting_transcript(meeting_id, company_id)
        if not chunks:
            return None

        # Concatenate all chunks into a single text
        full_text = "\n".join(
            f"{c.speaker_name or c.speaker_id or 'Speaker'}: {c.text}"
            for c in chunks
            if c.text
        )

        class _TranscriptText:
            content = full_text

        return _TranscriptText()

    async def get_by_speaker(
        self,
        meeting_id: uuid.UUID,
        speaker_id: str,
        company_id: uuid.UUID,
    ) -> List[Transcript]:
        """Get all chunks for a specific speaker"""
        stmt = select(Transcript).where(
            and_(
                Transcript.meeting_id == meeting_id,
                Transcript.speaker_id == speaker_id,
                Transcript.company_id == company_id,
            )
        ).order_by(Transcript.sequence_number)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_time_range(
        self,
        meeting_id: uuid.UUID,
        start_time: float,
        end_time: float,
        company_id: uuid.UUID,
    ) -> List[Transcript]:
        """Get chunks within a time range"""
        stmt = select(Transcript).where(
            and_(
                Transcript.meeting_id == meeting_id,
                Transcript.company_id == company_id,
                Transcript.start_time >= start_time,
                Transcript.end_time <= end_time,
            )
        ).order_by(Transcript.sequence_number)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ============================================
    # SEARCH
    # ============================================

    async def search(
        self,
        company_id: uuid.UUID,
        query: str,
        meeting_id: Optional[uuid.UUID] = None,
        speaker_id: Optional[str] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> Tuple[List[Transcript], int]:
        """
        Full-text search across transcripts.
        Uses PostgreSQL's tsvector for performance.
        """
        # Base query with full-text search
        stmt = select(Transcript).where(
            and_(
                Transcript.company_id == company_id,
                func.to_tsvector("english", Transcript.text).op("@@")(
                    func.plainto_tsquery("english", query)
                ),
            )
        )

        # Add filters
        if meeting_id:
            stmt = stmt.where(Transcript.meeting_id == meeting_id)
        if speaker_id:
            stmt = stmt.where(Transcript.speaker_id == speaker_id)

        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        # Order by relevance
        stmt = stmt.order_by(
            func.ts_rank(
                func.to_tsvector("english", Transcript.text),
                func.plainto_tsquery("english", query)
            ).desc()
        )

        # Paginate
        if pagination:
            stmt = stmt.offset(pagination.offset).limit(pagination.limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    # ============================================
    # UPDATE
    # ============================================

    async def update_chunk(self, chunk: Transcript) -> Transcript:
        """Update a transcript chunk"""
        chunk.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    async def update_speaker_info(
        self,
        meeting_id: uuid.UUID,
        speaker_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> int:
        """Bulk update speaker info across all chunks"""
        updates = {}
        if name is not None:
            updates["speaker_name"] = name
        if email is not None:
            updates["speaker_email"] = email

        if not updates:
            return 0

        stmt = (
            update(Transcript)
            .where(
                and_(
                    Transcript.meeting_id == meeting_id,
                    Transcript.speaker_id == speaker_id,
                )
            )
            .values(**updates)
        )

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def edit_chunk_text(
        self,
        chunk_id: uuid.UUID,
        new_text: str,
        edited_by: uuid.UUID,
    ) -> Optional[Transcript]:
        """Edit transcript chunk text (manual correction)"""
        chunk = await self.get_chunk_by_id(chunk_id, None)  # TODO: add company_id
        if not chunk:
            return None

        # Backup original text if first edit
        if not chunk.is_edited:
            chunk.original_text = chunk.text

        chunk.text = new_text
        chunk.is_edited = True
        chunk.edited_by = edited_by
        chunk.edited_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    # ============================================
    # DELETE
    # ============================================

    async def delete_chunks(self, chunk_ids: List[uuid.UUID]) -> int:
        """Delete multiple chunks"""
        stmt = delete(Transcript).where(Transcript.id.in_(chunk_ids))
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def delete_meeting_transcript(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> int:
        """Delete all transcript chunks for a meeting"""
        stmt = delete(Transcript).where(
            and_(
                Transcript.meeting_id == meeting_id,
                Transcript.company_id == company_id,
            )
        )
        result = await self.db.execute(stmt)

        # Also delete metadata
        metadata_stmt = delete(TranscriptMetadata).where(
            and_(
                TranscriptMetadata.meeting_id == meeting_id,
                TranscriptMetadata.company_id == company_id,
            )
        )
        await self.db.execute(metadata_stmt)

        await self.db.commit()
        return result.rowcount

    # ============================================
    # STATISTICS
    # ============================================

    async def get_speaker_stats(
        self,
        meeting_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> List[dict]:
        """Get aggregated stats per speaker"""
        stmt = select(
            Transcript.speaker_id,
            Transcript.speaker_name,
            Transcript.speaker_email,
            func.count(Transcript.id).label("turn_count"),
            func.sum(Transcript.duration).label("total_duration"),
            func.sum(func.length(Transcript.text)).label("total_chars"),
        ).where(
            and_(
                Transcript.meeting_id == meeting_id,
                Transcript.company_id == company_id,
            )
        ).group_by(
            Transcript.speaker_id,
            Transcript.speaker_name,
            Transcript.speaker_email,
        )

        result = await self.db.execute(stmt)
        return [
            {
                "speaker_id": row.speaker_id,
                "name": row.speaker_name,
                "email": row.speaker_email,
                "turns": row.turn_count,
                "duration": float(row.total_duration or 0),
                "chars": row.total_chars or 0,
            }
            for row in result.all()
        ]