"""
Integrations Router Configuration
Aggregates all integration-specific routers.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_db
from app.api.deps import get_current_user_async as get_current_user
from app.models.platform_connection import PlatformConnection
from app.api.v1.integrations import zoom, google, slack

router = APIRouter()

# Include platform-specific routers
router.include_router(zoom.router)
router.include_router(google.router)
router.include_router(slack.router)


@router.get(
    "/connections",
    summary="Get all connected platforms",
)
async def get_connections(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """List all connected platform accounts for the user"""
    stmt = select(PlatformConnection).where(
        PlatformConnection.user_id == current_user.id
    )
    result = await db.execute(stmt)
    connections = result.scalars().all()
    
    return {
        "connections": [
            {
                "id": str(conn.id),
                "platform": conn.platform,
                "platform_user_id": conn.platform_user_id,
                "platform_email": conn.platform_email,
                "is_active": conn.is_active,
                "connected_at": conn.connected_at.isoformat(),
                "last_synced_at": conn.last_synced_at.isoformat() if conn.last_synced_at else None,
            }
            for conn in connections
        ]
    }
