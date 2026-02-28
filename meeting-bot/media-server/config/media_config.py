"""
Media Server Configuration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class MediaConfig(BaseSettings):
    """Media server configuration"""

    # ── Server ───────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    
    # ── Audio Settings ───────────────────────────────
    SAMPLE_RATE:       int = 16000     # 16kHz
    CHANNELS:          int = 1         # Mono
    BITS_PER_SAMPLE:   int = 16        # 16-bit
    BUFFER_SIZE:       int = 4096      # Bytes per chunk
    
    # ── Recording ────────────────────────────────────
    RECORDING_DIR:     str = "/tmp/recordings"
    TEMP_DIR:          str = "/tmp/recordings/temp"
    OUTPUT_FORMAT:     str = "mp3"     # wav, mp3, m4a
    
    # ── Transcoding ──────────────────────────────────
    MP3_BITRATE:       str = "128k"
    MP3_QUALITY:       int = 2         # VBR quality (0=best, 9=worst)
    
    # ── Storage (Backblaze) ──────────────────────────
    B2_ENABLED:        bool = True
    B2_KEY_ID:         str = os.getenv("BACKBLAZE_KEY_ID", "")
    B2_APP_KEY:        str = os.getenv("BACKBLAZE_APPLICATION_KEY", "")
    B2_BUCKET:         str = os.getenv("BACKBLAZE_BUCKET_NAME", "vocaply-recordings")
    B2_REGION:         str = os.getenv("BACKBLAZE_REGION", "us-west-004")
    
    # ── Webhook ──────────────────────────────────────
    WEBHOOK_URL:       str = "http://localhost:8000/api/v1/webhooks/recording-complete"
    WEBHOOK_API_KEY:   str = os.getenv("BACKEND_API_KEY", "")
    
    # ── Stream Management ────────────────────────────
    MAX_STREAMS:       int = 50        # Max concurrent streams
    STREAM_TIMEOUT:    int = 300       # 5 min idle timeout
    HEARTBEAT_INTERVAL: int = 10       # Seconds
    
    # ── Cleanup ──────────────────────────────────────
    KEEP_LOCAL_FILES:  bool = False    # Keep files after upload
    CLEANUP_INTERVAL:  int = 3600      # 1 hour
    
    # ── Monitoring ───────────────────────────────────
    METRICS_ENABLED:   bool = True
    LOG_LEVEL:         str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = MediaConfig()