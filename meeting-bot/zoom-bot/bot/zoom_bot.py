"""
Zoom Bot
Top-level bot orchestration
"""

import asyncio
import httpx
from typing import Optional

from bot.meeting_controller import MeetingController
from config.zoom_config import settings


class ZoomBot:
    """
    Top-level Zoom bot that manages meeting sessions.
    
    This class is instantiated per bot instance and manages
    a single meeting session lifecycle.
    """

    def __init__(
        self,
        bot_id: str,
        meeting_id: str,
        meeting_url: str,
        company_id: str,
        webhook_url: str,
    ):
        self.bot_id = bot_id
        self.meeting_id = meeting_id
        self.meeting_url = meeting_url
        self.company_id = company_id
        self.webhook_url = webhook_url
        
        # Controller
        self.controller: Optional[MeetingController] = None
        
        # HTTP client for webhooks
        self.http_client = httpx.AsyncClient(timeout=10.0)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start(self):
        """Start bot and join meeting"""
        print(f"[ZoomBot] Starting bot {self.bot_id} for meeting {self.meeting_id}")
        
        try:
            # Create controller
            self.controller = MeetingController(
                meeting_id=self.meeting_id,
                meeting_url=self.meeting_url,
            )
            
            # Register webhooks
            self._register_webhooks()
            
            # Start controller
            await self.controller.start()
            
            # Send "joined" webhook
            await self._send_webhook("bot.joined", {
                "bot_id": self.bot_id,
                "meeting_id": self.meeting_id,
            })
            
            print(f"[ZoomBot] Bot {self.bot_id} successfully joined")
            
        except Exception as e:
            print(f"[ZoomBot] Failed to start: {e}")
            
            # Send error webhook
            await self._send_webhook("bot.error", {
                "bot_id": self.bot_id,
                "meeting_id": self.meeting_id,
                "error": str(e),
            })
            
            raise

    async def stop(self):
        """Stop bot and leave meeting"""
        print(f"[ZoomBot] Stopping bot {self.bot_id}")
        
        try:
            if self.controller:
                await self.controller.stop()
            
            # Send "left" webhook
            await self._send_webhook("bot.left", {
                "bot_id": self.bot_id,
                "meeting_id": self.meeting_id,
                "stats": self.get_stats(),
            })
            
        except Exception as e:
            print(f"[ZoomBot] Error during stop: {e}")
        
        finally:
            await self.http_client.aclose()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WEBHOOKS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _register_webhooks(self):
        """Register webhook handlers"""
        if not self.controller:
            return
        
        # Forward all events to bot service
        events = [
            "bot.joined",
            "bot.left",
            "bot.error",
            "participant.joined",
            "participant.left",
            "recording.status_changed",
        ]
        
        for event in events:
            self.controller.events.register_webhook(
                event,
                lambda data: self._send_webhook(event, data),
            )

    async def _send_webhook(self, event_type: str, data: dict):
        """Send webhook to bot service"""
        try:
            payload = {
                "event_type": event_type,
                "bot_id": self.bot_id,
                "meeting_id": self.meeting_id,
                "company_id": self.company_id,
                "data": data,
            }
            
            response = await self.http_client.post(
                self.webhook_url,
                json=payload,
            )
            
            response.raise_for_status()
            
        except Exception as e:
            print(f"[Webhook] Failed to send {event_type}: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stats(self) -> dict:
        """Get bot statistics"""
        if not self.controller:
            return {}
        
        return self.controller.get_stats()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN (for standalone testing)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def main():
    """Standalone bot test"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python zoom_bot.py <meeting_url>")
        sys.exit(1)
    
    meeting_url = sys.argv[1]
    
    bot = ZoomBot(
        bot_id="test-bot-1",
        meeting_id="test-meeting",
        meeting_url=meeting_url,
        company_id="test-company",
        webhook_url="http://localhost:8001/webhooks/bot-events",
    )
    
    try:
        await bot.start()
        
        # Keep running
        while bot.controller and bot.controller.is_running:
            await asyncio.sleep(5)
            print(f"[Stats] {bot.get_stats()}")
        
    except KeyboardInterrupt:
        print("\nStopping bot...")
    
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())