"""
Slack Integration API Endpoints
"""

import uuid
import secrets
import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.platform_connection import PlatformConnection
from app.services.integration.slack.slack_oauth import SlackOAuth
from app.services.integration.slack.slack_client import SlackClient
from app.services.integration.slack.slack_notifications import SlackNotifications
from app.services.integration.slack.slack_webhooks import SlackWebhooksHandler


router = APIRouter(prefix="/integrations/slack", tags=["Slack Integration"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestMessageRequest(BaseModel):
    channel_or_user: str  # Channel ID or User ID
    message: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OAUTH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/connect")
async def connect_slack(current_user=Depends(get_current_user)):
    """Initiate Slack OAuth flow"""
    state = secrets.token_urlsafe(32)
    
    slack_oauth = SlackOAuth()
    redirect_uri = "http://localhost:3000/integrations/slack/callback"
    
    auth_url = slack_oauth.get_oauth_url(state=state, redirect_uri=redirect_uri)
    
    return {"authorization_url": auth_url, "state": state}


@router.get("/callback")
async def oauth_callback(
    code: str,
    state: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Handle Slack OAuth callback"""
    slack_oauth = SlackOAuth()
    redirect_uri = "http://localhost:3000/integrations/slack/callback"
    
    # Exchange code for token
    oauth_response = await slack_oauth.exchange_code_for_token(code, redirect_uri)
    
    # Extract tokens
    tokens = slack_oauth.extract_tokens(oauth_response)
    
    # Check if connection exists
    stmt = select(PlatformConnection).where(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.platform == "slack"
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if connection:
        # Update existing
        connection.set_access_token(tokens["bot_token"])
        connection.platform_user_id = tokens.get("bot_user_id")
        connection.platform_metadata = tokens
        connection.is_active = True
    else:
        # Create new
        connection = PlatformConnection(
            user_id=current_user.id,
            company_id=current_user.company_id,
            platform="slack",
            platform_user_id=tokens.get("bot_user_id"),
            platform_email=tokens.get("team_name"),
            scopes=tokens.get("scope", "").split(","),
            platform_metadata=tokens,
        )
        connection.set_access_token(tokens["bot_token"])
        
        db.add(connection)
    
    await db.commit()
    
    return {
        "success": True,
        "platform": "slack",
        "team_name": tokens.get("team_name"),
        "bot_user_id": tokens.get("bot_user_id"),
    }


@router.post("/disconnect", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_slack(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect Slack"""
    stmt = select(PlatformConnection).where(
        PlatformConnection.user_id == current_user.id,
        PlatformConnection.platform == "slack"
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if connection:
        connection.is_active = False
        await db.commit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def _get_slack_connection(
    user_id: uuid.UUID,
    db: AsyncSession
) -> PlatformConnection:
    """Get user's Slack connection"""
    stmt = select(PlatformConnection).where(
        PlatformConnection.user_id == user_id,
        PlatformConnection.platform == "slack",
        PlatformConnection.is_active == True,
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(status_code=400, detail="Slack not connected")
    
    return connection


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MESSAGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/test-message")
async def send_test_message(
    request: TestMessageRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send test message to Slack"""
    connection = await _get_slack_connection(current_user.id, db)
    
    bot_token = connection.get_access_token()
    slack_client = SlackClient(bot_token)
    
    result = await slack_client.send_message(
        channel=request.channel_or_user,
        text=request.message,
    )
    
    return {
        "success": True,
        "message_ts": result.get("ts"),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WEBHOOKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/webhook/events")
async def slack_events_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Slack Events API webhook"""
    body = await request.body()
    
    # Verify signature
    slack_oauth = SlackOAuth()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")
    
    if not slack_oauth.verify_signature(timestamp, body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    data = await request.json()
    
    # Handle URL verification challenge
    if data.get("type") == "url_verification":
        return {"challenge": data.get("challenge")}
    
    # Handle event
    # Get bot token (in production, look up by team_id)
    # For now, get first active Slack connection
    stmt = select(PlatformConnection).where(
        PlatformConnection.platform == "slack",
        PlatformConnection.is_active == True,
    ).limit(1)
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if connection:
        bot_token = connection.get_access_token()
        slack_client = SlackClient(bot_token)
        webhook_handler = SlackWebhooksHandler(db, slack_client)
        
        await webhook_handler.handle_event(data)
    
    return {"ok": True}


@router.post("/webhook/interactions")
async def slack_interactions_webhook(
    request: Request,
    payload: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle Slack interactive components (button clicks)"""
    # Verify signature
    body = await request.body()
    slack_oauth = SlackOAuth()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")
    
    if not slack_oauth.verify_signature(timestamp, body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse payload
    data = json.loads(payload)
    
    # Get bot token
    stmt = select(PlatformConnection).where(
        PlatformConnection.platform == "slack",
        PlatformConnection.is_active == True,
    ).limit(1)
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if connection:
        bot_token = connection.get_access_token()
        slack_client = SlackClient(bot_token)
        webhook_handler = SlackWebhooksHandler(db, slack_client)
        
        await webhook_handler.handle_interaction(data)
    
    return {"ok": True}


@router.post("/webhook/slash-command")
async def slack_slash_command(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle /meeting-intel slash command"""
    # Verify signature
    body = await request.body()
    slack_oauth = SlackOAuth()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")
    
    if not slack_oauth.verify_signature(timestamp, body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse form data
    form_data = await request.form()
    command_data = dict(form_data)
    
    # Get bot token
    stmt = select(PlatformConnection).where(
        PlatformConnection.platform == "slack",
        PlatformConnection.is_active == True,
    ).limit(1)
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if connection:
        bot_token = connection.get_access_token()
        slack_client = SlackClient(bot_token)
        webhook_handler = SlackWebhooksHandler(db, slack_client)
        
        response = await webhook_handler.handle_slash_command(command_data)
        return response
    
    return {"text": "Slack not configured"}