"""
Zoom Bot Configuration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class ZoomConfig(BaseSettings):
    """Zoom Meeting SDK configuration"""

    # ── Zoom App Credentials (RTMS) ────────────────────────
    ZOOM_CLIENT_ID:    str = os.getenv("ZOOM_CLIENT_ID", "")
    ZOOM_CLIENT_SECRET: str = os.getenv("ZOOM_CLIENT_SECRET", "")
    
    # ── Bot Identity ─────────────────────────────────
    BOT_NAME:        str = "Vocaply Bot"
    BOT_EMAIL:       str = "bot@vocaply.com"
    BOT_USER_ID:     str = "vocaply_bot"
    
    # ── Audio Settings ───────────────────────────────
    AUDIO_SAMPLE_RATE:   int = 16000      # 16kHz (Zoom default)
    AUDIO_CHANNELS:      int = 1          # Mono
    AUDIO_BITS_PER_SAMPLE: int = 16       # 16-bit PCM
    AUDIO_BUFFER_SIZE:   int = 1024       # Samples per buffer
    
    # ── Bot Behavior ─────────────────────────────────
    AUTO_MUTE:           bool = True      # Mute bot on join
    AUTO_HIDE_VIDEO:     bool = True      # Turn off video
    AUTO_JOIN_AUDIO:     bool = True      # Join audio on entry
    ENABLE_RECORDING:    bool = True
    
    # ── Media Server ─────────────────────────────────
    MEDIA_SERVER_URL:    str = "ws://localhost:8002/audio"
    
    # ── Timeouts ─────────────────────────────────────
    JOIN_TIMEOUT:        int = 60         # Seconds
    MAX_MEETING_DURATION: int = 10800     # 3 hours
    ALONE_TIMEOUT:       int = 300        # 5 minutes
    
    # ── JWT Settings ─────────────────────────────────
    JWT_ALGORITHM:       str = "HS256"
    JWT_EXPIRATION:      int = 7200       # 2 hours
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = ZoomConfig()