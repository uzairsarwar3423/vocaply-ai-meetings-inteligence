"""
Analytics API
Vocaply Platform - Day 27

Endpoints:
  GET  /analytics/overview          Company-level KPIs
  GET  /analytics/completion-rate   Completion rate trend
  GET  /analytics/team-performance  Per-user productivity
  GET  /analytics/time-trends       Heatmap + activity trends
  GET  /analytics/export            Download full analytics JSON
"""
from __future__ import annotations

import json
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_async_db
from app.services.analytics.analytics_service import AnalyticsService

router = APIRouter(tags=["Analytics"])


# ── Dependency ──────────────────────────────────────────────────────────────

async def get_analytics_service(
    db: AsyncSession = Depends(get_async_db),
) -> AnalyticsService:
    return AnalyticsService(db)


# ============================================================
# GET /analytics/overview
# ============================================================

@router.get(
    "/overview",
    summary="Company analytics overview — KPI cards data",
)
async def get_overview(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back"),
    current_user  = Depends(get_current_user),
    svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Returns aggregated KPIs for the current user's company:
    - total action items created, completion rate, avg completion time, overdue count
    - total meetings, avg action items per meeting
    """
    return await svc.get_overview(
        company_id=str(current_user.company_id),
        days=days,
    )


# ============================================================
# GET /analytics/completion-rate
# ============================================================

@router.get(
    "/completion-rate",
    summary="Action-item completion rate trend over time",
)
async def get_completion_rate(
    days:        int     = Query(default=30, ge=1, le=365),
    granularity: Literal["daily", "weekly", "monthly"] = Query(default="daily"),
    current_user         = Depends(get_current_user),
    svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Returns time-series data suitable for a line chart:
    [{ date, completion_rate, total, completed }, ...]
    """
    return await svc.get_completion_rate(
        company_id  = str(current_user.company_id),
        days        = days,
        granularity = granularity,
    )


# ============================================================
# GET /analytics/team-performance
# ============================================================

@router.get(
    "/team-performance",
    summary="Per-user productivity stats",
)
async def get_team_performance(
    days: int = Query(default=30, ge=1, le=365),
    current_user         = Depends(get_current_user),
    svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Returns per-team-member stats suitable for a bar chart:
    [{ user_id, name, assigned, completed, completion_rate, ... }, ...]
    """
    return await svc.get_team_performance(
        company_id=str(current_user.company_id),
        days=days,
    )


# ============================================================
# GET /analytics/time-trends
# ============================================================

@router.get(
    "/time-trends",
    summary="Meeting heatmap + action item trends",
)
async def get_time_trends(
    days:        int     = Query(default=30, ge=1, le=365),
    granularity: Literal["daily", "weekly", "monthly"] = Query(default="daily"),
    current_user         = Depends(get_current_user),
    svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Returns:
    - heatmap data (day × hour meetings count)
    - action_item_trends (created vs completed per period)
    - meeting_efficiency (action items per meeting per day)
    """
    return await svc.get_time_trends(
        company_id  = str(current_user.company_id),
        days        = days,
        granularity = granularity,
    )


# ============================================================
# GET /analytics/export
# ============================================================

@router.get(
    "/export",
    summary="Export full analytics data as JSON",
)
async def export_analytics(
    days: int = Query(default=30, ge=1, le=365),
    current_user         = Depends(get_current_user),
    svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Returns a complete JSON payload of all analytics data for download.
    """
    data = await svc.export_data(
        company_id=str(current_user.company_id),
        days=days,
    )
    payload = json.dumps(data, indent=2, default=str)
    return Response(
        content      = payload,
        media_type   = "application/json",
        headers      = {
            "Content-Disposition": f"attachment; filename=analytics_{days}d.json"
        },
    )
