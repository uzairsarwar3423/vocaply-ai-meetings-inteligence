"""
Slack Webhooks Handler
Processes events and interactions from Slack
"""

from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.action_item import ActionItem, ActionItemStatus
from app.services.integration.slack.slack_client import SlackClient


class SlackWebhooksHandler:
    """
    Handles Slack webhook events.
    
    Events:
    - app_mention - Bot @mentions
    - message - Channel messages
    - slash_commands - /meeting-intel
    - interactivity - Button clicks
    """

    def __init__(self, db: AsyncSession, slack_client: SlackClient):
        self.db = db
        self.client = slack_client

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # EVENTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def handle_event(self, event_data: Dict):
        """Route event to appropriate handler"""
        event_type = event_data.get("type")
        event = event_data.get("event", {})
        
        handlers = {
            "app_mention": self._handle_app_mention,
            "message": self._handle_message,
        }
        
        handler = handlers.get(event.get("type"))
        if handler:
            await handler(event)

    async def _handle_app_mention(self, event: Dict):
        """Handle @bot mentions"""
        channel = event["channel"]
        text = event["text"]
        user = event["user"]
        
        # Respond to mention
        await self.client.send_message(
            channel=channel,
            text=f"Hi <@{user}>! 👋 Use `/meeting-intel` to see your pending action items.",
        )

    async def _handle_message(self, event: Dict):
        """Handle channel messages"""
        # Only respond to direct mentions
        if event.get("subtype") == "bot_message":
            return

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SLASH COMMANDS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def handle_slash_command(self, command_data: Dict) -> Dict:
        """
        Handle /meeting-intel slash command.
        
        Shows user their pending action items.
        """
        user_id = command_data["user_id"]
        
        # Get user's pending action items from database
        # (In production, look up user by Slack ID)
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📋 Your Action Items",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You have *3 pending action items*:\n\n• Review Q4 budget\n• Schedule team sync\n• Update project timeline"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View All"
                        },
                        "url": "http://localhost:3000/action-items",
                        "action_id": "view_all_items"
                    }
                ]
            }
        ]
        
        return {
            "response_type": "ephemeral",  # Only visible to user
            "blocks": blocks,
        }

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # INTERACTIONS (Button Clicks)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def handle_interaction(self, payload: Dict):
        """Handle button clicks and other interactions"""
        action_id = payload["actions"][0]["action_id"]
        
        handlers = {
            "mark_complete": self._handle_mark_complete,
        }
        
        handler = handlers.get(action_id)
        if handler:
            await handler(payload)

    async def _handle_mark_complete(self, payload: Dict):
        """
        Handle "Mark Complete" button click.
        
        Updates action item status and sends confirmation.
        """
        action_item_id = payload["actions"][0]["value"]
        user_id = payload["user"]["id"]
        channel = payload["channel"]["id"]
        message_ts = payload["message"]["ts"]
        
        # Update action item in database
        stmt = select(ActionItem).where(ActionItem.id == action_item_id)
        result = await self.db.execute(stmt)
        action_item = result.scalar_one_or_none()
        
        if action_item:
            action_item.status = ActionItemStatus.COMPLETED
            await self.db.commit()
            
            # Update message to show completion
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *Action item completed!*\n~{action_item.title}~"
                    }
                }
            ]
            
            await self.client.update_message(
                channel=channel,
                ts=message_ts,
                text="Action item completed",
                blocks=blocks,
            )
            
            # Send confirmation
            await self.client.send_dm(
                user_id=user_id,
                text="Great job! ✅ Action item marked as complete.",
            )