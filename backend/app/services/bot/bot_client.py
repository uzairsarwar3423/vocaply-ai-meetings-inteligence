"""
Bot Client
HTTP client for bot service API
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

import httpx

from app.core.config import settings


class BotServiceError(Exception):
    """Bot service error"""
    pass


class BotClient:
    """
    HTTP client for bot service.
    
    Endpoints:
    - POST /bots/create - Create bot
    - POST /bots/{id}/stop - Stop bot
    - GET /bots/{id}/status - Get status
    - GET /bots/active - List active bots
    - GET /bots/pool/status - Pool metrics
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        self.base_url = base_url or settings.BOT_SERVICE_URL
        self.api_key = api_key or settings.BOT_SERVICE_API_KEY
        self.timeout = timeout
        
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def connect(self):
        """Initialize HTTP client"""
        if self.client:
            return
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )

    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # BOT OPERATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def create_bot(
        self,
        meeting_url: str,
        meeting_id: str,
        company_id: str,
        platform: str,
    ) -> Dict[str, Any]:
        """
        Create a bot for a meeting.
        
        Args:
            meeting_url: Meeting URL to join
            meeting_id: Meeting ID
            company_id: Company ID
            platform: Platform (zoom, google_meet, teams)
        
        Returns:
            {
                "bot_id": "...",
                "status": "assigned",
                "meeting_id": "...",
                "created_at": "..."
            }
        
        Raises:
            BotServiceError: If request fails
        """
        if not self.client:
            await self.connect()
        
        try:
            response = await self.client.post(
                "/bots/create",
                json={
                    "meeting_url": meeting_url,
                    "meeting_id": meeting_id,
                    "company_id": company_id,
                    "platform": platform,
                },
            )
            
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", str(e))
            raise BotServiceError(f"Failed to create bot: {error_detail}")
        except httpx.RequestError as e:
            raise BotServiceError(f"Bot service unavailable: {e}")

    async def stop_bot(self, bot_id: str) -> bool:
        """
        Stop a bot.
        
        Returns:
            True on success
        """
        if not self.client:
            await self.connect()
        
        try:
            response = await self.client.post(f"/bots/{bot_id}/stop")
            response.raise_for_status()
            return True
            
        except httpx.HTTPStatusError as e:
            raise BotServiceError(f"Failed to stop bot: {e}")

    async def get_bot_status(self, bot_id: str) -> Dict[str, Any]:
        """
        Get bot status.
        
        Returns:
            {
                "bot_id": "...",
                "status": "in_meeting",
                "meeting_id": "...",
                "participant_count": 5,
                ...
            }
        """
        if not self.client:
            await self.connect()
        
        try:
            response = await self.client.get(f"/bots/{bot_id}/status")
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise BotServiceError(f"Bot {bot_id} not found")
            raise BotServiceError(f"Failed to get bot status: {e}")

    async def get_active_bots(self, company_id: Optional[str] = None) -> list:
        """
        Get all active bots.
        
        Args:
            company_id: Filter by company (optional)
        
        Returns:
            List of bot data dicts
        """
        if not self.client:
            await self.connect()
        
        try:
            params = {}
            if company_id:
                params["company_id"] = company_id
            
            response = await self.client.get("/bots/active", params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get("bots", [])
            
        except httpx.HTTPStatusError as e:
            raise BotServiceError(f"Failed to get active bots: {e}")

    async def get_pool_status(self) -> Dict[str, Any]:
        """
        Get bot pool status.
        
        Returns:
            {
                "total": 10,
                "available": 7,
                "in_use": 3,
                "max_size": 20,
                ...
            }
        """
        if not self.client:
            await self.connect()
        
        try:
            response = await self.client.get("/bots/pool/status")
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise BotServiceError(f"Failed to get pool status: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HEALTH CHECK
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def health_check(self) -> bool:
        """
        Check if bot service is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        if not self.client:
            await self.connect()
        
        try:
            response = await self.client.get("/health", timeout=5.0)
            return response.status_code == 200
        except:
            return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FACTORY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_bot_client: Optional[BotClient] = None


async def get_bot_client() -> BotClient:
    """Get or create bot client singleton"""
    global _bot_client
    
    if not _bot_client:
        _bot_client = BotClient()
        await _bot_client.connect()
    
    return _bot_client