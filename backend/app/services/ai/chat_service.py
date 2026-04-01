"""
Meeting AI Chat Service
Vocaply Platform - Day 28: Live Transcription & AI Hub
File: backend/app/services/ai/chat_service.py

Handles real-time AI assistant interactions during a live meeting.
"""
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.ai_usage import AIFeatureType
from app.services.ai.openai_service import openai_service
from app.services.websocket_manager import ws_manager
from app.core.websocket import ServerEvent, SubscriptionChannel


class MeetingChatService:
    """
    Assistant service that answers questions about the current meeting.
    Injects context from the transcript into the LLM prompt.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def handle_message(
        self,
        meeting_id: str,
        company_id: str,
        user_id: str,
        message: str,
        request_id: Optional[str] = None
    ):
        """
        Processes a chat message from the user.
        1. Fetches recent transcript context.
        2. Calls OpenAI with meeting context.
        3. Streams/Sends response back via WebSocket.
        """
        logger.info(f"AI Chat: User {user_id} asked in meeting {meeting_id}: {message}")

        try:
            # 1. Load context
            from app.repositories.transcript_repository import TranscriptRepository
            from app.repositories.meeting_repository import MeetingRepository
            
            transcript_repo = TranscriptRepository(self.db)
            meeting_repo    = MeetingRepository(self.db)
            
            meeting = await meeting_repo.get_by_id(uuid.UUID(meeting_id), company_id=company_id)
            if not meeting:
                await self._send_error(user_id, "Meeting not found.", request_id)
                return

            transcript_text = await transcript_repo.get_full_text(uuid.UUID(meeting_id))
            
            # 2. Call OpenAI
            ai_result = await openai_service.analyze(
                feature_type = AIFeatureType.CHAT_ASSISTANT,
                variables    = {
                    "meeting_title": meeting.title,
                    "transcript":    transcript_text[:10000],  # Limit context for now
                    "user_query":    message
                },
                company_id   = company_id,
                meeting_id   = meeting_id,
                user_id      = user_id,
                db           = self.db
            )

            if ai_result.status != "success":
                await self._send_error(user_id, f"AI Error: {ai_result.error}", request_id)
                return

            # 3. Broadcast response to user
            # In a real streaming implementation, we'd use Server-Sent Events or multiple WS frames.
            # For now, we send the complete message as a CHAT_RESPONSE.
            response_text = ai_result.parsed.get("answer", "I'm sorry, I couldn't process that.")
            
            await ws_manager.send_to_user(
                user_id = user_id,
                event   = ServerEvent.CHAT_RESPONSE,
                data    = {
                    "meeting_id":  meeting_id,
                    "answer":      response_text,
                    "request_id":  request_id,
                    "citations":   ai_result.parsed.get("citations", [])
                }
            )

        except Exception as e:
            logger.error(f"AI Chat processing failed: {e}")
            await self._send_error(user_id, "Internal server error during chat processing.", request_id)

    async def _send_error(self, user_id: str, message: str, request_id: Optional[str]):
        await ws_manager.send_to_user(
            user_id = user_id,
            event   = ServerEvent.ERROR,
            data    = {
                "message":    message,
                "request_id": request_id
            }
        )

def get_chat_service(db: AsyncSession) -> MeetingChatService:
    return MeetingChatService(db)
