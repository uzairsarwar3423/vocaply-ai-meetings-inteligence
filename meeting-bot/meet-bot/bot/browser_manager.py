"""
Browser Manager
Manages Puppeteer browser with audio capture capabilities
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page


class BrowserManager:
    """
    Manages headless Chrome with:
    - Audio/video permissions
    - Extension loading
    - PulseAudio virtual sink
    """

    def __init__(
        self,
        headless: bool = True,
        extension_path: Optional[str] = None,
    ):
        self.headless = headless
        self.extension_path = extension_path or str(Path(__file__).parent.parent / "chrome-extensions")
        
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start(self) -> Page:
        """Launch browser and return page"""
        if self.browser:
            return self.page
        
        print("[Browser] Launching Chrome...")
        
        # Build launch args
        args = self._build_launch_args()
        
        # Launch browser
        self.browser = await launch(
            headless=self.headless,
            args=args,
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False,
            autoClose=False,
        )
        
        # Get page
        pages = await self.browser.pages()
        self.page = pages[0] if pages else await self.browser.newPage()
        
        # Configure page
        await self._configure_page()
        
        print("[Browser] Chrome launched successfully")
        return self.page

    async def stop(self):
        """Close browser"""
        if self.page:
            await self.page.close()
            self.page = None
        
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        print("[Browser] Chrome closed")

    def _build_launch_args(self) -> list:
        """Build Chrome launch arguments"""
        args = [
            # Audio/video permissions
            '--use-fake-ui-for-media-stream',  # Auto-grant permissions
            '--use-fake-device-for-media-stream',
            '--allow-file-access',
            
            # Performance
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            
            # Hide automation
            '--disable-blink-features=AutomationControlled',
            
            # Window size
            '--window-size=1920,1080',
            
            # Audio output (PulseAudio)
            '--enable-features=WebRTCPipeWireCapturer',
        ]
        
        # Load extension
        if self.extension_path and os.path.exists(self.extension_path):
            args.append(f'--disable-extensions-except={self.extension_path}')
            args.append(f'--load-extension={self.extension_path}')
            print(f"[Browser] Loading extension: {self.extension_path}")
        
        return args

    async def _configure_page(self):
        """Configure page settings"""
        if not self.page:
            return
        
        # Set viewport
        await self.page.setViewport({
            'width': 1920,
            'height': 1080,
        })
        
        # Permissions are granted via --use-fake-ui-for-media-stream Chrome flag
        # No additional CDP call needed for pyppeteer's bundled Chrome
        
        # Set user agent (hide headless)
        await self.page.setUserAgent(
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Inject webdriver evasion
        await self.page.evaluateOnNewDocument('''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        ''')

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PAGE ACTIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def navigate(self, url: str, wait_until: str = 'networkidle2'):
        """Navigate to URL"""
        if not self.page:
            raise RuntimeError("Browser not started")
        
        print(f"[Browser] Navigating to {url}")
        await self.page.goto(url, {'waitUntil': wait_until, 'timeout': 60000})

    async def screenshot(self, path: str):
        """Take screenshot"""
        if not self.page:
            return
        
        await self.page.screenshot({'path': path, 'fullPage': True})
        print(f"[Browser] Screenshot saved: {path}")

    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript in page"""
        if not self.page:
            return None
        
        return await self.page.evaluate(script)

    async def send_message(self, action: str, data: Dict = None) -> Dict:
        """
        Send message to content script via window.postMessage
        """

        if not self.page:
            return {'success': False, 'error': 'Page not available'}
        
        # Reset response slot and inject listener (IIFE for pyppeteer compatibility)
        await self.page.evaluate(
            '(function() {'
            '  window.__vocaplyResponse = null;'
            '  window.addEventListener("message", function(event) {'
            '    if (event.data.type === "VOCAPLY_BOT_RESPONSE") {'
            '      window.__vocaplyResponse = event.data.result;'
            '    }'
            '  });'
            '})()'
        )
        
        # Send postMessage (IIFE, json-serialised data)
        data_json = json.dumps(data or {})
        js = (
            '(function() {'
            '  window.postMessage({'
            f'    type: "VOCAPLY_BOT_ACTION",'
            f'    action: "{action}",'
            f'    data: {data_json}'
            '  }, "*");'
            '})()'
        )
        await self.page.evaluate(js)
        
        # Wait for response (with timeout)
        try:
            await self.page.waitForFunction(
                'window.__vocaplyResponse !== null',
                {'timeout': 5000}
            )
            
            response = await self.page.evaluate('window.__vocaplyResponse')
            return response or {'success': False}
            
        except Exception:
            return {'success': False, 'error': 'Timeout waiting for response'}

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HELPERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def wait_for_selector(
        self,
        selector: str,
        timeout: int = 30000,
        visible: bool = True,
    ):
        """Wait for element to appear"""
        if not self.page:
            return None
        
        return await self.page.waitForSelector(
            selector,
            {'timeout': timeout, 'visible': visible}
        )

    async def click(self, selector: str, timeout: int = 5000):
        """Click element"""
        if not self.page:
            return
        
        await self.page.waitForSelector(selector, {'timeout': timeout})
        await self.page.click(selector)

    async def type_text(self, selector: str, text: str):
        """Type text into input"""
        if not self.page:
            return
        
        await self.page.waitForSelector(selector)
        await self.page.type(selector, text)