"""
Transcripts API Endpoints
Vocaply Platform - Day 7

Endpoints for retrieving meeting transcripts, speaker stats, and performing searches.
"""

import uuid
from typing import List, Optional, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models import User
from app.schemas.transcript import (
    Transcript,
    TranscriptMetadata,
    TranscriptUpdate,
    TranscriptSearchResponse
)
from app.schemas.pagination import PaginationParams
from app.repositories.transcript_repository import TranscriptRepository

router = APIRouter()


@router.get("/meeting/{meeting_id}", response_model=List[Transcript])
async def get_meeting_transcript(
    meeting_id: uuid.UUID,
    include_words: bool = Query(False, description="Include detailed word timestamps"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve the full transcript for a specific meeting.
    Ordered by sequence number.
    """
    repo = TranscriptRepository(db)
    transcripts = await repo.get_meeting_transcript(
        meeting_id=meeting_id,
        company_id=current_user.company_id,
        include_words=include_words
    )
    
    if not transcripts and include_words:
        # Check if meeting exists but no transcript yet
        pass
        
    return transcripts


@router.get("/meeting/{meeting_id}/metadata", response_model=TranscriptMetadata)
async def get_transcript_metadata(
    meeting_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get aggregated transcript metadata (speaker stats, totals) for a meeting.
    """
    repo = TranscriptRepository(db)
    metadata = await repo.get_metadata(
        meeting_id=meeting_id,
        company_id=current_user.company_id
    )
    
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript metadata not found for this meeting"
        )
        
    return metadata


@router.get("/search", response_model=TranscriptSearchResponse)
async def search_transcripts(
    q: str = Query(..., min_length=2, description="Search query"),
    meeting_id: Optional[uuid.UUID] = None,
    speaker_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Full-text search across all transcripts within the company.
    Can be filtered by meeting_id or speaker_id.
    """
    repo = TranscriptRepository(db)
    pagination = PaginationParams(page=page, per_page=per_page)
    
    results, total = await repo.search(
        company_id=current_user.company_id,
        query=q,
        meeting_id=meeting_id,
        speaker_id=speaker_id,
        pagination=pagination
    )
    
    return {
        "results": results,
        "total": total,
        "query": q
    }


@router.patch("/{transcript_id}", response_model=Transcript)
async def update_transcript_chunk(
    transcript_id: uuid.UUID,
    chunk_in: TranscriptUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Manually correct a transcript chunk text or speaker info.
    Backs up the original text on first edit.
    """
    repo = TranscriptRepository(db)
    
    # Check existence
    chunk = await repo.get_chunk_by_id(transcript_id, current_user.company_id)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript chunk not found"
        )
    
    if chunk_in.text is not None:
        chunk = await repo.edit_chunk_text(
            chunk_id=transcript_id,
            new_text=chunk_in.text,
            edited_by=current_user.id
        )
        
    # Update speaker info if provided
    if chunk_in.speaker_name is not None or chunk_in.speaker_email is not None:
        # Note: In a real app, you might want to bulk update ALL chunks for this speaker_id
        # For now, we update just this chunk or the repo handles bulk if desired.
        if chunk.speaker_id:
            await repo.update_speaker_info(
                meeting_id=chunk.meeting_id,
                speaker_id=chunk.speaker_id,
                name=chunk_in.speaker_name,
                email=chunk_in.speaker_email
            )
            # Refresh chunk to get updated speaker info
            chunk = await repo.get_chunk_by_id(transcript_id, current_user.company_id)

    return chunk