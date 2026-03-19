"""
Slack Client
Handles Slack API operations
"""

from typing import Dict, List, Optional
import httpx


class SlackClient:
    """
    Slack Web API client.
    
    Operations:
    - Send messages (DM, channel)
    - User lookup
    - Channel management
    - File upload
    """

    API_BASE = "https://slack.com/api"

    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MESSAGES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def send_message(
        self,
        channel: str,
        text: Optional[str] = None,
        blocks: Optional[List[Dict]] = None,
        thread_ts: Optional[str] = None,
    ) -> Dict:
        """
        Send a message to a channel or user.
        
        Args:
            channel: Channel ID (C...) or User ID (U...) for DM
            text: Plain text message (fallback)
            blocks: Rich message blocks
            thread_ts: Reply to thread
        
        Returns:
            Response dict with ts (timestamp)
        """
        payload = {"channel": channel}
        
        if text:
            payload["text"] = text
        
        if blocks:
            payload["blocks"] = blocks
        
        if thread_ts:
            payload["thread_ts"] = thread_ts
        
        return await self._api_call("chat.postMessage", payload)

    async def send_dm(
        self,
        user_id: str,
        text: Optional[str] = None,
        blocks: Optional[List[Dict]] = None,
    ) -> Dict:
        """Send direct message to user"""
        # Open DM channel
        dm_response = await self._api_call(
            "conversations.open",
            {"users": user_id}
        )
        
        channel_id = dm_response["channel"]["id"]
        
        # Send message
        return await self.send_message(
            channel=channel_id,
            text=text,
            blocks=blocks,
        )

    async def update_message(
        self,
        channel: str,
        ts: str,
        text: Optional[str] = None,
        blocks: Optional[List[Dict]] = None,
    ) -> Dict:
        """Update existing message"""
        payload = {
            "channel": channel,
            "ts": ts,
        }
        
        if text:
            payload["text"] = text
        
        if blocks:
            payload["blocks"] = blocks
        
        return await self._api_call("chat.update", payload)

    async def delete_message(self, channel: str, ts: str) -> Dict:
        """Delete message"""
        return await self._api_call(
            "chat.delete",
            {"channel": channel, "ts": ts}
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # USERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Look up user by email address.
        
        Returns:
            User dict or None if not found
        """
        try:
            response = await self._api_call(
                "users.lookupByEmail",
                {"email": email}
            )
            return response.get("user")
        except Exception as e:
            print(f"[Slack] User lookup failed: {e}")
            return None

    async def get_user_info(self, user_id: str) -> Dict:
        """Get user profile information"""
        response = await self._api_call(
            "users.info",
            {"user": user_id}
        )
        return response["user"]

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CHANNELS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def list_channels(self) -> List[Dict]:
        """List all channels bot has access to"""
        response = await self._api_call("conversations.list")
        return response.get("channels", [])

    async def get_channel_info(self, channel_id: str) -> Dict:
        """Get channel information"""
        response = await self._api_call(
            "conversations.info",
            {"channel": channel_id}
        )
        return response["channel"]

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FILES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def upload_file(
        self,
        channels: str,
        file_content: bytes,
        filename: str,
        title: Optional[str] = None,
        initial_comment: Optional[str] = None,
    ) -> Dict:
        """Upload file to Slack"""
        payload = {
            "channels": channels,
            "filename": filename,
        }
        
        if title:
            payload["title"] = title
        
        if initial_comment:
            payload["initial_comment"] = initial_comment
        
        files = {"file": (filename, file_content)}
        
        return await self._api_call("files.upload", payload, files=files)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # REACTIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def add_reaction(
        self,
        channel: str,
        timestamp: str,
        emoji: str,
    ) -> Dict:
        """Add emoji reaction to message"""
        return await self._api_call(
            "reactions.add",
            {
                "channel": channel,
                "timestamp": timestamp,
                "name": emoji,  # Without colons (e.g., "thumbsup")
            }
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # API CALL
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _api_call(
        self,
        method: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
    ) -> Dict:
        """Make Slack API call"""
        url = f"{self.API_BASE}/{method}"
        
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
        }
        
        async with httpx.AsyncClient() as client:
            if files:
                # Multipart form data (for file uploads)
                response = await client.post(
                    url,
                    headers=headers,
                    data=data,
                    files=files,
                )
            else:
                # JSON payload
                headers["Content-Type"] = "application/json"
                response = await client.post(
                    url,
                    headers=headers,
                    json=data or {},
                )
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get("ok"):
                error = result.get("error", "unknown_error")
                raise ValueError(f"Slack API error: {error}")
            
            return result