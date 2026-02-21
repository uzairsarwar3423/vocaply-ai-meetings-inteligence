"""
Token Tracker
Vocaply Platform - Day 9: OpenAI Integration & Prompt Engineering
File: backend/app/services/ai/token_tracker.py

Handles:
  - Per-company rate limiting (tokens/minute, requests/minute)
  - Usage aggregation in Redis (daily/monthly counters)
  - Rate limit check before making an API call
"""
from __future__ import annotations

import json
import time
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

import redis as redis_lib

from app.core.config import settings


# ============================================
# CONSTANTS
# ============================================

# Default per-company limits (can be overridden via company plan)
DEFAULT_TOKENS_PER_MINUTE  = 100_000    # gpt-4o-mini shared default
DEFAULT_REQUESTS_PER_MINUTE = 500
DEFAULT_MONTHLY_BUDGET_USD  = 50.0      # soft budget cap in USD

# Redis key TTLs
MINUTE_WINDOW_SECONDS = 60
DAY_WINDOW_SECONDS    = 86_400
MONTH_WINDOW_SECONDS  = 86_400 * 31


# ============================================
# TOKEN TRACKER
# ============================================

class TokenTracker:
    """
    Manages per-company token usage tracking and rate limiting via Redis.

    Redis key schema:
        ai:rl:{company_id}:rpm                  → request counter (60s window)
        ai:rl:{company_id}:tpm                  → token counter   (60s window)
        ai:usage:{company_id}:{YYYY-MM-DD}      → daily usage hash
        ai:usage:{company_id}:{YYYY-MM}         → monthly usage hash
    """

    def __init__(self) -> None:
        try:
            self._redis = redis_lib.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            self._redis.ping()
            self._available = True
        except Exception:
            # Degrade gracefully – tracking won't work but calls won't fail
            self._redis = None
            self._available = False

    # ----------------------------------------
    # RATE LIMITING
    # ----------------------------------------

    def check_rate_limit(
        self,
        company_id: str,
        estimated_tokens: int,
        tokens_per_minute:  int = DEFAULT_TOKENS_PER_MINUTE,
        requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE,
    ) -> tuple[bool, str | None]:
        """
        Check if the company is within rate limits.

        Returns:
            (allowed: bool, reason: str | None)
            reason is None when allowed; contains a message when blocked.
        """
        if not self._available:
            return True, None

        rpm_key = self._rpm_key(company_id)
        tpm_key = self._tpm_key(company_id)

        pipe = self._redis.pipeline(transaction=True)
        pipe.incr(rpm_key)
        pipe.expire(rpm_key, MINUTE_WINDOW_SECONDS)
        pipe.get(tpm_key)
        results = pipe.execute()

        current_rpm = int(results[0])
        current_tpm = int(results[2] or 0)

        if current_rpm > requests_per_minute:
            return False, (
                f"Rate limit exceeded: {current_rpm} requests/min "
                f"(limit: {requests_per_minute})"
            )

        if current_tpm + estimated_tokens > tokens_per_minute:
            return False, (
                f"Token rate limit exceeded: {current_tpm + estimated_tokens} "
                f"estimated tokens/min (limit: {tokens_per_minute})"
            )

        return True, None

    def record_token_usage(
        self,
        company_id: str,
        tokens_used: int,
    ) -> None:
        """Increment the per-minute token counter after a successful API call."""
        if not self._available:
            return
        tpm_key = self._tpm_key(company_id)
        pipe = self._redis.pipeline(transaction=True)
        pipe.incrby(tpm_key, tokens_used)
        pipe.expire(tpm_key, MINUTE_WINDOW_SECONDS)
        pipe.execute()

    # ----------------------------------------
    # USAGE AGGREGATION
    # ----------------------------------------

    def record_usage(
        self,
        company_id:        str,
        feature_type:      str,
        prompt_tokens:     int,
        completion_tokens: int,
        total_cost_usd:    Decimal,
        model:             str = "gpt-4o-mini",
        was_cached:        bool = False,
    ) -> None:
        """
        Record usage counters in Redis daily & monthly aggregation hashes.
        This is in addition to the persistent DB record in ai_usage.
        """
        if not self._available:
            return

        today = date.today().isoformat()           # "2024-01-15"
        month = date.today().strftime("%Y-%m")     # "2024-01"

        day_key   = self._day_key(company_id, today)
        month_key = self._month_key(company_id, month)

        cost_cents = int(float(total_cost_usd) * 100_000)   # store as micro-cents

        pipe = self._redis.pipeline(transaction=True)
        for key, ttl in ((day_key, DAY_WINDOW_SECONDS), (month_key, MONTH_WINDOW_SECONDS)):
            pipe.hincrby(key, "total_requests",      1)
            pipe.hincrby(key, "prompt_tokens",       prompt_tokens)
            pipe.hincrby(key, "completion_tokens",   completion_tokens)
            pipe.hincrby(key, "total_tokens",        prompt_tokens + completion_tokens)
            pipe.hincrby(key, "total_cost_microcents", cost_cents)
            pipe.hincrby(key, f"feature:{feature_type}", 1)
            if was_cached:
                pipe.hincrby(key, "cached_requests", 1)
            pipe.expire(key, ttl)
        pipe.execute()

    def get_daily_usage(self, company_id: str, day: str | None = None) -> dict:
        """
        Return raw daily usage counters from Redis.

        Args:
            day: ISO date string "YYYY-MM-DD"; defaults to today.
        """
        if not self._available:
            return {}
        day = day or date.today().isoformat()
        raw = self._redis.hgetall(self._day_key(company_id, day))
        return self._parse_counters(raw)

    def get_monthly_usage(self, company_id: str, month: str | None = None) -> dict:
        """
        Return raw monthly usage counters from Redis.

        Args:
            month: "YYYY-MM"; defaults to current month.
        """
        if not self._available:
            return {}
        month = month or date.today().strftime("%Y-%m")
        raw = self._redis.hgetall(self._month_key(company_id, month))
        return self._parse_counters(raw)

    def check_monthly_budget(
        self,
        company_id: str,
        estimated_cost_usd: float,
        budget_usd: float = DEFAULT_MONTHLY_BUDGET_USD,
    ) -> tuple[bool, float]:
        """
        Check if adding estimated_cost_usd would exceed the monthly budget.

        Returns:
            (within_budget: bool, current_spend_usd: float)
        """
        if not self._available:
            return True, 0.0

        month   = date.today().strftime("%Y-%m")
        raw     = self._redis.hget(self._month_key(company_id, month), "total_cost_microcents")
        current = int(raw or 0) / 100_000   # back to USD

        return (current + estimated_cost_usd) <= budget_usd, current

    # ----------------------------------------
    # HELPERS
    # ----------------------------------------

    @staticmethod
    def _rpm_key(cid: str) -> str:
        return f"ai:rl:{cid}:rpm"

    @staticmethod
    def _tpm_key(cid: str) -> str:
        return f"ai:rl:{cid}:tpm"

    @staticmethod
    def _day_key(cid: str, day: str) -> str:
        return f"ai:usage:{cid}:{day}"

    @staticmethod
    def _month_key(cid: str, month: str) -> str:
        return f"ai:usage:{cid}:{month}"

    @staticmethod
    def _parse_counters(raw: dict) -> dict:
        """Convert all values to integers and cost to USD float."""
        parsed: dict = {}
        for k, v in raw.items():
            try:
                parsed[k] = int(v)
            except (ValueError, TypeError):
                parsed[k] = v
        # Convert micro-cents → USD
        if "total_cost_microcents" in parsed:
            parsed["total_cost_usd"] = parsed["total_cost_microcents"] / 100_000
        return parsed

    @property
    def is_available(self) -> bool:
        return self._available


# ============================================
# MODULE-LEVEL SINGLETON
# ============================================

token_tracker = TokenTracker()
