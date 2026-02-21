"""
Bot Control API
Vocaply AI Meeting Intelligence - Day 15
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from shared.models.bot_status import CreateBotRequest, BotStatusResponse, BotInfo
from app.services.bot_manager import bot_manager
from app.services.redis_state import state_service
from app.services.instance_pool import instance_pool

router = APIRouter(prefix="/bots", tags=["Bot Control"])

@router.post("/create", response_model=BotInfo)
async def create_bot(request: CreateBotRequest):
    """Start a new bot for a meeting."""
    return await bot_manager.create_bot(request)

@router.post("/{id}/stop")
async def stop_bot(id: str):
    """Manually stop a bot instance."""
    await bot_manager.stop_bot(id, reason="admin_stop")
    return {"status": "success"}

@router.get("/{id}/status", response_model=BotStatusResponse)
async def get_bot_status(id: str):
    """Check current status of a bot."""
    info = await state_service.get_bot_info(id)
    if not info:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return BotStatusResponse(
        bot_id=info.bot_id,
        status=info.status,
        meeting_id=info.meeting_id,
        platform=info.platform,
        participant_count=info.participant_count,
        created_at=info.created_at,
        updated_at=info.updated_at,
        error_message=info.error_message
    )

@router.get("/active", response_model=List[str])
async def list_active_bots():
    """List all currently in-use bot IDs."""
    return await state_service.get_all_active_bot_ids()

@router.get("/pool/stats")
async def get_pool_stats():
    """Diagnostic info about the instance pool."""
    return await instance_pool.get_status()
