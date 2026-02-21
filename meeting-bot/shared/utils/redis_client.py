"""
Shared Redis Client
Vocaply AI Meeting Intelligence - Day 15

Async Redis client with automatic connection pooling and retry logic.
Shared between bot-service and individual bot instances.
"""

import os
from typing import Optional, Any
import redis.asyncio as redis
from .logger import get_logger

logger = get_logger("redis-client")

class RedisClient:
    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis: Optional[redis.Redis] = None

    async def connect(self):
        """Initialize the connection pool."""
        if self._redis is None:
            logger.info(f"Connecting to Redis at {self.url}")
            self._redis = redis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                retry_on_timeout=True
            )
        return self._redis

    async def disconnect(self):
        """Close the connection pool."""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Redis disconnected")

    @property
    def client(self) -> redis.Redis:
        if self._redis is None:
            raise RuntimeError("RedisClient not connected. Call .connect() first.")
        return self._redis

    # Helpers for common operations
    async def set_json(self, key: str, data: Any, expire: Optional[int] = None):
        import json
        await self.client.set(key, json.dumps(data), ex=expire)

    async def get_json(self, key: str) -> Optional[Any]:
        import json
        data = await self.client.get(key)
        return json.loads(data) if data else None

# Singleton instance
redis_client = RedisClient()
