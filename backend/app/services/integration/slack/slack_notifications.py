"""
Slack Notifications
Sends formatted notifications to Slack
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.services.integration.slack.slack_client import SlackClient


class SlackNotifications:
    """
    Slack notification service.
    
    Sends formatted notifications for:
    - Action items assigned
    - Action items due
    - Meetings starting
    - Daily digest
    """

    def __init__(self, slack_client: SlackClient):
        self.client = slack_client

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ACTION ITEMS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def notify_action_item_assigned(
        self,
        user_slack_id: str,
        action_item: Dict,
        meeting: Dict,
    ):
        """
        Notify user when action item is assigned to them.
        
        Includes:
        - Action item title and description
        - Due date
        - Meeting context
        - "Mark Complete" button
        """
        due_date = action_item.get("due_date")
        due_text = f"📅 Due: {self._format_date(due_date)}" if due_date else "📅 No due date"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "✅ New Action Item Assigned",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{action_item['title']}*\n\n{action_item.get('description', '')}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Meeting:*\n{meeting['title']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": due_text
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Mark Complete ✓"
                        },
                        "style": "primary",
                        "value": str(action_item["id"]),
                        "action_id": "mark_complete"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Meeting"
                        },
                        "url": f"{self._get_app_url()}/meetings/{meeting['id']}",
                        "action_id": "view_meeting"
                    }
                ]
            }
        ]
        
        await self.client.send_dm(
            user_id=user_slack_id,
            text=f"New action item: {action_item['title']}",
            blocks=blocks,
        )

    async def notify_action_item_due_soon(
        self,
        user_slack_id: str,
        action_items: List[Dict],
    ):
        """
        Notify user of action items due tomorrow.
        
        Sent daily at 9 AM.
        """
        if not action_items:
            return
        
        items_text = "\n".join([
            f"• *{item['title']}*"
            for item in action_items
        ])
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "⏰ Action Items Due Tomorrow",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"You have {len(action_items)} action item(s) due tomorrow:\n\n{items_text}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View All Action Items"
                        },
                        "url": f"{self._get_app_url()}/action-items",
                        "action_id": "view_action_items"
                    }
                ]
            }
        ]
        
        await self.client.send_dm(
            user_id=user_slack_id,
            text=f"{len(action_items)} action items due tomorrow",
            blocks=blocks,
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MEETINGS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def notify_meeting_starting(
        self,
        user_slack_id: str,
        meeting: Dict,
        minutes_until: int = 5,
    ):
        """
        Notify user that meeting is starting soon.
        
        Sent 5 minutes before scheduled time.
        """
        start_time = meeting["scheduled_time"]
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📞 Meeting in {minutes_until} minutes",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{meeting['title']}*\n\n{self._format_datetime(start_time)}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Join Meeting"
                        },
                        "style": "primary",
                        "url": meeting.get("meeting_url", ""),
                        "action_id": "join_meeting"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Details"
                        },
                        "url": f"{self._get_app_url()}/meetings/{meeting['id']}",
                        "action_id": "view_details"
                    }
                ]
            }
        ]
        
        await self.client.send_dm(
            user_id=user_slack_id,
            text=f"Meeting starting in {minutes_until} min: {meeting['title']}",
            blocks=blocks,
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DIGEST
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def send_daily_digest(
        self,
        user_slack_id: str,
        summary: Dict,
    ):
        """
        Send daily digest to user.
        
        Includes:
        - Pending action items
        - Meetings today
        - Upcoming meetings this week
        
        Sent at 8 AM daily.
        """
        pending_count = summary.get("pending_action_items", 0)
        meetings_today = summary.get("meetings_today", 0)
        meetings_week = summary.get("meetings_week", 0)
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Daily Digest",
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Pending Action Items*\n{pending_count}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Meetings Today*\n{meetings_today}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Meetings This Week*\n{meetings_week}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Dashboard"
                        },
                        "url": f"{self._get_app_url()}/dashboard",
                        "action_id": "view_dashboard"
                    }
                ]
            }
        ]
        
        await self.client.send_dm(
            user_id=user_slack_id,
            text=f"Daily digest: {pending_count} pending items, {meetings_today} meetings today",
            blocks=blocks,
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CHANNEL NOTIFICATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def post_meeting_summary(
        self,
        channel_id: str,
        meeting: Dict,
        summary: Dict,
    ):
        """
        Post meeting summary to channel.
        
        Sent after meeting completes and transcript is processed.
        """
        action_items = summary.get("action_items", [])
        key_points = summary.get("key_points", [])
        
        action_items_text = "\n".join([
            f"• {item['title']}"
            for item in action_items[:5]
        ]) if action_items else "_No action items_"
        
        key_points_text = "\n".join([
            f"• {point}"
            for point in key_points[:5]
        ]) if key_points else "_No key points_"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📝 Meeting Summary: {meeting['title']}",
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Duration:*\n{meeting.get('duration_minutes', 0)} min"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Participants:*\n{meeting.get('participant_count', 0)}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Action Items:*\n{action_items_text}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Key Points:*\n{key_points_text}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Full Summary"
                        },
                        "url": f"{self._get_app_url()}/meetings/{meeting['id']}",
                        "action_id": "view_summary"
                    }
                ]
            }
        ]
        
        await self.client.send_message(
            channel=channel_id,
            text=f"Meeting summary: {meeting['title']}",
            blocks=blocks,
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HELPERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _format_date(self, date_str: str) -> str:
        """Format date as human-readable"""
        if not date_str:
            return "No date set"
        
        date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return date.strftime("%B %d, %Y")

    def _format_datetime(self, datetime_str: str) -> str:
        """Format datetime as human-readable"""
        dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d at %I:%M %p")

    def _get_app_url(self) -> str:
        """Get application base URL"""
        import os
        return os.getenv("APP_URL", "http://localhost:3000")