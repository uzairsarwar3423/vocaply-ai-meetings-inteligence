"""
Bot Instance Model
Manages a single bot with browser automation
"""

import asyncio
import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from app.config import settings
from shared.models.bot_status import BotStatus, BotPlatform, BotInstance as BotData
from shared.utils.logger import logger


class BotInstance:
    """
    Single bot instance with headless browser.
    Each bot runs in isolated Playwright context.
    """

    def __init__(self, bot_id: Optional[str] = None):
        self.bot_id = bot_id or str(uuid.uuid4())
        self.data = BotData(
            bot_id=self.bot_id,
            status=BotStatus.INITIALIZING,
            created_at=datetime.utcnow(),
        )
        
        # Playwright objects
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Recording
        self.recording_task: Optional[asyncio.Task] = None
        self.stop_recording = asyncio.Event()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def initialize(self):
        """Start browser and prepare bot"""
        try:
            logger.info(f"Initializing bot {self.bot_id}")
            
            # Launch Playwright
            self.playwright = await async_playwright().start()
            
            # Launch browser
            browser_type = getattr(self.playwright, settings.BROWSER_TYPE)
            self.browser = await browser_type.launch(
                headless=settings.BROWSER_HEADLESS,
                args=settings.BROWSER_ARGS,
            )
            
            # Create context with permissions
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 720},
                permissions=["microphone", "camera"],
                record_video_dir=settings.RECORDING_PATH if settings.RECORDING_PATH else None,
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            # Setup event listeners
            self.page.on("console", self._on_console)
            self.page.on("pageerror", self._on_error)
            
            self.data.status = BotStatus.AVAILABLE
            logger.info(f"Bot {self.bot_id} initialized and available")
            
        except Exception as e:
            logger.error(f"Bot {self.bot_id} initialization failed: {e}", exc_info=True)
            self.data.status = BotStatus.FAILED
            self.data.error = str(e)
            raise

    async def assign(
        self,
        meeting_url: str,
        meeting_id: str,
        company_id: str,
        platform: BotPlatform,
    ):
        """Assign bot to a meeting"""
        if self.data.status != BotStatus.AVAILABLE:
            raise ValueError(f"Bot {self.bot_id} is not available (status: {self.data.status})")
        
        self.data.status = BotStatus.ASSIGNED
        self.data.meeting_url = meeting_url
        self.data.meeting_id = meeting_id
        self.data.company_id = company_id
        self.data.platform = platform
        self.data.assigned_at = datetime.utcnow()
        
        logger.info(
            f"Bot {self.bot_id} assigned to meeting {meeting_id} ({platform})",
            extra={"bot_id": self.bot_id, "meeting_id": meeting_id},
        )

    async def join(self):
        """Navigate to meeting and join"""
        if not self.page or not self.data.meeting_url:
            raise ValueError("Bot not properly initialized or assigned")
        
        self.data.status = BotStatus.JOINING
        logger.info(f"Bot {self.bot_id} joining meeting", extra={"bot_id": self.bot_id})
        
        try:
            # Platform-specific join logic
            if self.data.platform == BotPlatform.ZOOM:
                await self._join_zoom()
            elif self.data.platform == BotPlatform.GOOGLE_MEET:
                await self._join_google_meet()
            elif self.data.platform == BotPlatform.TEAMS:
                await self._join_teams()
            else:
                raise NotImplementedError(f"Platform {self.data.platform} not supported")
            
            self.data.status = BotStatus.IN_MEETING
            self.data.joined_at = datetime.utcnow()
            logger.info(f"Bot {self.bot_id} successfully joined meeting")
            
        except asyncio.TimeoutError:
            self.data.status = BotStatus.FAILED
            self.data.error = "Timeout joining meeting"
            logger.error(f"Bot {self.bot_id} timeout joining meeting")
            raise
        except Exception as e:
            self.data.status = BotStatus.FAILED
            self.data.error = str(e)
            logger.error(f"Bot {self.bot_id} failed to join: {e}", exc_info=True)
            raise

    async def start_recording(self):
        """Begin audio/video recording"""
        if self.data.status != BotStatus.IN_MEETING:
            raise ValueError("Bot must be in meeting to start recording")
        
        self.data.status = BotStatus.RECORDING
        self.data.recording_started = datetime.utcnow()
        
        # Build recording path
        recording_file = Path(settings.RECORDING_PATH) / f"{self.data.meeting_id}.{settings.RECORDING_FORMAT}"
        self.data.recording_path = str(recording_file)
        
        logger.info(f"Bot {self.bot_id} started recording to {recording_file}")
        
        # Start background recording task
        self.recording_task = asyncio.create_task(self._record_audio_video())

    async def leave(self):
        """Leave meeting and cleanup"""
        self.data.status = BotStatus.LEAVING
        logger.info(f"Bot {self.bot_id} leaving meeting")
        
        # Stop recording
        if self.recording_task:
            self.stop_recording.set()
            await self.recording_task
        
        # Leave meeting (platform-specific)
        if self.page and not self.page.is_closed():
            try:
                # Click leave button if present
                await self.page.click('button:has-text("Leave")', timeout=5000)
            except:
                pass
        
        self.data.status = BotStatus.COMPLETED
        self.data.left_at = datetime.utcnow()
        logger.info(f"Bot {self.bot_id} left meeting")

    async def terminate(self):
        """Forcefully terminate bot"""
        logger.info(f"Terminating bot {self.bot_id}")
        
        # Stop recording
        if self.recording_task:
            self.stop_recording.set()
        
        # Close browser
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        self.data.status = BotStatus.TERMINATED
        logger.info(f"Bot {self.bot_id} terminated")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PLATFORM-SPECIFIC JOIN LOGIC
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _join_zoom(self):
        """Join Zoom meeting"""
        await self.page.goto(self.data.meeting_url, wait_until="networkidle", timeout=30000)
        
        # Wait for join screen
        await self.page.wait_for_selector('input[placeholder*="name"]', timeout=10000)
        
        # Enter bot name
        await self.page.fill('input[placeholder*="name"]', settings.BOT_DISPLAY_NAME)
        
        # Click join
        await self.page.click('button:has-text("Join")')
        
        # Wait for meeting to load
        await self.page.wait_for_selector('[aria-label*="participant"]', timeout=60000)
        
        # Mute audio/video if needed
        if not settings.BOT_ENABLE_AUDIO:
            await self.page.click('button[aria-label*="Mute"]', timeout=5000)
        if not settings.BOT_ENABLE_VIDEO:
            await self.page.click('button[aria-label*="Stop video"]', timeout=5000)

    async def _join_google_meet(self):
        """Join Google Meet"""
        await self.page.goto(self.data.meeting_url, wait_until="networkidle", timeout=30000)
        
        # Turn off camera/mic
        if not settings.BOT_ENABLE_VIDEO:
            await self.page.click('div[aria-label*="camera"]', timeout=5000)
        if not settings.BOT_ENABLE_AUDIO:
            await self.page.click('div[aria-label*="microphone"]', timeout=5000)
        
        # Click "Join now"
        await self.page.click('span:has-text("Join now")', timeout=10000)
        
        # Wait for meeting UI
        await self.page.wait_for_selector('[data-participant-id]', timeout=60000)

    async def _join_teams(self):
        """Join Microsoft Teams"""
        await self.page.goto(self.data.meeting_url, wait_until="networkidle", timeout=30000)
        
        # Click "Join now" (web version)
        await self.page.click('button:has-text("Join now")', timeout=10000)
        
        # Enter name
        await self.page.fill('input[placeholder*="name"]', settings.BOT_DISPLAY_NAME, timeout=10000)
        
        # Mute by default
        if not settings.BOT_ENABLE_AUDIO:
            await self.page.click('button[title*="Mute"]', timeout=5000)
        if not settings.BOT_ENABLE_VIDEO:
            await self.page.click('button[title*="Camera"]', timeout=5000)
        
        # Join meeting
        await self.page.click('button:has-text("Join now")')
        
        # Wait for participant list
        await self.page.wait_for_selector('[role="list"]', timeout=60000)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # RECORDING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _record_audio_video(self):
        """Background task to capture audio/video"""
        try:
            # Playwright's built-in video recording handles this
            # The video is saved when context closes
            while not self.stop_recording.is_set():
                await asyncio.sleep(1)
                
                # Update file size
                if self.data.recording_path and Path(self.data.recording_path).exists():
                    size_bytes = Path(self.data.recording_path).stat().st_size
                    self.data.recording_size_mb = size_bytes / (1024 * 1024)
                
        except Exception as e:
            logger.error(f"Recording error: {e}", exc_info=True)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # EVENT HANDLERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _on_console(self, msg):
        """Handle console messages from page"""
        logger.debug(f"[Browser Console] {msg.text}")

    def _on_error(self, error):
        """Handle page errors"""
        logger.error(f"[Browser Error] {error}")
        self.data.error = str(error)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MONITORING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def check_participants(self) -> int:
        """Get current participant count"""
        if not self.page or self.page.is_closed():
            return 0
        
        try:
            # Platform-specific participant detection
            if self.data.platform == BotPlatform.ZOOM:
                count = await self.page.locator('[aria-label*="participant"]').count()
            elif self.data.platform == BotPlatform.GOOGLE_MEET:
                count = await self.page.locator('[data-participant-id]').count()
            elif self.data.platform == BotPlatform.TEAMS:
                count = await self.page.locator('[role="listitem"]').count()
            else:
                count = 0
            
            self.data.participant_count = count
            
            # Check if alone (only bot in meeting)
            if count <= 1:
                if not self.data.is_alone:
                    self.data.is_alone = True
                    self.data.alone_since = datetime.utcnow()
            else:
                self.data.is_alone = False
                self.data.alone_since = None
            
            return count
            
        except Exception as e:
            logger.warning(f"Failed to check participants: {e}")
            return 0

    def should_leave(self) -> bool:
        """Check if bot should leave meeting"""
        # Alone too long
        if self.data.is_alone and self.data.alone_since:
            elapsed = (datetime.utcnow() - self.data.alone_since).total_seconds()
            if elapsed > settings.BOT_ALONE_TIMEOUT:
                logger.info(f"Bot {self.bot_id} alone for {elapsed}s, leaving")
                return True
        
        # Max duration exceeded
        if self.data.joined_at:
            duration = (datetime.utcnow() - self.data.joined_at).total_seconds()
            if duration > settings.BOT_MAX_DURATION:
                logger.info(f"Bot {self.bot_id} exceeded max duration, leaving")
                return True
        
        return False