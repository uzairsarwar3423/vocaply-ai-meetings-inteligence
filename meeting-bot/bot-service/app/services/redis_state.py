"""
Redis State Manager
Vocaply AI Meeting Intelligence - Day 15

Handles the schema transitions and atomic operations for bot lifecycle:
bot:{bot_id}       -> Details
bot:pool:available -> List of IDs
bot:pool:in_use    -> List of IDs
company:{company_id}:active_bots -> Active set
"""

import json
from datetime import datetime
from typing import List, Optional, Any
from shared.utils.redis_client import redis_client
from shared.models.bot_status import BotInfo, BotStatus

class RedisStateService:
    @staticmethod
    def _key_bot(bot_id: str) -> str:
        return f"bot:{bot_id}"
    
    @staticmethod
    def _key_pool_available() -> str:
        return "bot:pool:available"
    
    @staticmethod
    def _key_pool_in_use() -> str:
        return "bot:pool:in_use"
    
    @staticmethod
    def _key_company_bots(company_id: str) -> str:
        return f"company:{company_id}:active_bots"

    async def save_bot_info(self, info: BotInfo):
        info.updated_at = datetime.utcnow()
        await redis_client.client.set(
            self._key_bot(info.bot_id),
            info.model_dump_json()
        )

    async def get_bot_info(self, bot_id: str) -> Optional[BotInfo]:
        data = await redis_client.client.get(self._key_bot(bot_id))
        if not data:
            return None
        return BotInfo.model_validate_json(data)

    async def delete_bot_info(self, bot_id: str):
        await redis_client.client.delete(self._key_bot(bot_id))

    async def add_to_pool(self, bot_id: str):
        """Atomic move to available pool."""
        pipe = redis_client.client.pipeline()
        pipe.lrem(self._key_pool_in_use(), 0, bot_id)
        pipe.lpush(self._key_pool_available(), bot_id)
        await pipe.execute()

    async def claim_from_pool(self) -> Optional[str]:
        """Atomically pop from available and push to in_use."""
        # Using RPOPLPUSH (or LMOVE in newer redis) for atomic migration
        return await redis_client.client.rpoplpush(
            self._key_pool_available(),
            self._key_pool_in_use()
        )

    async def release_to_pool(self, bot_id: str):
        """Move from in_use back to available."""
        pipe = redis_client.client.pipeline()
        pipe.lrem(self._key_pool_in_use(), 0, bot_id)
        pipe.lpush(self._key_pool_available(), bot_id)
        await pipe.execute()

    async def register_active_bot(self, company_id: str, bot_id: str):
        await redis_client.client.sadd(self._key_company_bots(company_id), bot_id)

    async def unregister_active_bot(self, company_id: str, bot_id: str):
        await redis_client.client.srem(self._key_company_bots(company_id), bot_id)

    async def get_company_active_bots(self, company_id: str) -> List[str]:
        return await redis_client.client.smembers(self._key_company_bots(company_id))

    async def get_all_active_bot_ids(self) -> List[str]:
        return await redis_client.client.lrange(self._key_pool_in_use(), 0, -1)

state_service = RedisStateService()
