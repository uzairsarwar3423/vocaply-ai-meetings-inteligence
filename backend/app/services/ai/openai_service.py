"""
OpenAI Service
Vocaply Platform - Day 9: OpenAI Integration & Prompt Engineering
File: backend/app/services/ai/openai_service.py

Full-featured OpenAI API client wrapper:
  - gpt-4o-mini integration
  - Token usage tracking & cost calculation
  - Redis response caching
  - Per-company rate limiting
  - Exponential-backoff retries
  - Streaming support
  - Context window management via PromptBuilder
"""
from __future__ import annotations

import asyncio
import json
import time
from decimal import Decimal
from typing import Any, AsyncGenerator, Dict, List, Optional
from uuid import UUID

import openai
from openai import AsyncOpenAI, RateLimitError, APIConnectionError, APIStatusError
from loguru import logger

from app.core.config import settings
from app.services.ai.prompt_builder import prompt_builder, PromptBuilder
from app.services.ai.prompt_templates import TemplateKey, get_template
from app.services.ai.token_tracker import token_tracker
from app.models.ai_usage import AIUsage, AIFeatureType, AIRequestStatus


# ============================================
# CONSTANTS
# ============================================

DEFAULT_MODEL           = "gpt-4o-mini"
DEFAULT_TEMPERATURE     = 0.3
MAX_RETRIES             = 3
BASE_RETRY_DELAY        = 1.0       # seconds
CACHE_TTL_SECONDS       = 3_600     # 1 hour
CONTEXT_WINDOW_TOKENS   = 128_000   # gpt-4o-mini

# Feature type → TemplateKey mapping
FEATURE_TO_TEMPLATE: Dict[AIFeatureType, TemplateKey] = {
    AIFeatureType.MEETING_SUMMARY:        TemplateKey.MEETING_SUMMARY,
    AIFeatureType.ACTION_ITEM_EXTRACTION: TemplateKey.ACTION_ITEM_EXTRACTION,
    AIFeatureType.KEY_DECISIONS:          TemplateKey.KEY_DECISIONS,
    AIFeatureType.PARTICIPANT_ANALYSIS:   TemplateKey.PARTICIPANT_ANALYSIS,
    AIFeatureType.TOPIC_EXTRACTION:       TemplateKey.TOPIC_EXTRACTION,
    AIFeatureType.SENTIMENT_ANALYSIS:     TemplateKey.SENTIMENT_ANALYSIS,
}


# ============================================
# RESULT DATACLASS
# ============================================

class AIResult:
    """Returned by every OpenAI call."""

    __slots__ = (
        "content", "parsed", "feature_type", "model",
        "prompt_tokens", "completion_tokens", "total_tokens",
        "prompt_cost", "completion_cost", "total_cost",
        "latency_ms", "was_cached", "retry_count",
        "prompt_version", "request_id", "status", "error",
    )

    def __init__(
        self,
        content:           str,
        parsed:            Any,
        feature_type:      str,
        model:             str,
        prompt_tokens:     int,
        completion_tokens: int,
        total_tokens:      int,
        prompt_cost:       Decimal,
        completion_cost:   Decimal,
        total_cost:        Decimal,
        latency_ms:        int,
        was_cached:        bool,
        retry_count:       int,
        prompt_version:    str,
        request_id:        Optional[str],
        status:            str,
        error:             Optional[str] = None,
    ) -> None:
        self.content           = content
        self.parsed            = parsed
        self.feature_type      = feature_type
        self.model             = model
        self.prompt_tokens     = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens      = total_tokens
        self.prompt_cost       = prompt_cost
        self.completion_cost   = completion_cost
        self.total_cost        = total_cost
        self.latency_ms        = latency_ms
        self.was_cached        = was_cached
        self.retry_count       = retry_count
        self.prompt_version    = prompt_version
        self.request_id        = request_id
        self.status            = status
        self.error             = error

    def to_dict(self) -> dict:
        return {
            "content":           self.content,
            "parsed":            self.parsed,
            "feature_type":      self.feature_type,
            "model":             self.model,
            "prompt_tokens":     self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens":      self.total_tokens,
            "total_cost_usd":    float(self.total_cost),
            "latency_ms":        self.latency_ms,
            "was_cached":        self.was_cached,
            "retry_count":       self.retry_count,
            "status":            self.status,
        }


# ============================================
# OPENAI SERVICE
# ============================================

class OpenAIService:
    """
    Central service for all OpenAI API interactions.

    Typical usage::

        result = await openai_service.analyze(
            feature_type  = AIFeatureType.MEETING_SUMMARY,
            variables     = {...},
            company_id    = company_id,
            meeting_id    = meeting.id,
            db            = db,
        )
        summary_json = result.parsed
    """

    def __init__(self) -> None:
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            logger.warning(
                "OPENAI_API_KEY not set in environment. "
                "OpenAI calls will fail until it is configured."
            )
        self._client = AsyncOpenAI(api_key=api_key or "dummy-key")

        # Redis client (shared with token_tracker)
        self._redis = token_tracker._redis
        self._redis_available = token_tracker.is_available

    # ==========================================
    # PRIMARY PUBLIC API
    # ==========================================

    async def analyze(
        self,
        feature_type:       AIFeatureType,
        variables:          Dict[str, Any],
        company_id:         str,
        db,                                     # SQLAlchemy Session
        meeting_id:         Optional[UUID] = None,
        user_id:            Optional[str]  = None,
        template_version:   Optional[str]  = None,
        model:              str             = DEFAULT_MODEL,
        use_cache:          bool            = True,
        skip_rate_limit:    bool            = False,
    ) -> AIResult:
        """
        Run an AI analysis feature and persist usage records.

        Args:
            feature_type:     Which AI feature to use.
            variables:        Template variables (transcript_text, meeting_title, …).
            company_id:       Multi-tenant company ID.
            db:               Database session for persisting AIUsage records.
            meeting_id:       Optional linked meeting UUID.
            user_id:          Optional user who triggered the call.
            template_version: Pin to a specific prompt version; None = latest.
            model:            OpenAI model name.
            use_cache:        Whether to check/store Redis cache.
            skip_rate_limit:  Bypass rate limit check (internal/admin calls).

        Returns:
            AIResult
        """
        template_key = FEATURE_TO_TEMPLATE.get(feature_type)
        if not template_key:
            raise ValueError(f"No template registered for feature '{feature_type}'")

        template = get_template(template_key, template_version)

        # ---- Build messages ----
        messages, build_meta = prompt_builder.build(
            template_key          = template_key,
            variables             = variables,
            version               = template_version,
            context_window_tokens = CONTEXT_WINDOW_TOKENS,
        )

        # ---- Rate limit check ----
        if not skip_rate_limit:
            allowed, reason = token_tracker.check_rate_limit(
                company_id       = company_id,
                estimated_tokens = build_meta["estimated_tokens"],
            )
            if not allowed:
                logger.warning(f"Rate limit hit for company {company_id}: {reason}")
                result = self._build_error_result(
                    feature_type  = feature_type.value,
                    model         = model,
                    prompt_version= template.version,
                    status        = AIRequestStatus.RATE_LIMITED.value,
                    error         = reason,
                )
                await self._persist_usage(db, result, company_id, meeting_id, user_id)
                return result

        # ---- Cache lookup ----
        cache_key: Optional[str] = None
        if use_cache and self._redis_available:
            cache_key = prompt_builder.build_cache_key(template_key, variables, template_version)
            cached    = self._get_cache(cache_key)
            if cached:
                logger.debug(f"Cache HIT for {feature_type.value} | key={cache_key[:20]}…")
                result = self._result_from_cache(cached, feature_type.value, template.version)
                await self._persist_usage(db, result, company_id, meeting_id, user_id)
                return result

        # ---- Call OpenAI with retries ----
        result = await self._call_with_retry(
            messages        = messages,
            template        = template,
            feature_type    = feature_type.value,
            model           = model,
        )

        # ---- Record token usage in Redis rate-limit window ----
        token_tracker.record_token_usage(company_id, result.total_tokens)
        token_tracker.record_usage(
            company_id        = company_id,
            feature_type      = feature_type.value,
            prompt_tokens     = result.prompt_tokens,
            completion_tokens = result.completion_tokens,
            total_cost_usd    = result.total_cost,
            model             = model,
            was_cached        = False,
        )

        # ---- Store in cache ----
        if use_cache and cache_key and self._redis_available and result.status == AIRequestStatus.SUCCESS.value:
            self._set_cache(cache_key, result)

        # ---- Persist to DB ----
        await self._persist_usage(db, result, company_id, meeting_id, user_id)

        return result

    # ==========================================
    # STREAMING
    # ==========================================

    async def stream_analyze(
        self,
        feature_type:     AIFeatureType,
        variables:        Dict[str, Any],
        company_id:       str,
        template_version: Optional[str] = None,
        model:            str           = DEFAULT_MODEL,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming variant — yields text chunks as they arrive.
        Usage records are NOT persisted (caller's responsibility).

        Yields:
            str chunks of the completion text.
        """
        template_key = FEATURE_TO_TEMPLATE.get(feature_type)
        if not template_key:
            raise ValueError(f"No template for feature '{feature_type}'")

        messages, _ = prompt_builder.build(
            template_key          = template_key,
            variables             = variables,
            version               = template_version,
            context_window_tokens = CONTEXT_WINDOW_TOKENS,
        )

        template = get_template(template_key, template_version)

        params: Dict[str, Any] = {
            "model":       model,
            "messages":    messages,
            "temperature": template.temperature,
            "max_tokens":  template.max_tokens,
            "stream":      True,
        }

        try:
            stream = await self._client.chat.completions.create(**params)
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as exc:
            logger.error(f"Streaming error: {exc}")
            raise

    # ==========================================
    # CORE HTTP CALL WITH RETRY
    # ==========================================

    async def _call_with_retry(
        self,
        messages:     List[Dict],
        template,
        feature_type: str,
        model:        str,
    ) -> AIResult:
        """
        Call the OpenAI Chat Completions API with exponential backoff.
        """
        last_exception: Optional[Exception] = None
        retry_count = 0

        params: Dict[str, Any] = {
            "model":       model,
            "messages":    messages,
            "temperature": template.temperature,
            "max_tokens":  template.max_tokens,
        }
        if template.json_mode:
            params["response_format"] = {"type": "json_object"}

        for attempt in range(MAX_RETRIES + 1):
            try:
                t0 = time.monotonic()
                response = await self._client.chat.completions.create(**params)
                latency_ms = int((time.monotonic() - t0) * 1000)

                raw_content    = response.choices[0].message.content or ""
                request_id     = getattr(response, "_request_id", None)
                usage          = response.usage
                prompt_tokens  = usage.prompt_tokens     if usage else 0
                comp_tokens    = usage.completion_tokens if usage else 0
                total_tokens   = usage.total_tokens      if usage else 0

                p_cost, c_cost, t_cost = AIUsage.calculate_cost(
                    prompt_tokens, comp_tokens, model
                )

                # Parse JSON
                parsed = None
                if template.json_mode:
                    try:
                        parsed = json.loads(raw_content)
                    except json.JSONDecodeError:
                        logger.warning(
                            f"Could not parse JSON from {feature_type} response. "
                            f"Raw: {raw_content[:200]}"
                        )
                        parsed = {"raw": raw_content}

                return AIResult(
                    content           = raw_content,
                    parsed            = parsed,
                    feature_type      = feature_type,
                    model             = model,
                    prompt_tokens     = prompt_tokens,
                    completion_tokens = comp_tokens,
                    total_tokens      = total_tokens,
                    prompt_cost       = p_cost,
                    completion_cost   = c_cost,
                    total_cost        = t_cost,
                    latency_ms        = latency_ms,
                    was_cached        = False,
                    retry_count       = retry_count,
                    prompt_version    = template.version,
                    request_id        = request_id,
                    status            = AIRequestStatus.SUCCESS.value,
                )

            except RateLimitError as exc:
                last_exception = exc
                retry_count   += 1
                wait = BASE_RETRY_DELAY * (2 ** attempt)
                logger.warning(
                    f"OpenAI RateLimitError on attempt {attempt + 1}. "
                    f"Retrying in {wait:.1f}s…"
                )
                await asyncio.sleep(wait)

            except (APIConnectionError, APIStatusError) as exc:
                last_exception = exc
                retry_count   += 1
                wait = BASE_RETRY_DELAY * (2 ** attempt)
                logger.warning(
                    f"OpenAI API error on attempt {attempt + 1}: {exc}. "
                    f"Retrying in {wait:.1f}s…"
                )
                await asyncio.sleep(wait)

            except Exception as exc:
                logger.error(f"Unexpected OpenAI error: {exc}")
                return self._build_error_result(
                    feature_type   = feature_type,
                    model          = model,
                    prompt_version = template.version,
                    status         = AIRequestStatus.FAILED.value,
                    error          = str(exc),
                    retry_count    = retry_count,
                )

        # All retries exhausted
        return self._build_error_result(
            feature_type   = feature_type,
            model          = model,
            prompt_version = template.version,
            status         = AIRequestStatus.FAILED.value,
            error          = str(last_exception),
            retry_count    = retry_count,
        )

    # ==========================================
    # CACHING
    # ==========================================

    def _get_cache(self, key: str) -> Optional[dict]:
        if not self._redis_available:
            return None
        try:
            raw = self._redis.get(key)
            return json.loads(raw) if raw else None
        except Exception as exc:
            logger.debug(f"Cache read error: {exc}")
            return None

    def _set_cache(self, key: str, result: AIResult) -> None:
        if not self._redis_available:
            return
        try:
            payload = {
                "content":           result.content,
                "parsed":            result.parsed,
                "prompt_tokens":     result.prompt_tokens,
                "completion_tokens": result.completion_tokens,
                "total_tokens":      result.total_tokens,
                "prompt_cost":       str(result.prompt_cost),
                "completion_cost":   str(result.completion_cost),
                "total_cost":        str(result.total_cost),
                "model":             result.model,
                "latency_ms":        result.latency_ms,
                "prompt_version":    result.prompt_version,
            }
            self._redis.setex(key, CACHE_TTL_SECONDS, json.dumps(payload))
        except Exception as exc:
            logger.debug(f"Cache write error: {exc}")

    @staticmethod
    def _result_from_cache(cached: dict, feature_type: str, prompt_version: str) -> AIResult:
        return AIResult(
            content           = cached.get("content", ""),
            parsed            = cached.get("parsed"),
            feature_type      = feature_type,
            model             = cached.get("model", DEFAULT_MODEL),
            prompt_tokens     = cached.get("prompt_tokens", 0),
            completion_tokens = cached.get("completion_tokens", 0),
            total_tokens      = cached.get("total_tokens", 0),
            prompt_cost       = Decimal(cached.get("prompt_cost", "0")),
            completion_cost   = Decimal(cached.get("completion_cost", "0")),
            total_cost        = Decimal(cached.get("total_cost", "0")),
            latency_ms        = cached.get("latency_ms", 0),
            was_cached        = True,
            retry_count       = 0,
            prompt_version    = prompt_version,
            request_id        = None,
            status            = AIRequestStatus.CACHED.value,
        )

    # ==========================================
    # DB PERSISTENCE
    # ==========================================

    async def _persist_usage(
        self,
        db,
        result:     AIResult,
        company_id: str,
        meeting_id: Optional[UUID],
        user_id:    Optional[str],
    ) -> None:
        """Write an AIUsage row to the database (fire-and-forget style)."""
        try:
            usage = AIUsage(
                company_id        = company_id,
                meeting_id        = meeting_id,
                user_id           = user_id,
                feature_type      = result.feature_type,
                model             = result.model,
                prompt_version    = result.prompt_version,
                request_id        = result.request_id,
                status            = result.status,
                prompt_tokens     = result.prompt_tokens,
                completion_tokens = result.completion_tokens,
                total_tokens      = result.total_tokens,
                prompt_cost       = result.prompt_cost,
                completion_cost   = result.completion_cost,
                total_cost        = result.total_cost,
                latency_ms        = result.latency_ms,
                was_cached        = result.was_cached,
                retry_count       = result.retry_count,
                error_message     = result.error,
                meta_data         = {
                    "prompt_version": result.prompt_version,
                    "was_cached":     result.was_cached,
                },
            )
            db.add(usage)
            db.commit()
        except Exception as exc:
            logger.error(f"Failed to persist AI usage record: {exc}")
            db.rollback()

    # ==========================================
    # HELPERS
    # ==========================================

    @staticmethod
    def _build_error_result(
        feature_type:  str,
        model:         str,
        prompt_version: str,
        status:        str,
        error:         Optional[str] = None,
        retry_count:   int = 0,
    ) -> AIResult:
        return AIResult(
            content           = "",
            parsed            = None,
            feature_type      = feature_type,
            model             = model,
            prompt_tokens     = 0,
            completion_tokens = 0,
            total_tokens      = 0,
            prompt_cost       = Decimal("0"),
            completion_cost   = Decimal("0"),
            total_cost        = Decimal("0"),
            latency_ms        = 0,
            was_cached        = False,
            retry_count       = retry_count,
            prompt_version    = prompt_version,
            request_id        = None,
            status            = status,
            error             = error,
        )


# ============================================
# MODULE-LEVEL SINGLETON
# ============================================

openai_service = OpenAIService()
