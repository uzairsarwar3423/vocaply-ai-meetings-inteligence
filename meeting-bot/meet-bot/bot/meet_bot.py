"""
Google Meet Bot
Main bot orchestrator
"""

import asyncio
import httpx
from typing import Optional
from datetime import datetime, timezone

def _utcnow() -> datetime:
    """Timezone-aware UTC now (replaces deprecated datetime.utcnow())"""
    return datetime.now(timezone.utc)

from bot.browser_manager import BrowserManager
from bot.meet_actions import MeetActions
from bot.audio_capture import AudioCapture
from bot.page_monitor import PageMonitor
from bot.participant_scraper import ParticipantScraper


class MeetBot:
    """
    Complete Google Meet bot.
    
    Lifecycle:
    1. Launch browser
    2. Join meeting
    3. Start audio capture
    4. Monitor meeting
    5. Leave when done
    """

    def __init__(
        self,
        bot_id: str,
        meeting_id: str,
        meeting_url: str,
        company_id: str,
        webhook_url: str,
        bot_name: str = "Vocaply Bot",
    ):
        self.bot_id = bot_id
        self.meeting_id = meeting_id
        self.meeting_url = meeting_url
        self.company_id = company_id
        self.webhook_url = webhook_url
        self.bot_name = bot_name
        
        # Components
        self.browser: Optional[BrowserManager] = None
        self.actions: Optional[MeetActions] = None
        self.audio: Optional[AudioCapture] = None
        self.monitor: Optional[PageMonitor] = None
        self.participants: Optional[ParticipantScraper] = None
        
        # State
        self.is_running = False
        self.joined_at: Optional[datetime] = None
        self.left_at: Optional[datetime] = None
        
        # HTTP client for webhooks
        self.http_client = httpx.AsyncClient(timeout=10.0)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start(self):
        """Start bot and join meeting"""
        print(f"[MeetBot] Starting for meeting {self.meeting_id}")
        
        try:
            # Initialize browser
            self.browser = BrowserManager(headless=True)
            await self.browser.start()
            
            # Initialize components
            self.actions = MeetActions(self.browser)
            self.audio = AudioCapture(self.meeting_id)
            self.monitor = PageMonitor(self.browser, self.actions)
            self.participants = ParticipantScraper(self.actions)
            
            # Register event callbacks
            self._register_callbacks()
            
            # Join meeting
            await self.actions.join_meeting(self.meeting_url, self.bot_name)
            
            self.is_running = True
            self.joined_at = _utcnow()
            
            # Send "joined" webhook
            await self._send_webhook('bot.joined', {})
            
            # Start audio capture
            await self.audio.start()
            
            # Redirect Chrome audio to virtual sink
            # Note: This needs Chrome PID, which we can get from browser process
            self.audio.redirect_chrome_audio()
            
            # Start monitoring
            await self.monitor.start()
            
            # Start monitoring loop
            asyncio.create_task(self._run_loop())
            
            print(f"[MeetBot] Successfully started")
            
        except Exception as e:
            print(f"[MeetBot] Failed to start: {e}")
            
            # Send error webhook
            await self._send_webhook('bot.error', {'error': str(e)})
            
            # Cleanup
            await self.stop()
            raise

    async def stop(self):
        """Stop bot and cleanup"""
        if not self.is_running and not self.browser:
            return  # Nothing to clean up
        
        print(f"[MeetBot] Stopping")
        
        self.is_running = False
        self.left_at = _utcnow()
        
        # Leave meeting
        if self.actions:
            try:
                await self.actions.leave_meeting()
            except:
                pass
        
        # Stop monitoring
        if self.monitor:
            await self.monitor.stop()
        
        # Stop audio
        if self.audio:
            await self.audio.stop()
        
        # Close browser
        if self.browser:
            await self.browser.stop()
        
        # Send "left" webhook
        await self._send_webhook('bot.left', {
            'stats': self.get_stats(),
        })
        
        # Close HTTP client
        await self.http_client.aclose()
        
        print(f"[MeetBot] Stopped")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MAIN LOOP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _run_loop(self):
        """Main bot loop"""
        while self.is_running:
            try:
                await asyncio.sleep(10)  # Every 10 seconds
                
                # Refresh participants
                await self.participants.refresh()
                
                # Check alone timeout
                if self.monitor.check_alone_timeout(300):  # 5 minutes
                    print("[MeetBot] Alone timeout, leaving")
                    await self.stop()
                    return
                
                # Check max duration (3 hours)
                if self.joined_at:
                    duration = (_utcnow() - self.joined_at).total_seconds()
                    if duration > 10800:  # 3 hours
                        print("[MeetBot] Max duration reached, leaving")
                        await self.stop()
                        return
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[MeetBot] Loop error: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # EVENT CALLBACKS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _register_callbacks(self):
        """Register event callbacks"""
        if not self.monitor:
            return
        
        self.monitor.on('meeting_ended', self._on_meeting_ended)
        self.monitor.on('participant_count_changed', self._on_participant_changed)
        self.monitor.on('page_error', self._on_page_error)

    async def _on_meeting_ended(self, data):
        """Handle meeting ended event"""
        print("[MeetBot] Meeting ended")
        await self._send_webhook('meeting.ended', data)
        await self.stop()

    async def _on_participant_changed(self, data):
        """Handle participant count change"""
        await self._send_webhook('participant.count_changed', data)

    async def _on_page_error(self, data):
        """Handle page error"""
        print(f"[MeetBot] Page error: {data['error']}")
        await self._send_webhook('bot.error', data)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WEBHOOKS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _send_webhook(self, event_type: str, data: dict):
        """Send webhook to bot service"""
        try:
            payload = {
                'event_type': event_type,
                'bot_id': self.bot_id,
                'meeting_id': self.meeting_id,
                'company_id': self.company_id,
                'timestamp': _utcnow().isoformat(),
                'data': data,
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
        duration = 0
        if self.joined_at:
            end = self.left_at or _utcnow()
            duration = (end - self.joined_at).total_seconds()
        
        return {
            'bot_id': self.bot_id,
            'meeting_id': self.meeting_id,
            'is_running': self.is_running,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'left_at': self.left_at.isoformat() if self.left_at else None,
            'duration_seconds': duration,
            'participants': self.participants.get_stats() if self.participants else {},
            'audio': self.audio.get_stats() if self.audio else {},
            'monitor': self.monitor.get_stats() if self.monitor else {},
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN (standalone testing)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def main():
    """Standalone bot test"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python meet_bot.py <meeting_url>")
        sys.exit(1)
    
    meeting_url = sys.argv[1]
    
    bot = MeetBot(
        bot_id="test-bot-1",
        meeting_id="test-meeting",
        meeting_url=meeting_url,
        company_id="test-company",
        webhook_url="http://localhost:8001/webhooks/bot-events",
    )
    
    try:
        await bot.start()
        
        # Keep running
        while bot.is_running:
            await asyncio.sleep(5)
            print(f"[Stats] Participants: {bot.participants.get_count()}")
        
    except KeyboardInterrupt:
        print("\nStopping bot...")
    
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())