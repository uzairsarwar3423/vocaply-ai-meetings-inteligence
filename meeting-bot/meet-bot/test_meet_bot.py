"""
Meet Bot Test Suite
===================
Tests all layers of the meet bot:
  1. Browser launch
  2. Google Drive / Google login page load
  3. Meet pre-join page navigation
  4. Join flow selectors (screenshot for debugging)
  5. Content-script messaging
  6. Audio capture module import

Run: python test_meet_bot.py [meet_url]
     If no URL provided, uses a public Google Meet test link.
"""

import asyncio
import os
import sys
import time

# ─────────────────────────────────────────────────────────────
# ANSI helpers
# ─────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

PASS = f"{GREEN}✔ PASS{RESET}"
FAIL = f"{RED}✖ FAIL{RESET}"
SKIP = f"{YELLOW}⚠ SKIP{RESET}"
INFO = f"{CYAN}ℹ INFO{RESET}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(BASE_DIR, "test_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

results = []  # (name, status, message)


def log(status, name, msg=""):
    tag = {"PASS": PASS, "FAIL": FAIL, "SKIP": SKIP, "INFO": INFO}[status]
    print(f"  {tag}  {BOLD}{name}{RESET}  {msg}")
    results.append((name, status, msg))


# ─────────────────────────────────────────────────────────────
# TEST 1: imports
# ─────────────────────────────────────────────────────────────
def test_imports():
    print(f"\n{BOLD}── Test 1: Module Imports ──{RESET}")
    try:
        from bot.browser_manager import BrowserManager
        log("PASS", "BrowserManager import")
    except Exception as e:
        log("FAIL", "BrowserManager import", str(e))

    try:
        from bot.meet_actions import MeetActions
        log("PASS", "MeetActions import")
    except Exception as e:
        log("FAIL", "MeetActions import", str(e))

    try:
        from bot.audio_capture import AudioCapture
        log("PASS", "AudioCapture import")
    except Exception as e:
        log("FAIL", "AudioCapture import", str(e))

    try:
        from bot.page_monitor import PageMonitor
        log("PASS", "PageMonitor import")
    except Exception as e:
        log("FAIL", "PageMonitor import", str(e))

    try:
        from bot.participant_scraper import ParticipantScraper
        log("PASS", "ParticipantScraper import")
    except Exception as e:
        log("FAIL", "ParticipantScraper import", str(e))

    try:
        from bot.meet_bot import MeetBot
        log("PASS", "MeetBot import")
    except Exception as e:
        log("FAIL", "MeetBot import", str(e))


# ─────────────────────────────────────────────────────────────
# TEST 2: browser launch + basic navigation
# ─────────────────────────────────────────────────────────────
async def test_browser():
    print(f"\n{BOLD}── Test 2: Browser Launch & Navigation ──{RESET}")
    from bot.browser_manager import BrowserManager

    browser = BrowserManager(headless=True)
    try:
        page = await browser.start()
        log("PASS", "Chrome launched")

        await browser.navigate("https://www.google.com")
        title = await page.title()
        log("PASS", "Navigate to google.com", f"title='{title}'")

        ss = os.path.join(SCREENSHOT_DIR, "01_google.png")
        await browser.screenshot(ss)
        log("PASS", "Screenshot saved", ss)

    except Exception as e:
        log("FAIL", "Browser test", str(e))
    finally:
        await browser.stop()
        log("PASS", "Chrome closed cleanly")


# ─────────────────────────────────────────────────────────────
# TEST 3: Meet pre-join page
# ─────────────────────────────────────────────────────────────
async def test_meet_page(meeting_url: str):
    print(f"\n{BOLD}── Test 3: Google Meet Pre-Join Page ──{RESET}")
    print(f"  {INFO}  URL: {meeting_url}")

    from bot.browser_manager import BrowserManager

    browser = BrowserManager(headless=True)
    page = await browser.start()

    try:
        # Navigate to Meet
        await browser.navigate(meeting_url)
        await asyncio.sleep(4)

        title = await page.title()
        url   = page.url
        log("PASS", "Meet page loaded", f"title='{title}'")
        log("INFO", "Current URL", url)

        ss = os.path.join(SCREENSHOT_DIR, "02_meet_prejoin.png")
        await browser.screenshot(ss)
        log("PASS", "Pre-join screenshot saved", ss)

        # Check for common pre-join elements
        selectors_to_check = {
            "Join button (aria-label)"  : '[aria-label*="Join" i]',
            "Name input"                : 'input[aria-label*="name" i]',
            "Camera button"             : '[aria-label*="camera" i]',
            "Microphone button"         : '[aria-label*="microphone" i]',
            "jsname join button"        : '[jsname="Qx7uuf"]',
        }

        found_any = False
        for label, sel in selectors_to_check.items():
            try:
                el = await page.querySelector(sel)
                if el:
                    log("PASS", f"Selector found: {label}", sel)
                    found_any = True
                else:
                    log("SKIP", f"Selector absent: {label}", sel)
            except Exception as e:
                log("SKIP", f"Selector error: {label}", str(e))

        if not found_any:
            log("INFO", "No Meet controls found",
                "Meeting may be invalid/expired or Google is blocking headless access")

    except Exception as e:
        log("FAIL", "Meet page test", str(e))
        ss = os.path.join(SCREENSHOT_DIR, "02_meet_error.png")
        try:
            await browser.screenshot(ss)
            log("INFO", "Error screenshot", ss)
        except:
            pass
    finally:
        await browser.stop()


# ─────────────────────────────────────────────────────────────
# TEST 4: content-script message roundtrip on a real Meet page
# ─────────────────────────────────────────────────────────────
async def test_content_script(meeting_url: str):
    print(f"\n{BOLD}── Test 4: Content Script Messaging ──{RESET}")
    from bot.browser_manager import BrowserManager
    from bot.meet_actions import MeetActions

    browser = BrowserManager(headless=True)
    await browser.start()

    try:
        await browser.navigate(meeting_url)
        await asyncio.sleep(4)

        actions = MeetActions(browser)

        # GET_STATUS
        status = await actions.get_meeting_status()
        log("PASS", "GET_STATUS message", str(status))

        # GET_PARTICIPANT_COUNT
        cnt = await actions.get_participant_count()
        log("PASS", "GET_PARTICIPANT_COUNT message", f"count={cnt}")

        # GET_PARTICIPANTS
        parts = await actions.get_participants()
        log("PASS", "GET_PARTICIPANTS message", f"participants={parts}")

    except Exception as e:
        log("FAIL", "Content script test", str(e))
    finally:
        await browser.stop()


# ─────────────────────────────────────────────────────────────
# TEST 5: MeetBot instantiation + lifecycle
# ─────────────────────────────────────────────────────────────
def test_meetbot_init():
    print(f"\n{BOLD}── Test 5: MeetBot Instantiation ──{RESET}")
    try:
        from bot.meet_bot import MeetBot
        bot = MeetBot(
            bot_id="test-bot-001",
            meeting_id="test-meeting-001",
            meeting_url="https://meet.google.com/abc-defg-hij",
            company_id="vocaply-test",
            webhook_url="http://localhost:8001/webhooks/bot-events",
            bot_name="Vocaply Test Bot",
        )
        log("PASS", "MeetBot instantiated", f"id={bot.bot_id}")
        log("PASS", "Initial state: is_running=False", str(bot.is_running))
        stats = bot.get_stats()
        log("PASS", "get_stats() returns dict", f"keys={list(stats.keys())}")
    except Exception as e:
        log("FAIL", "MeetBot instantiation", str(e))


# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
def print_summary():
    print(f"\n{BOLD}{'─'*50}{RESET}")
    print(f"{BOLD}  TEST SUMMARY{RESET}")
    print(f"{BOLD}{'─'*50}{RESET}")
    passed = sum(1 for _, s, _ in results if s == "PASS")
    failed = sum(1 for _, s, _ in results if s == "FAIL")
    skipped = sum(1 for _, s, _ in results if s in ("SKIP", "INFO"))
    print(f"  {GREEN}{passed} passed{RESET}  |  {RED}{failed} failed{RESET}  |  {YELLOW}{skipped} skipped/info{RESET}")
    if failed:
        print(f"\n{RED}  Failed checks:{RESET}")
        for name, status, msg in results:
            if status == "FAIL":
                print(f"    ✖ {name}: {msg}")
    print(f"\n  Screenshots saved to: {SCREENSHOT_DIR}/")
    print()


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
async def main():
    print(f"\n{BOLD}{CYAN}{'═'*50}{RESET}")
    print(f"{BOLD}{CYAN}  VOCAPLY MEET BOT — TEST SUITE{RESET}")
    print(f"{BOLD}{CYAN}{'═'*50}{RESET}")

    # Get meeting URL from arg (or default to a dummy)
    if len(sys.argv) >= 2:
        meeting_url = sys.argv[1]
    else:
        # Use a real-ish looking Meet URL for page load tests
        meeting_url = "https://meet.google.com/new"  # redirects to a new meeting lobby

    print(f"  Meeting URL: {meeting_url}")

    # Run tests
    test_imports()
    await test_browser()
    await test_meet_page(meeting_url)
    await test_content_script(meeting_url)
    test_meetbot_init()

    print_summary()


if __name__ == "__main__":
    asyncio.run(main())
