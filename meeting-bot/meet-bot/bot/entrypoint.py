"""
Bot Entrypoint
==============
Starts the MeetBot using environment variables.
Called by Docker CMD: python -m bot.entrypoint

Required env vars:
  BOT_ID        - Unique bot instance ID
  MEETING_ID    - Meeting ID in Vocaply system
  MEETING_URL   - Full Google Meet URL (e.g. https://meet.google.com/abc-defg-hij)
  COMPANY_ID    - Company/tenant ID

Optional env vars:
  WEBHOOK_URL   - URL to send bot events to (default: http://bot-orchestrator:8001/webhooks/bot-events)
  BOT_NAME      - Display name in the meeting (default: Vocaply Bot)
"""

import asyncio
import os
import sys

from bot.meet_bot import MeetBot


def _require_env(key: str) -> str:
    """Get required env var or exit with clear error."""
    val = os.environ.get(key, "").strip()
    if not val:
        print(f"[Entrypoint] ERROR: Environment variable '{key}' is required but not set.")
        sys.exit(1)
    return val


async def main():
    # Required
    bot_id      = _require_env("BOT_ID")
    meeting_id  = _require_env("MEETING_ID")
    meeting_url = _require_env("MEETING_URL")
    company_id  = _require_env("COMPANY_ID")

    # Optional with defaults
    webhook_url = os.environ.get("WEBHOOK_URL", "http://bot-orchestrator:8001/webhooks/bot-events")
    bot_name    = os.environ.get("BOT_NAME", "Vocaply Bot")

    print(f"[Entrypoint] Starting bot")
    print(f"[Entrypoint]   bot_id      = {bot_id}")
    print(f"[Entrypoint]   meeting_id  = {meeting_id}")
    print(f"[Entrypoint]   meeting_url = {meeting_url}")
    print(f"[Entrypoint]   company_id  = {company_id}")
    print(f"[Entrypoint]   webhook_url = {webhook_url}")
    print(f"[Entrypoint]   bot_name    = {bot_name}")

    bot = MeetBot(
        bot_id=bot_id,
        meeting_id=meeting_id,
        meeting_url=meeting_url,
        company_id=company_id,
        webhook_url=webhook_url,
        bot_name=bot_name,
    )

    try:
        await bot.start()

        # Keep process alive while bot is running
        while bot.is_running:
            await asyncio.sleep(5)

    except KeyboardInterrupt:
        print("\n[Entrypoint] Interrupted, stopping...")

    except Exception as e:
        print(f"[Entrypoint] Fatal error: {e}")
        sys.exit(1)

    finally:
        await bot.stop()

    print("[Entrypoint] Bot finished.")


if __name__ == "__main__":
    asyncio.run(main())
