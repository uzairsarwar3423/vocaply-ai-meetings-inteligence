"""
Bot Join Worker
Celery task for executing scheduled bot joins
"""

from celery import Task
from celery.utils.log import get_task_logger
import asyncio

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.bot import BotScheduler
from app.models.calendar_event import CalendarEvent
from sqlalchemy import select

logger = get_task_logger(__name__)


@celery_app.task(
    bind=True,
    name="bot_join",
    max_retries=3,
)
def schedule_bot_join_task(self, meeting_id: str, company_id: str):
    """
    Start bot for a meeting (scheduled via ETA).
    
    This task is scheduled to run 2 minutes before meeting start time.
    
    Args:
        meeting_id: Meeting ID
        company_id: Company ID
    """
    try:
        logger.info(f"Starting bot for meeting {meeting_id}")
        asyncio.run(_join_meeting_async(meeting_id, company_id))
        logger.info(f"Bot started for meeting {meeting_id}")
    except Exception as exc:
        logger.error(f"Failed to start bot for meeting {meeting_id}: {exc}", exc_info=True)
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


async def _join_meeting_async(meeting_id: str, company_id: str):
    """Async bot join logic"""
    async with AsyncSessionLocal() as db:
        bot_scheduler = BotScheduler(db)
        
        try:
            # Start bot
            bot_session = await bot_scheduler.start_bot_for_meeting(
                meeting_id=meeting_id,
                company_id=company_id,
            )
            
            logger.info(f"Bot {bot_session.bot_instance_id} assigned to meeting {meeting_id}")
            
            # Mark calendar event as executed
            stmt = select(CalendarEvent).where(CalendarEvent.meeting_id == meeting_id)
            result = await db.execute(stmt)
            calendar_event = result.scalar_one_or_none()
            
            if calendar_event:
                calendar_event.auto_join_executed = True
                await db.commit()
            
        except Exception as e:
            logger.error(f"Bot join failed for meeting {meeting_id}: {e}")
            raise