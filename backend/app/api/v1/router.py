"""
API Router Configuration
Vocaply Platform

Aggregates all API endpoints into versioned router.
"""

from fastapi import APIRouter

from app.api.v1 import (
    auth,           # Authentication endpoints (login, register, refresh)
    meetings,       # Meeting CRUD (Day 4)
    upload,         # File upload to Backblaze B2 (Day 6)
    transcripts,    # Transcription management (Day 7)
    action_items,   # Action item extraction (Day 10)
    summaries,      # AI Meeting Summaries (Day 13)
    websocket,      # WebSocket (Day 14)
    webhooks,       # External/Internal Webhooks (Day 15)
)

# ============================================
# API V1 ROUTER
# ============================================

api_router = APIRouter()

# ── Authentication ──────────────────────────────────────────────
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# ── Meetings (Day 4) ────────────────────────────────────────────
api_router.include_router(
    meetings.router,
    prefix="/meetings",
    tags=["Meetings"]
)

# ── File Upload (Day 6) ─────────────────────────────────────────
api_router.include_router(
    upload.router,
    prefix="/upload",
    tags=["File Upload"]
)

# ── Transcripts (Day 7) ─────────────────────────────────────────
api_router.include_router(
    transcripts.router,
    prefix="/transcripts",
    tags=["Transcripts"]
)

# ── Action Items (Day 10) ────────────────────────────────────────
api_router.include_router(
    action_items.router,
    prefix="/action-items",
    tags=["Action Items"]
)

# POST /meetings/{id}/analyze
api_router.include_router(
    action_items.analysis_router,
    prefix="/meetings",
    tags=["AI Analysis"]
)

# ── Meeting Summaries (Day 13) ───────────────────────────────────
# POST /meetings/{id}/summarize  &  GET /meetings/{id}/summary
api_router.include_router(
    summaries.meetings_summary_router,
    prefix="/meetings",
    tags=["Meeting Summaries"]
)

# PUT/POST /summaries/{id}  &  GET /summaries/{id}/export/{fmt}
api_router.include_router(
    summaries.summaries_router,
    prefix="/summaries",
    tags=["Meeting Summaries"]
)

# ── WebSocket (Day 14) ──────────────────────────────────────────────────────
api_router.include_router(
    websocket.router,
    tags=["WebSocket"]
)

# ── Webhooks (Day 15) ────────────────────────────────────────────────────────
api_router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["Webhooks"]
)

# ── Future Endpoints ────────────────────────────────────────────
# api_router.include_router(
#     integrations.router,
#     prefix="/integrations",
#     tags=["Integrations"]
# )
#
# api_router.include_router(
#     analytics.router,
#     prefix="/analytics",
#     tags=["Analytics"]
# )
#
# api_router.include_router(
#     webhooks.router,
#     prefix="/webhooks",
#     tags=["Webhooks"]
# )