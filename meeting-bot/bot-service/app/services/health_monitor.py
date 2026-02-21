"""
Bot Health Monitor
Vocaply AI Meeting Intelligence - Day 15

Background task that checks the health of active bots and cleans up
stale or failed instances.
"""

import asyncio
from typing import List
from app.config import settings
from shared.utils.logger import get_logger
from .redis_state import state_service
from .instance_pool import instance_pool

logger = get_logger("health-monitor")

class HealthMonitor:
    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("Health monitor started")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Health monitor stopped")

    async def _monitor_loop(self):
        while self._running:
            try:
                await self._check_bots()
            except Exception as e:
                logger.error(f"Error in health check: {e}")
            
            await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)

    async def _check_bots(self):
        """Audit all bots in Redis."""
        # Clean up bots that haven't updated in a while or are in 'failed' state
        active_ids = await state_service.get_all_active_bot_ids()
        
        for bot_id in active_ids:
            info = await state_service.get_bot_info(bot_id)
            if not info:
                continue

            # logic for timeout (e.g. if updated_at is > 5 mins ago)
            # or if status is FAILED, trigger recovery
            if info.status == "failed":
                logger.warning(f"Bot {bot_id} in failed state, triggering recovery")
                # Recovery logic: notify backend, terminate instance, release slot
                await instance_pool.release_instance(bot_id)

health_monitor = HealthMonitor()
