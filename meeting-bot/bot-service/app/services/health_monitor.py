"""
Health Monitor
System health checks and metrics
"""

import asyncio
import psutil
from datetime import datetime
from typing import Dict, Any

from app.config import settings
from shared.utils.redis_client import RedisClient
from shared.utils.logger import logger


class HealthMonitor:
    """Monitor system health and metrics"""

    def __init__(self, redis: RedisClient):
        self.redis = redis
        self._monitor_task: asyncio.Task = None
        self.metrics: Dict[str, Any] = {}

    async def start(self):
        """Start monitoring"""
        logger.info("Starting health monitor")
        self._monitor_task = asyncio.create_task(self._collect_metrics())

    async def stop(self):
        """Stop monitoring"""
        if self._monitor_task:
            self._monitor_task.cancel()
        logger.info("Health monitor stopped")

    async def get_health(self) -> Dict[str, Any]:
        """Get current health status"""
        try:
            # Check Redis
            await self.redis.client.ping()
            redis_healthy = True
        except:
            redis_healthy = False

        # System resources
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Pool metrics
        available, in_use = await self.redis.pool_size()

        return {
            "status": "healthy" if redis_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "bot-service",
            "version": "1.0.0",
            "redis": {
                "connected": redis_healthy,
            },
            "pool": {
                "available": available,
                "in_use": in_use,
                "total": available + in_use,
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_percent": disk.percent,
            },
        }

    async def _collect_metrics(self):
        """Background task: collect metrics"""
        while True:
            try:
                await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
                
                self.metrics = await self.get_health()
                
                # Store in Redis for monitoring
                await self.redis.client.setex(
                    "bot-service:health",
                    settings.HEALTH_CHECK_INTERVAL * 2,
                    str(self.metrics),
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}", exc_info=True)