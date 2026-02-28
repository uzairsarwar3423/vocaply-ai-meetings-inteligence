"""
Calendar Sync Worker
Celery task for periodic calendar synchronization
"""

from celery import Task
from celery.utils.log import get_task_logger
import asyncio

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.calendar import CalendarSyncService, AutoJoinScheduler

logger = get_task_logger(__name__)


@celery_app.task(
    bind=True,
    name="sync_calendars",
)
def sync_calendars_task(self):
    """
    Sync calendars for all users.
    Runs every 15 minutes (configured in Celery beat schedule).
    """
    try:
        logger.info("Starting calendar sync")
        asyncio.run(_sync_calendars_async())
        logger.info("Calendar sync complete")
    except Exception as exc:
        logger.error(f"Calendar sync failed: {exc}", exc_info=True)


async def _sync_calendars_async():
    """Async calendar sync logic"""
    from sqlalchemy import select
    from app.models.user import User

    async with AsyncSessionLocal() as db:
        # Get all users with calendar OAuth tokens
        stmt = select(User).where(User.calendar_token.isnot(None))
        result = await db.execute(stmt)
        users = result.scalars().all()

        sync_service = CalendarSyncService(db)

        for user in users:
            try:
                logger.info(f"Syncing calendar for user {user.id}")
                
                # Note: In production, you'd fetch the access token from OAuth token store
                # For now, assume it's stored in user.calendar_token
                count = await sync_service.sync_google_calendar(
                    user_id=str(user.id),
                    access_token=user.calendar_token,
                    days_ahead=7,
                )
                
                logger.info(f"Synced {count} events for user {user.id}")
            except Exception as e:
                logger.error(f"Failed to sync calendar for user {user.id}: {e}")


@celery_app.task(
    bind=True,
    name="schedule_auto_joins",
)
def schedule_auto_joins_task(self):
    """
    Schedule bots for upcoming calendar events.
    Runs every 5 minutes.
    """
    try:
        logger.info("Scheduling auto-joins")
        asyncio.run(_schedule_auto_joins_async())
        logger.info("Auto-join scheduling complete")
    except Exception as exc:
        logger.error(f"Auto-join scheduling failed: {exc}", exc_info=True)


async def _schedule_auto_joins_async():
    """Async auto-join scheduling logic"""
    async with AsyncSessionLocal() as db:
        scheduler = AutoJoinScheduler(db)
        
        # Look ahead 30 minutes
        count = await scheduler.schedule_upcoming_meetings(lookahead_minutes=30)
        
        logger.info(f"Scheduled {count} auto-joins")


@celery_app.task(
    bind=True,
    name="cleanup_old_calendar_events",
)
def cleanup_old_calendar_events_task(self):
    """
    Cleanup calendar events older than 30 days.
    Runs daily.
    """
    try:
        logger.info("Cleaning up old calendar events")
        asyncio.run(_cleanup_old_events_async())
        logger.info("Cleanup complete")
    except Exception as exc:
        logger.error(f"Cleanup failed: {exc}", exc_info=True)


async def _cleanup_old_events_async():
    """Async cleanup logic"""
    async with AsyncSessionLocal() as db:
        sync_service = CalendarSyncService(db)
        count = await sync_service.cleanup_old_events(days_old=30)
        logger.info(f"Deleted {count} old calendar events")