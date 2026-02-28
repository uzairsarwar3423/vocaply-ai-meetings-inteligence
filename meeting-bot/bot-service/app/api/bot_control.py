"""
Bot Control API
FastAPI endpoints for bot management
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional

from app.services.bot_manager import BotManager
from shared.models.bot_status import BotPlatform


router = APIRouter(prefix="/bots", tags=["Bot Control"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REQUEST/RESPONSE MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CreateBotRequest(BaseModel):
    meeting_url:  str = Field(..., description="Meeting URL to join")
    meeting_id:   str = Field(..., description="Meeting ID from platform backend")
    company_id:   str = Field(..., description="Company ID")
    platform:     str = Field(..., description="Platform: zoom, google_meet, teams")


class BotResponse(BaseModel):
    bot_id:       str
    status:       str
    meeting_id:   Optional[str] = None
    created_at:   str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DEPENDENCY INJECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_bot_manager() -> BotManager:
    """Get bot manager from app state"""
    from app.main import bot_manager
    return bot_manager


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post(
    "/create",
    response_model=BotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create and assign bot to meeting",
    description=(
        "Assigns an available bot from the pool to the specified meeting. "
        "Bot will automatically join and start recording."
    ),
)
async def create_bot(
    body: CreateBotRequest,
    manager: BotManager = Depends(get_bot_manager),
):
    """Create bot for meeting"""
    try:
        result = await manager.create_bot_for_meeting(
            meeting_url=body.meeting_url,
            meeting_id=body.meeting_id,
            company_id=body.company_id,
            platform=body.platform,
        )
        return BotResponse(**result)
    
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.post(
    "/{bot_id}/stop",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Stop bot and leave meeting",
)
async def stop_bot(
    bot_id: str,
    manager: BotManager = Depends(get_bot_manager),
):
    """Manually stop a bot"""
    try:
        await manager.stop_bot(bot_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/{bot_id}/status",
    summary="Get bot status",
)
async def get_bot_status(
    bot_id: str,
    manager: BotManager = Depends(get_bot_manager),
):
    """Get current status of a bot"""
    try:
        return await manager.get_bot_status(bot_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/active",
    summary="List active bots",
    description="Get all active bots, optionally filtered by company",
)
async def get_active_bots(
    company_id: Optional[str] = None,
    manager: BotManager = Depends(get_bot_manager),
):
    """List all active bots"""
    bots = await manager.get_active_bots(company_id)
    return {"bots": bots, "count": len(bots)}


@router.get(
    "/pool/status",
    summary="Get pool status",
    description="View bot pool metrics and availability",
)
async def get_pool_status(
    manager: BotManager = Depends(get_bot_manager),
):
    """Get bot pool status"""
    return await manager.pool.get_pool_status()