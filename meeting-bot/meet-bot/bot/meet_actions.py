"""
Meet Actions
Google Meet-specific browser actions
"""

import asyncio
from typing import List, Dict, Optional

from bot.browser_manager import BrowserManager


class MeetActions:
    """
    Handles all Google Meet-specific actions:
    - Join meeting
    - Mute/unmute
    - Enable/disable video
    - Get participants
    - Check meeting status
    """

    def __init__(self, browser: BrowserManager):
        self.browser = browser

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # JOIN FLOW
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def join_meeting(self, meeting_url: str, bot_name: str = "Vocaply Bot"):
        """
        Join Google Meet meeting.
        
        Flow:
        1. Navigate to URL
        2. Wait for pre-join screen
        3. Enter name if asked
        4. Turn off camera/mic
        5. Click "Join now"
        6. Wait for meeting to load
        """
        print(f"[Meet] Joining meeting: {meeting_url}")
        
        # Navigate
        await self.browser.navigate(meeting_url)
        
        # Wait for page to load
        await asyncio.sleep(3)
        
        # Handle name input if present
        await self._handle_name_input(bot_name)
        
        # Disable camera and mic
        await self.disable_camera()
        await self.mute_microphone()
        
        # Click join button
        await self._click_join_button()
        
        # Wait for meeting to load
        await self._wait_for_meeting()
        
        print("[Meet] Successfully joined meeting")

    async def _handle_name_input(self, name: str):
        """Handle name input dialog"""
        try:
            # Check if name input exists
            name_input = await self.browser.page.querySelector('input[aria-label*="name" i]')
            
            if name_input:
                print(f"[Meet] Entering name: {name}")
                await self.browser.type_text('input[aria-label*="name" i]', name)
                await asyncio.sleep(0.5)
        except:
            pass  # Name input not present

    async def _click_join_button(self):
        """Click "Join now" button"""
        # Try multiple selectors (Meet UI changes)
        selectors = [
            'button[aria-label*="Join" i]',
            'button:has-text("Join now")',
            '[jsname="Qx7uuf"]',  # Meet's internal jsname
            'div[role="button"]:has-text("Join")',
        ]
        
        for selector in selectors:
            try:
                await self.browser.click(selector, timeout=2000)
                print("[Meet] Clicked join button")
                return
            except:
                continue
        
        # Fallback: use content script
        result = await self.browser.send_message('JOIN')
        if result.get('success'):
            print("[Meet] Joined via content script")
        else:
            raise RuntimeError("Failed to click join button")

    async def _wait_for_meeting(self, timeout: int = 60):
        """Wait for meeting to fully load"""
        print("[Meet] Waiting for meeting to load...")
        
        start = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start) < timeout:
            status = await self.get_meeting_status()
            
            if status['in_meeting']:
                print("[Meet] Meeting loaded")
                return
            
            if status['waiting']:
                print("[Meet] Waiting for host to admit...")
            
            await asyncio.sleep(2)
        
        raise TimeoutError("Timeout waiting for meeting to load")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONTROLS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def disable_camera(self):
        """Turn off camera"""
        result = await self.browser.send_message('DISABLE_CAMERA')
        
        if not result.get('success'):
            # Fallback: try direct click
            try:
                await self.browser.click('[aria-label*="camera" i][aria-label*="turn off" i]', timeout=2000)
            except:
                pass

    async def mute_microphone(self):
        """Mute microphone"""
        result = await self.browser.send_message('MUTE_MIC')
        
        if not result.get('success'):
            # Fallback: try direct click
            try:
                await self.browser.click('[aria-label*="microphone" i][aria-label*="turn off" i]', timeout=2000)
            except:
                pass

    async def leave_meeting(self):
        """Leave meeting"""
        print("[Meet] Leaving meeting...")
        
        try:
            # Click leave/end call button
            await self.browser.click('[aria-label*="Leave call" i]', timeout=5000)
        except:
            # If button not found, just close browser
            print("[Meet] Leave button not found, closing browser")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATUS & INFO
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def get_meeting_status(self) -> Dict:
        """
        Get current meeting status.
        
        Returns:
            {
                "in_meeting": bool,
                "waiting": bool,
                "ended": bool
            }
        """
        result = await self.browser.send_message('GET_STATUS')
        
        return {
            'in_meeting': result.get('inMeeting', False),
            'waiting': result.get('waiting', False),
            'ended': result.get('ended', False),
        }

    async def get_participants(self) -> List[Dict]:
        """
        Get list of participants.
        
        Returns:
            [{"id": "...", "name": "...", "isMuted": bool, "hasVideo": bool}]
        """
        result = await self.browser.send_message('GET_PARTICIPANTS')
        return result.get('participants', [])

    async def get_participant_count(self) -> int:
        """Get number of participants"""
        result = await self.browser.send_message('GET_PARTICIPANT_COUNT')
        return result.get('count', 0)

    async def is_alone(self) -> bool:
        """Check if bot is alone in meeting"""
        count = await self.get_participant_count()
        return count <= 1  # Only bot

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DEBUGGING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def take_screenshot(self, filename: str = "/tmp/meet_screenshot.png"):
        """Take screenshot for debugging"""
        await self.browser.screenshot(filename)
        print(f"[Meet] Screenshot saved: {filename}")