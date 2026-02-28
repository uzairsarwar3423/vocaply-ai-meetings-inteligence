"""
Bot Scheduler Worker
Celery task for monitoring bot health
"""

from celery import Task
from celery.utils.log import get_task_logger
import asyncio

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.bot import BotScheduler

logger = get_task_logger(__name__)


@celery_app.task(
    bind=True,
    name="monitor_bots",
)
def monitor_bots_task(self):
    """
    Celery task to monitor active bots.
    
    Runs every 30 seconds (configured in celery beat schedule).
    
    Checks:
    - Bot health
    - Stuck bots
    - Participant counts
    - Timeouts
    """
    try:
        logger.info("Monitoring active bots")
        
        # Run async monitoring in sync Celery context
        asyncio.run(_monitor_bots_async())
        
        logger.info("Bot monitoring complete")
        
    except Exception as exc:
        logger.error(f"Bot monitoring failed: {exc}", exc_info=True)
        # Don't retry on failure, just log


async def _monitor_bots_async():
    """Async bot monitoring logic"""
    async with AsyncSessionLocal() as db:
        scheduler = BotScheduler(db)
        await scheduler.monitor_active_bots()