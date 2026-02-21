"""
Bot Instance Model
Vocaply AI Meeting Intelligence - Day 15

Represents a low-level bot instance (container/process).
"""

from typing import Optional
from pydantic import BaseModel
from shared.models.bot_status import BotStatus

class BotInstance(BaseModel):
    id: str
    container_id: Optional[str] = None
    ip_address: Optional[str] = None
    port: int = 8080
    status: BotStatus = BotStatus.IDLE
    
    @property
    def api_url(self) -> str:
        return f"http://{self.ip_address}:{self.port}"
