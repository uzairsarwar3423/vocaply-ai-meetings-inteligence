"""
Prompt Templates
Vocaply Platform - Day 9: OpenAI Integration & Prompt Engineering
File: backend/app/services/ai/prompt_templates.py

All prompt templates with versioning support.
Each template is a PromptTemplate dataclass with:
    - version      : semver string
    - system_msg   : system role content
    - user_template: Jinja2-style {variable} placeholders
    - max_tokens   : suggested completion cap
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


# ============================================
# TEMPLATE REGISTRY
# ============================================

class TemplateKey(str, Enum):
    """Canonical keys used to look up templates."""
    MEETING_SUMMARY        = "meeting_summary"
    ACTION_ITEM_EXTRACTION = "action_item_extraction"
    KEY_DECISIONS          = "key_decisions"
    PARTICIPANT_ANALYSIS   = "participant_analysis"
    TOPIC_EXTRACTION       = "topic_extraction"
    SENTIMENT_ANALYSIS     = "sentiment_analysis"


@dataclass
class PromptTemplate:
    key:           TemplateKey
    version:       str
    system_msg:    str
    user_template: str
    max_tokens:    int = 1000
    temperature:   float = 0.3
    # JSON-mode hint: if True the caller should set response_format={"type":"json_object"}
    json_mode:     bool = True
    description:   str = ""


# ============================================
# TEMPLATE DEFINITIONS
# ============================================

_COMMON_JSON_REMINDER = (
    "\n\nIMPORTANT: Return ONLY valid JSON with no markdown fences or extra text."
)

# ---------- MEETING SUMMARY ----------------

MEETING_SUMMARY_V1 = PromptTemplate(
    key=TemplateKey.MEETING_SUMMARY,
    version="1.0.0",
    description="Generates a structured meeting summary from a transcript.",
    system_msg=(
        "You are an expert meeting analyst. Your task is to read a meeting "
        "transcript and produce a concise, well-structured summary. "
        "Focus on clarity, brevity, and actionability. "
        "Always respond in JSON format."
    ),
    user_template="""Analyze the following meeting transcript and generate a structured summary.

MEETING DETAILS:
- Title: {meeting_title}
- Date: {meeting_date}
- Duration: {duration_minutes} minutes
- Participants: {participant_names}

TRANSCRIPT:
{transcript_text}

Return a JSON object with this exact structure:
{{
  "executive_summary": "2-3 sentence high-level summary",
  "main_topics": ["topic 1", "topic 2", ...],
  "key_outcomes": ["outcome 1", "outcome 2", ...],
  "decisions_made": ["decision 1", ...],
  "open_questions": ["question 1", ...],
  "next_steps": ["step 1", ...],
  "sentiment": "positive|neutral|negative",
  "meeting_effectiveness_score": 1-10,
  "word_count": <integer>
}}""" + _COMMON_JSON_REMINDER,
    max_tokens=1500,
    temperature=0.2,
    json_mode=True,
)

# ---------- ACTION ITEM EXTRACTION ---------

ACTION_ITEM_EXTRACTION_V1 = PromptTemplate(
    key=TemplateKey.ACTION_ITEM_EXTRACTION,
    version="1.0.0",
    description="Extracts structured action items from a transcript.",
    system_msg=(
        "You are an expert at identifying action items in meeting transcripts. "
        "Extract every explicit or strongly implied commitment, task, or follow-up. "
        "Always respond in JSON format."
    ),
    user_template="""Extract all action items from the following meeting transcript.

MEETING CONTEXT:
- Title: {meeting_title}
- Date: {meeting_date}
- Participants: {participant_names}

TRANSCRIPT:
{transcript_text}

Return a JSON object with this exact structure:
{{
  "action_items": [
    {{
      "title": "Short task title (max 100 chars)",
      "description": "Detail about the task",
      "assignee_name": "Person's name or null if unassigned",
      "assignee_email": "email if determinable, else null",
      "due_date": "YYYY-MM-DD or null",
      "priority": "high|medium|low",
      "category": "follow_up|research|approval|communication|other",
      "confidence": 0.0-1.0
    }}
  ],
  "total_count": <integer>,
  "unassigned_count": <integer>
}}""" + _COMMON_JSON_REMINDER,
    max_tokens=2000,
    temperature=0.1,
    json_mode=True,
)

# ---------- KEY DECISIONS ------------------

KEY_DECISIONS_V1 = PromptTemplate(
    key=TemplateKey.KEY_DECISIONS,
    version="1.0.0",
    description="Extracts key decisions made during the meeting.",
    system_msg=(
        "You are an expert meeting analyst specializing in decision tracking. "
        "Identify every formal or informal decision recorded in the transcript. "
        "Always respond in JSON format."
    ),
    user_template="""Identify all key decisions made during this meeting.

MEETING CONTEXT:
- Title: {meeting_title}
- Date: {meeting_date}
- Participants: {participant_names}

TRANSCRIPT:
{transcript_text}

Return a JSON object with this exact structure:
{{
  "decisions": [
    {{
      "title": "Short decision title",
      "description": "What was decided and why",
      "decision_maker": "Person who made/confirmed the decision or null",
      "rationale": "Reasoning behind decision or null",
      "impact": "high|medium|low",
      "category": "strategic|tactical|operational|technical|financial|other",
      "confidence": 0.0-1.0,
      "timestamp_hint": "Quote from transcript near the decision or null"
    }}
  ],
  "total_count": <integer>
}}""" + _COMMON_JSON_REMINDER,
    max_tokens=1500,
    temperature=0.15,
    json_mode=True,
)

# ---------- PARTICIPANT IDENTIFICATION -----

PARTICIPANT_ANALYSIS_V1 = PromptTemplate(
    key=TemplateKey.PARTICIPANT_ANALYSIS,
    version="1.0.0",
    description="Identifies and profiles participants from the transcript.",
    system_msg=(
        "You are an expert at analyzing meeting dynamics and participant roles. "
        "Identify who participated, their roles, and their engagement level. "
        "Always respond in JSON format."
    ),
    user_template="""Analyze the participants of this meeting from the transcript.

MEETING CONTEXT:
- Title: {meeting_title}
- Date: {meeting_date}
- Known attendees (from calendar): {participant_names}

TRANSCRIPT:
{transcript_text}

Return a JSON object with this exact structure:
{{
  "participants": [
    {{
      "name": "Speaker name",
      "email": "email if identifiable, else null",
      "role": "organizer|presenter|contributor|observer",
      "speaking_time_percent": 0-100,
      "key_contributions": ["contribution 1", ...],
      "sentiment": "positive|neutral|negative",
      "engagement_level": "high|medium|low"
    }}
  ],
  "total_speakers": <integer>,
  "dominant_speaker": "name of person who spoke most",
  "meeting_dynamic": "collaborative|presenter-led|discussion|one-on-one|other"
}}""" + _COMMON_JSON_REMINDER,
    max_tokens=1200,
    temperature=0.2,
    json_mode=True,
)

# ---------- TOPIC EXTRACTION ---------------

TOPIC_EXTRACTION_V1 = PromptTemplate(
    key=TemplateKey.TOPIC_EXTRACTION,
    version="1.0.0",
    description="Extracts and categorizes topics discussed in the meeting.",
    system_msg=(
        "You are an expert at identifying and categorizing discussion topics in meetings. "
        "Extract topics hierarchically with time estimates. "
        "Always respond in JSON format."
    ),
    user_template="""Extract and categorize the main topics discussed in this meeting.

MEETING CONTEXT:
- Title: {meeting_title}
- Date: {meeting_date}
- Duration: {duration_minutes} minutes
- Participants: {participant_names}

TRANSCRIPT:
{transcript_text}

Return a JSON object with this exact structure:
{{
  "topics": [
    {{
      "name": "Topic name",
      "description": "Brief description of what was discussed",
      "time_spent_percent": 0-100,
      "subtopics": ["subtopic 1", "subtopic 2"],
      "category": "technical|business|planning|review|problem-solving|other",
      "keywords": ["keyword1", "keyword2"]
    }}
  ],
  "total_topics": <integer>,
  "primary_topic": "name of main focus",
  "off_topic_time_percent": 0-100
}}""" + _COMMON_JSON_REMINDER,
    max_tokens=1200,
    temperature=0.2,
    json_mode=True,
)

# ---------- SENTIMENT ANALYSIS -------------

SENTIMENT_ANALYSIS_V1 = PromptTemplate(
    key=TemplateKey.SENTIMENT_ANALYSIS,
    version="1.0.0",
    description="Analyses overall and per-speaker sentiment.",
    system_msg=(
        "You are an expert sentiment analyst for professional meetings. "
        "Analyse tone, mood, and emotional undertones objectively. "
        "Always respond in JSON format."
    ),
    user_template="""Perform sentiment analysis on this meeting transcript.

MEETING CONTEXT:
- Title: {meeting_title}
- Date: {meeting_date}
- Participants: {participant_names}

TRANSCRIPT:
{transcript_text}

Return a JSON object with this exact structure:
{{
  "overall_sentiment": "positive|neutral|negative",
  "overall_score": -1.0 to 1.0,
  "sentiment_progression": "improving|stable|declining",
  "per_speaker_sentiment": {{
    "Speaker Name": {{
      "sentiment": "positive|neutral|negative",
      "score": -1.0 to 1.0,
      "dominant_emotions": ["emotion1", ...]
    }}
  }},
  "highlighted_moments": [
    {{
      "type": "positive|negative|tension|resolution",
      "description": "Brief description",
      "quote": "Relevant quote from transcript"
    }}
  ],
  "meeting_health_score": 1-10
}}""" + _COMMON_JSON_REMINDER,
    max_tokens=1200,
    temperature=0.2,
    json_mode=True,
)


# ============================================
# TEMPLATE REGISTRY
# ============================================

TEMPLATE_REGISTRY: Dict[TemplateKey, list[PromptTemplate]] = {
    TemplateKey.MEETING_SUMMARY:        [MEETING_SUMMARY_V1],
    TemplateKey.ACTION_ITEM_EXTRACTION: [ACTION_ITEM_EXTRACTION_V1],
    TemplateKey.KEY_DECISIONS:          [KEY_DECISIONS_V1],
    TemplateKey.PARTICIPANT_ANALYSIS:   [PARTICIPANT_ANALYSIS_V1],
    TemplateKey.TOPIC_EXTRACTION:       [TOPIC_EXTRACTION_V1],
    TemplateKey.SENTIMENT_ANALYSIS:     [SENTIMENT_ANALYSIS_V1],
}


def get_template(key: TemplateKey, version: str | None = None) -> PromptTemplate:
    """
    Return the requested template (latest if version not specified).

    Args:
        key:     Template key from TemplateKey enum.
        version: Optional semver string. Returns latest if None.

    Raises:
        KeyError:   Template key not found.
        ValueError: Requested version not found.
    """
    templates = TEMPLATE_REGISTRY[key]
    if not version:
        return templates[-1]  # latest = last in list
    for tmpl in templates:
        if tmpl.version == version:
            return tmpl
    raise ValueError(
        f"Template '{key}' version '{version}' not found. "
        f"Available: {[t.version for t in templates]}"
    )


def list_templates() -> list[dict]:
    """Return a summary of all registered templates."""
    result = []
    for key, templates in TEMPLATE_REGISTRY.items():
        latest = templates[-1]
        result.append({
            "key":         key.value,
            "versions":    [t.version for t in templates],
            "latest":      latest.version,
            "description": latest.description,
            "max_tokens":  latest.max_tokens,
            "json_mode":   latest.json_mode,
        })
    return result
