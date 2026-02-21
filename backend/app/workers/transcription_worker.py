"""
Transcription Worker
Vocaply Platform - Day 7

Celery tasks for background transcription processing.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict
import uuid

from celery import Task
from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery_app import celery_app
from app.db.session import async_session_maker
from app.services.transcription import DeepgramService, TranscriptProcessor
from app.repositories.transcript_repository import TranscriptRepository
from app.repositories.meeting_repository import MeetingRepository
from app.models.meeting import MeetingStatus

logger = get_task_logger(__name__)


# ============================================
# BASE TASK WITH DB SESSION
# ============================================

class DatabaseTask(Task):
    """Base task that provides async DB session"""
    _db = None

    async def get_db(self) -> AsyncSession:
        """Get async database session"""
        async with async_session_maker() as session:
            yield session


# ============================================
# TRANSCRIPTION TASK
# ============================================

@celery_app.task(
    bind=True,
    name="transcribe_meeting",
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def transcribe_meeting_task(
    self,
    meeting_id: str,
    recording_url: str,
    language: str = "en",
    model: str = "nova-2",
    diarize: bool = True,
) -> Dict[str, Any]:
    """
    Background task to transcribe a meeting recording.
    
    Flow:
    1. Update meeting status → transcribing
    2. Call Deepgram API
    3. Parse response
    4. Save chunks to database
    5. Update meeting status → analyzing (ready for AI extraction)
    """
    try:
        logger.info(f"Starting transcription for meeting {meeting_id}")
        
        # Run async processing in sync Celery context
        result = asyncio.run(
            _process_transcription(
                meeting_id=uuid.UUID(meeting_id),
                recording_url=recording_url,
                language=language,
                model=model,
                diarize=diarize,
            )
        )
        
        logger.info(f"Transcription complete for meeting {meeting_id}: {result['chunks']} chunks")
        return result

    except Exception as exc:
        logger.error(f"Transcription failed for meeting {meeting_id}: {exc}", exc_info=True)
        
        # Update meeting status to failed
        asyncio.run(_update_meeting_status(
            meeting_id=uuid.UUID(meeting_id),
            status=MeetingStatus.FAILED,
            error=str(exc),
        ))
        
        # Retry if not max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            "success": False,
            "error": str(exc),
            "meeting_id": meeting_id,
        }


# ============================================
# ASYNC PROCESSING LOGIC
# ============================================

async def _process_transcription(
    meeting_id: uuid.UUID,
    recording_url: str,
    language: str,
    model: str,
    diarize: bool,
) -> Dict[str, Any]:
    """Core async transcription logic"""
    async with async_session_maker() as db:
        meeting_repo = MeetingRepository(db)
        transcript_repo = TranscriptRepository(db)
        
        # Get meeting
        meeting = await meeting_repo.get_by_id(meeting_id, meeting_id)  # TODO: fix company_id
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")
        
        # Update status → transcribing
        await meeting_repo.update_status(
            meeting=meeting,
            new_status=MeetingStatus.TRANSCRIBING,
            transcript_status="processing",
        )
        
        start_time = datetime.utcnow()
        
        # Call Deepgram
        deepgram = DeepgramService()
        response = await deepgram.transcribe_from_url(
            audio_url=recording_url,
            language=language,
            model=model,
            diarize=diarize,
            punctuate=True,
            smart_format=True,
            paragraphs=True,
        )
        
        if not response.get("success"):
            raise RuntimeError(f"Deepgram error: {response.get('error')}")
        
        # Parse response
        parsed = deepgram.parse_transcription(response["result"])
        if not parsed.get("success"):
            raise RuntimeError(f"Parse error: {parsed.get('error')}")
        
        # Process into chunks
        processor = TranscriptProcessor(transcript_repo)
        chunks_created, metadata = await processor.process_transcription(
            meeting=meeting,
            deepgram_result=parsed,
            audio_duration=parsed.get("duration", 0),
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Update metadata with processing time
        metadata.processing_time_seconds = processing_time
        metadata.estimated_cost_usd = deepgram.estimate_cost(
            parsed.get("duration", 0),
            model=model,
        )
        await db.commit()
        
        # Update meeting status → analyzing (ready for AI)
        await meeting_repo.update_status(
            meeting=meeting,
            new_status=MeetingStatus.ANALYZING,
            transcript_status="completed",
            transcript_completed_at=datetime.utcnow(),
            transcript_word_count=metadata.total_words,
        )
        
        return {
            "success": True,
            "meeting_id": str(meeting_id),
            "chunks": chunks_created,
            "words": metadata.total_words,
            "duration": metadata.total_duration_seconds,
            "speakers": metadata.speaker_count,
            "processing_time": processing_time,
            "cost": metadata.estimated_cost_usd,
        }


async def _update_meeting_status(
    meeting_id: uuid.UUID,
    status: MeetingStatus,
    error: str = None,
):
    """Update meeting status after failure"""
    async with async_session_maker() as db:
        meeting_repo = MeetingRepository(db)
        meeting = await meeting_repo.get_by_id(meeting_id, meeting_id)
        if meeting:
            await meeting_repo.update_status(
                meeting=meeting,
                new_status=status,
                transcript_status="failed" if error else None,
            )


# ============================================
# MAINTENANCE TASKS
# ============================================

@celery_app.task(name="cleanup_old_results")
def cleanup_old_results():
    """Delete Celery task results older than 7 days"""
    logger.info("Running cleanup of old task results")
    # Celery automatically expires results based on result_expires config
    # This is a placeholder for custom cleanup logic
    return {"cleaned": 0}


@celery_app.task(name="check_stuck_jobs")
def check_stuck_jobs():
    """
    Check for meetings stuck in 'transcribing' status > 1 hour.
    Retry or mark as failed.
    """
    logger.info("Checking for stuck transcription jobs")
    
    result = asyncio.run(_check_stuck_jobs_async())
    return result


async def _check_stuck_jobs_async() -> Dict[str, Any]:
    """Find and handle stuck jobs"""
    async with async_session_maker() as db:
        meeting_repo = MeetingRepository(db)
        
        # Find meetings stuck in transcribing > 1 hour
        from sqlalchemy import select, and_
        from app.models.meeting import Meeting
        
        cutoff = datetime.utcnow() - timedelta(hours=1)
        
        stmt = select(Meeting).where(
            and_(
                Meeting.status == MeetingStatus.TRANSCRIBING,
                Meeting.updated_at < cutoff,
            )
        )
        
        result = await db.execute(stmt)
        stuck_meetings = result.scalars().all()
        
        logger.info(f"Found {len(stuck_meetings)} stuck meetings")
        
        for meeting in stuck_meetings:
            logger.warning(f"Marking stuck meeting {meeting.id} as failed")
            await meeting_repo.update_status(
                meeting=meeting,
                new_status=MeetingStatus.FAILED,
                transcript_status="failed",
            )
        
        return {
            "stuck_meetings": len(stuck_meetings),
            "meetings": [str(m.id) for m in stuck_meetings],
        }


# ============================================
# TASK STATUS HELPERS
# ============================================

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get status of a Celery task"""
    result = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": result.status,  # PENDING, STARTED, SUCCESS, FAILURE, RETRY
        "result": result.result if result.ready() else None,
        "traceback": result.traceback if result.failed() else None,
    }


def revoke_task(task_id: str, terminate: bool = False):
    """Cancel a running task"""
    celery_app.control.revoke(task_id, terminate=terminate)