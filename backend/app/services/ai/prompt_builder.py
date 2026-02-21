"""
Prompt Builder
Vocaply Platform - Day 9: OpenAI Integration & Prompt Engineering
File: backend/app/services/ai/prompt_builder.py

Responsible for:
  - Filling prompt templates with runtime context
  - Managing context window: truncating transcript to fit within limits
  - Building the final messages list for the OpenAI API
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, List, Optional

from app.services.ai.prompt_templates import PromptTemplate, TemplateKey, get_template


# ============================================
# CONSTANTS
# ============================================

# gpt-4o-mini context window = 128k tokens.
# Rough token estimate: 1 token ≈ 4 chars (English text).
CHARS_PER_TOKEN_APPROX = 4

# Safety buffer – leave this many tokens for system + user boiler-plate & response.
SAFETY_OVERHEAD_TOKENS = 2_000


# ============================================
# PROMPT BUILDER
# ============================================

class PromptBuilder:
    """
    Builds final messages lists from a template + runtime variables.

    Usage::

        builder = PromptBuilder()
        messages, meta = builder.build(
            template_key=TemplateKey.MEETING_SUMMARY,
            variables={
                "meeting_title":    meeting.title,
                "meeting_date":     meeting.scheduled_start.date().isoformat(),
                "duration_minutes": meeting.duration_minutes or 0,
                "participant_names": ", ".join(...),
                "transcript_text":  full_transcript,
            },
            context_window_tokens=128_000,
        )
    """

    # ----------------------------------------
    # PUBLIC API
    # ----------------------------------------

    def build(
        self,
        template_key: TemplateKey,
        variables: Dict[str, Any],
        version: Optional[str] = None,
        context_window_tokens: int = 128_000,
    ) -> tuple[List[Dict], Dict]:
        """
        Build the messages list and return metadata.

        Returns:
            messages : List[dict] ready for openai.chat.completions.create(messages=...)
            meta     : dict with keys: template_version, prompt_hash, estimated_tokens,
                       transcript_truncated, chars_used
        """
        template = get_template(template_key, version)

        # Truncate the transcript if needed
        transcript, truncated = self._fit_transcript(
            variables=variables,
            template=template,
            context_window_tokens=context_window_tokens,
        )
        if truncated:
            variables = {**variables, "transcript_text": transcript}

        user_content = self._render(template.user_template, variables)

        messages: List[Dict] = [
            {"role": "system", "content": template.system_msg},
            {"role": "user",   "content": user_content},
        ]

        estimated_tokens = self._estimate_tokens(
            template.system_msg + user_content
        )

        prompt_hash = hashlib.sha256(
            (template.system_msg + user_content).encode()
        ).hexdigest()[:16]

        meta = {
            "template_key":         template_key.value,
            "template_version":     template.version,
            "prompt_hash":          prompt_hash,
            "estimated_tokens":     estimated_tokens,
            "transcript_truncated": truncated,
            "chars_used":           len(user_content),
        }

        return messages, meta

    def build_cache_key(
        self,
        template_key: TemplateKey,
        variables: Dict[str, Any],
        version: Optional[str] = None,
    ) -> str:
        """
        Deterministic cache key for a fully-rendered prompt.
        Used by the OpenAI service for Redis caching.
        """
        template = get_template(template_key, version)
        rendered = self._render(template.user_template, variables)
        content  = template.system_msg + rendered
        return f"ai:prompt:{hashlib.sha256(content.encode()).hexdigest()}"

    # ----------------------------------------
    # PRIVATE HELPERS
    # ----------------------------------------

    @staticmethod
    def _render(template_str: str, variables: Dict[str, Any]) -> str:
        """
        Simple {variable} substitution.
        Leaves un-matched placeholders as-is (safe for JSON examples in templates).
        """
        def replacer(match: re.Match) -> str:
            key = match.group(1)
            value = variables.get(key)
            if value is None:
                return match.group(0)  # keep original placeholder
            if isinstance(value, (dict, list)):
                return json.dumps(value, ensure_ascii=False)
            return str(value)

        # Match only single-word placeholders like {transcript_text}, not {{...}}
        return re.sub(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})", replacer, template_str)

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough token count (no tiktoken dependency required)."""
        return max(1, len(text) // CHARS_PER_TOKEN_APPROX)

    def _fit_transcript(
        self,
        variables: Dict[str, Any],
        template: PromptTemplate,
        context_window_tokens: int,
    ) -> tuple[str, bool]:
        """
        Truncate the transcript text so the total prompt fits in the context window.

        Returns:
            (transcript_text, was_truncated)
        """
        transcript: str = variables.get("transcript_text", "")
        if not transcript:
            return transcript, False

        # Calculate overhead: system + user template without transcript
        placeholder_text = "{transcript_text}"
        user_without_transcript = self._render(
            template.user_template.replace(placeholder_text, ""),
            variables,
        )
        overhead_tokens = (
            self._estimate_tokens(template.system_msg)
            + self._estimate_tokens(user_without_transcript)
            + template.max_tokens          # reserve for completion
            + SAFETY_OVERHEAD_TOKENS
        )

        available_tokens   = context_window_tokens - overhead_tokens
        available_chars    = max(1000, available_tokens * CHARS_PER_TOKEN_APPROX)

        if len(transcript) <= available_chars:
            return transcript, False

        # Truncate at a sentence boundary where possible
        truncated = transcript[:available_chars]
        last_period = truncated.rfind(".")
        if last_period > available_chars * 0.8:
            truncated = truncated[:last_period + 1]

        truncated += "\n\n[TRANSCRIPT TRUNCATED — CONTEXT WINDOW LIMIT REACHED]"
        return truncated, True


# ============================================
# MODULE-LEVEL SINGLETON
# ============================================

prompt_builder = PromptBuilder()
