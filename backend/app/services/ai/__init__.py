"""
AI Service Package
Vocaply Platform - Day 9/10: OpenAI Integration & Action Item Extraction
File: backend/app/services/ai/__init__.py
"""
from app.services.ai.openai_service import openai_service, OpenAIService, AIResult
from app.services.ai.prompt_templates import (
    TemplateKey,
    PromptTemplate,
    get_template,
    list_templates,
)
from app.services.ai.prompt_builder import prompt_builder, PromptBuilder
from app.services.ai.token_tracker import token_tracker, TokenTracker
from app.services.ai.action_item_extractor import ActionItemExtractor, get_extractor
from app.services.ai.entity_matcher import EntityMatcher, AttendeeCandidate, MatchResult

__all__ = [
    # Service singletons
    "openai_service",
    "prompt_builder",
    "token_tracker",
    # Classes
    "OpenAIService",
    "PromptBuilder",
    "TokenTracker",
    "AIResult",
    # Template utils
    "TemplateKey",
    "PromptTemplate",
    "get_template",
    "list_templates",
    # Day 10: Extraction
    "ActionItemExtractor",
    "get_extractor",
    "EntityMatcher",
    "AttendeeCandidate",
    "MatchResult",
]
