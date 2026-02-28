import asyncio
from bot.browser_manager import BrowserManager
import os

async def test_browser():
    print("Testing BrowserManager...")
    browser = BrowserManager(headless=True)
    try:
        page = await browser.start()
        print("Browser started successfully")
        
        url = "https://www.google.com"
        print(f"Navigating to {url}...")
        await browser.navigate(url)
        
        title = await page.title()
        print(f"Page title: {title}")
        
        screenshot_path = "/home/uzair/vocaply-ai-meeting-inteligence/meeting-bot/meet-bot/test_screenshot.png"
        await browser.screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        if os.path.exists(screenshot_path):
            print("Test PASSED: Browser launched, navigated, and saved screenshot.")
        else:
            print("Test FAILED: Screenshot not found.")
            
    except Exception as e:
        print(f"Test FAILED with error: {e}")
    finally:
        await browser.stop()

if __name__ == "__main__":
    asyncio.run(test_browser())
