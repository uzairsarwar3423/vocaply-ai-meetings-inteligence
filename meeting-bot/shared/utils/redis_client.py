"""
Redis Client
Shared Redis connection and operations
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import redis.asyncio as redis


class RedisClient:
    """Async Redis client wrapper"""

    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client: Optional[redis.Redis] = None

    async def connect(self):
        """Establish connection"""
        if not self._client:
            self._client = redis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True,
                socket_keepalive=True,
                socket_timeout=5,
            )
        return self._client

    async def disconnect(self):
        """Close connection"""
        if self._client:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> redis.Redis:
        """Get client (ensure connected first)"""
        if not self._client:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client

    # ── Bot State ────────────────────────────────────
    async def set_bot(self, bot_id: str, data: Dict[str, Any], ttl: int = 3600):
        """Store bot instance data"""
        key = f"bot:{bot_id}"
        await self.client.setex(key, ttl, json.dumps(data, default=str))

    async def get_bot(self, bot_id: str) -> Optional[Dict]:
        """Get bot instance data"""
        key = f"bot:{bot_id}"
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def delete_bot(self, bot_id: str):
        """Remove bot from Redis"""
        key = f"bot:{bot_id}"
        await self.client.delete(key)

    # ── Bot Pool ─────────────────────────────────────
    async def add_to_pool(self, bot_id: str, available: bool = True):
        """Add bot to available or in-use pool"""
        pool = "bot:pool:available" if available else "bot:pool:in_use"
        await self.client.sadd(pool, bot_id)

    async def remove_from_pool(self, bot_id: str):
        """Remove bot from all pools"""
        await self.client.srem("bot:pool:available", bot_id)
        await self.client.srem("bot:pool:in_use", bot_id)

    async def move_to_in_use(self, bot_id: str):
        """Move bot from available to in-use"""
        await self.client.smove("bot:pool:available", "bot:pool:in_use", bot_id)

    async def move_to_available(self, bot_id: str):
        """Move bot from in-use to available"""
        await self.client.smove("bot:pool:in_use", "bot:pool:available", bot_id)

    async def get_available_bots(self) -> List[str]:
        """Get all available bot IDs"""
        return list(await self.client.smembers("bot:pool:available"))

    async def get_in_use_bots(self) -> List[str]:
        """Get all in-use bot IDs"""
        return list(await self.client.smembers("bot:pool:in_use"))

    async def pool_size(self) -> tuple[int, int]:
        """Get (available, in_use) counts"""
        available = await self.client.scard("bot:pool:available")
        in_use = await self.client.scard("bot:pool:in_use")
        return (available, in_use)

    # ── Company Tracking ─────────────────────────────
    async def add_company_bot(self, company_id: str, bot_id: str):
        """Track active bot for company"""
        key = f"company:{company_id}:active_bots"
        await self.client.sadd(key, bot_id)
        await self.client.expire(key, 86400)  # 24 hour TTL

    async def remove_company_bot(self, company_id: str, bot_id: str):
        """Remove bot from company's active list"""
        key = f"company:{company_id}:active_bots"
        await self.client.srem(key, bot_id)

    async def get_company_bots(self, company_id: str) -> List[str]:
        """Get all active bots for company"""
        key = f"company:{company_id}:active_bots"
        return list(await self.client.smembers(key))

    # ── Heartbeat ────────────────────────────────────
    async def set_heartbeat(self, bot_id: str, ttl: int = 60):
        """Update bot heartbeat"""
        key = f"bot:{bot_id}:heartbeat"
        await self.client.setex(key, ttl, datetime.utcnow().isoformat())

    async def get_heartbeat(self, bot_id: str) -> Optional[str]:
        """Get last heartbeat timestamp"""
        key = f"bot:{bot_id}:heartbeat"
        return await self.client.get(key)

    # ── Metrics ──────────────────────────────────────
    async def increment_counter(self, key: str, amount: int = 1):
        """Increment a counter"""
        await self.client.incrby(key, amount)

    async def get_counter(self, key: str) -> int:
        """Get counter value"""
        val = await self.client.get(key)
        return int(val) if val else 0

    # ── Pub/Sub ──────────────────────────────────────
    async def publish(self, channel: str, message: Dict):
        """Publish message to channel"""
        await self.client.publish(channel, json.dumps(message, default=str))

    async def subscribe(self, channel: str):
        """Subscribe to channel (returns async generator)"""
        pubsub = self.client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    # ── Lock (for critical sections) ─────────────────
    async def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        """Acquire distributed lock"""
        return await self.client.set(
            f"lock:{lock_name}",
            "1",
            nx=True,
            ex=timeout,
        )

    async def release_lock(self, lock_name: str):
        """Release distributed lock"""
        await self.client.delete(f"lock:{lock_name}")


# ── Singleton instance ───────────────────────────────
_redis_client: Optional[RedisClient] = None


async def get_redis() -> RedisClient:
    """Get or create Redis client singleton"""
    global _redis_client
    if not _redis_client:
        _redis_client = RedisClient()
        await _redis_client.connect()
    return _redis_client