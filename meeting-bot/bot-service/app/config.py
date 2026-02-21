"""
Bot Service Configuration
Vocaply AI Meeting Intelligence - Day 15
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Vocaply Bot Service"
    API_V1_STR: str = "/api/v1"
    
    # Discovery & State
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Internal Webhook to Backend
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://backend:8000/api/v1")
    BACKEND_API_KEY: str = os.getenv("BACKEND_API_KEY", "internal-secret")
    
    # Bot Pool Settings
    BOT_POOL_SIZE: int = 10
    BOT_COOLDOWN_SECONDS: int = 300  # 5 minutes before recycling
    
    # Docker/Containerization defaults (used by Manager to spawn bots)
    BOT_NAMESPACE: str = os.getenv("BOT_NAMESPACE", "vocaply-bots")
    
    # Health Monitoring
    HEALTH_CHECK_INTERVAL: int = 60  # seconds

settings = Settings()
