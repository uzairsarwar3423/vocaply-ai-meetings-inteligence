"""
Bot Service Configuration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Bot service settings"""

    # ── Application ──────────────────────────────────
    APP_NAME: str = "Vocaply Bot Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # ── Server ───────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # ── Redis ────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ── Platform Backend API ─────────────────────────
    BACKEND_API_URL: str = "http://localhost:8000"
    BACKEND_API_KEY: str = "your-internal-api-key"
    
    # ── Bot Pool Configuration ───────────────────────
    POOL_MIN_SIZE: int = 2           # Minimum bots in pool
    POOL_MAX_SIZE: int = 10          # Maximum total bots
    POOL_PRE_WARM: int = 3           # Pre-warmed on startup
    POOL_REFILL_THRESHOLD: int = 3   # Refill when available < this
    
    # ── Bot Behavior ─────────────────────────────────
    BOT_DISPLAY_NAME: str = "Vocaply Bot"
    BOT_ENABLE_VIDEO: bool = False
    BOT_ENABLE_AUDIO: bool = False   # Muted by default
    BOT_JOIN_TIMEOUT: int = 60       # Seconds to join meeting
    BOT_ALONE_TIMEOUT: int = 300     # 5 minutes alone = leave
    BOT_MAX_DURATION: int = 10800    # 3 hours max per meeting
    
    # ── Recording ────────────────────────────────────
    RECORDING_PATH: str = "/tmp/recordings"
    RECORDING_FORMAT: str = "webm"
    RECORDING_VIDEO_CODEC: str = "vp8"
    RECORDING_AUDIO_CODEC: str = "opus"
    RECORDING_BITRATE: str = "128k"
    
    # ── Playwright ───────────────────────────────────
    BROWSER_TYPE: str = "chromium"   # chromium, firefox, webkit
    BROWSER_HEADLESS: bool = True
    BROWSER_ARGS: list = [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--use-fake-ui-for-media-stream",  # Auto-allow camera/mic
        "--use-fake-device-for-media-stream",
    ]
    
    # ── Monitoring ───────────────────────────────────
    HEALTH_CHECK_INTERVAL: int = 30  # Seconds between health checks
    HEARTBEAT_INTERVAL: int = 10     # Seconds between heartbeats
    METRICS_ENABLED: bool = True
    
    # ── Webhooks ─────────────────────────────────────
    WEBHOOK_RETRY_ATTEMPTS: int = 3
    WEBHOOK_RETRY_DELAY: int = 5     # Seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()