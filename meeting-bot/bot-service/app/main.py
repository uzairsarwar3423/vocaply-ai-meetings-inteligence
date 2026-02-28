"""
Bot Service Main Application
FastAPI server for bot orchestration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api import bot_control, webhooks
from app.services.bot_manager import BotManager
from app.services.health_monitor import HealthMonitor
from shared.utils.redis_client import get_redis
from shared.utils.logger import logger


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GLOBAL STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

bot_manager: BotManager = None
health_monitor: HealthMonitor = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LIFESPAN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown"""
    global bot_manager, health_monitor
    
    # ── Startup ──
    logger.info(f"🤖 {settings.APP_NAME} starting...")
    
    # Connect Redis
    redis = await get_redis()
    
    # Initialize services
    bot_manager = BotManager(redis)
    await bot_manager.start()
    
    health_monitor = HealthMonitor(redis)
    await health_monitor.start()
    
    logger.info(f"✅ {settings.APP_NAME} ready")
    
    yield
    
    # ── Shutdown ──
    logger.info(f"🛑 {settings.APP_NAME} shutting down...")
    
    await bot_manager.stop()
    await health_monitor.stop()
    await redis.disconnect()
    
    logger.info("Shutdown complete")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CREATE APP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title=settings.APP_NAME,
    description="Bot orchestration service for meeting automation",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bot_control.router)
app.include_router(webhooks.router)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROOT ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Root"])
async def health():
    """Health check endpoint"""
    return await health_monitor.get_health()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN (development)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )