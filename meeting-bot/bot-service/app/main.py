"""
Bot Service Main Entry Point
Vocaply AI Meeting Intelligence - Day 15
"""

import sys
import os
from pathlib import Path

# Add project root (meeting-bot) to sys.path to allow importing from 'shared'
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings
from app.api import bot_control, webhooks
from app.services.instance_pool import instance_pool
from app.services.health_monitor import health_monitor
from shared.utils.redis_client import redis_client
from shared.utils.logger import get_logger

logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Bot Service...")
    await redis_client.connect()
    
    # Initialize services
    await instance_pool.start()
    await health_monitor.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Bot Service...")
    await health_monitor.stop()
    await redis_client.disconnect()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# Routes
app.include_router(bot_control.router, prefix=settings.API_V1_STR)
app.include_router(webhooks.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Vocaply Bot Service is running",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
