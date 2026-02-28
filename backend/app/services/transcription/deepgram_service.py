"""
Deepgram Service
Vocaply Platform - Day 7

Deepgram API client for audio transcription with speaker diarization.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, AsyncIterator
from datetime import datetime

import httpx
from deepgram import AsyncDeepgramClient

from app.core.config import settings


class DeepgramService:
    """
    Wrapper for Deepgram API.
    Handles audio transcription with speaker diarization and timestamps.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.DEEPGRAM_API_KEY
        self.client = AsyncDeepgramClient(api_key=self.api_key)
        self.base_url = "https://api.deepgram.com/v1"

    # ============================================
    # TRANSCRIBE FROM URL
    # ============================================

    async def transcribe_from_url(
        self,
        audio_url: str,
        language: str = "en",
        model: str = "nova-2",
        diarize: bool = True,
        punctuate: bool = True,
        smart_format: bool = True,
        paragraphs: bool = True,
        detect_language: bool = False,
    ) -> Dict[str, Any]:
        """
        Transcribe audio from URL (Backblaze B2).
        
        Returns Deepgram response with:
        - results.channels[0].alternatives[0].transcript (full text)
        - results.channels[0].alternatives[0].words (word-level timestamps)
        - results.channels[0].alternatives[0].paragraphs.paragraphs (speaker turns)
        """
        try:
            # Make request
            response = await self.client.listen.v1.media.transcribe_url(
                url=audio_url,
                model=model,
                language=language if not detect_language else None,
                detect_language=detect_language,
                punctuate=punctuate,
                diarize=diarize,
                smart_format=smart_format,
                paragraphs=paragraphs,
                utterances=True,
                utt_split=0.8,  # Split utterances on 0.8s silence
            )

            # Extract result
            result = response.model_dump() if hasattr(response, "model_dump") else response.dict() if hasattr(response, "dict") else response

            return {
                "success": True,
                "result": result,
                "request_id": result.get("metadata", {}).get("request_id"),
                "duration": result.get("metadata", {}).get("duration"),
                "model_info": result.get("metadata", {}).get("model_info"),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    # ============================================
    # TRANSCRIBE FROM FILE
    # ============================================

    async def transcribe_from_file(
        self,
        file_path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Transcribe from local file path"""
        try:
            with open(file_path, "rb") as audio:
                buffer_data = audio.read()

            response = await self.client.listen.v1.media.transcribe_file(
                request=buffer_data,
                model=kwargs.get("model", "nova-2"),
                language=kwargs.get("language", "en"),
                diarize=kwargs.get("diarize", True),
                punctuate=kwargs.get("punctuate", True),
                smart_format=kwargs.get("smart_format", True),
                paragraphs=kwargs.get("paragraphs", True),
            )

            result = response.model_dump() if hasattr(response, "model_dump") else response.dict() if hasattr(response, "dict") else response

            return {
                "success": True,
                "result": result,
                "request_id": result.get("metadata", {}).get("request_id"),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    # ============================================
    # PARSE RESPONSE
    # ============================================

    def parse_transcription(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Deepgram response into structured format.
        Extracts: full text, speaker turns, word timestamps.
        """
        try:
            metadata = result.get("metadata", {})
            channels = result.get("results", {}).get("channels", [])
            
            if not channels:
                return {
                    "success": False,
                    "error": "No channels in response"
                }

            channel = channels[0]
            alternatives = channel.get("alternatives", [])
            
            if not alternatives:
                return {
                    "success": False,
                    "error": "No alternatives in response"
                }

            alternative = alternatives[0]

            # Full transcript
            full_text = alternative.get("transcript", "")

            # Words with timestamps
            words = alternative.get("words", [])

            # Paragraphs (speaker turns)
            paragraphs = alternative.get("paragraphs", {}).get("paragraphs", [])

            # Extract speakers from paragraphs
            speaker_turns = []
            for para in paragraphs:
                speaker_turns.append({
                    "speaker": para.get("speaker"),
                    "text": " ".join([s.get("text", "") for s in para.get("sentences", [])]),
                    "start": para.get("start"),
                    "end": para.get("end"),
                    "num_words": para.get("num_words"),
                    "sentences": para.get("sentences", []),
                })

            # Confidence scoring
            confidences = [w.get("confidence", 0) for w in words if "confidence" in w]
            avg_confidence = sum(confidences) / len(confidences) if confidences else None

            return {
                "success": True,
                "full_text": full_text,
                "words": words,
                "speaker_turns": speaker_turns,
                "average_confidence": avg_confidence,
                "duration": metadata.get("duration"),
                "language": metadata.get("detected_language") or metadata.get("language"),
                "model": metadata.get("model_info", {}).get("name"),
                "request_id": metadata.get("request_id"),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Parse error: {str(e)}",
            }

    # ============================================
    # EXTRACT SPEAKERS
    # ============================================

    def extract_speakers(self, speaker_turns: List[Dict]) -> List[Dict[str, Any]]:
        """
        Aggregate speaker statistics from turns.
        Returns list of unique speakers with word counts, durations.
        """
        speakers_map = {}

        for turn in speaker_turns:
            speaker_id = str(turn.get("speaker", "unknown"))
            
            if speaker_id not in speakers_map:
                speakers_map[speaker_id] = {
                    "id": speaker_id,
                    "name": None,
                    "email": None,
                    "word_count": 0,
                    "duration": 0.0,
                    "turn_count": 0,
                }

            speakers_map[speaker_id]["word_count"] += turn.get("num_words", 0)
            speakers_map[speaker_id]["duration"] += (turn.get("end", 0) - turn.get("start", 0))
            speakers_map[speaker_id]["turn_count"] += 1

        return list(speakers_map.values())

    # ============================================
    # STREAMING (Advanced)
    # ============================================

    async def transcribe_streaming(
        self,
        audio_stream: AsyncIterator[bytes],
        language: str = "en",
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream transcription results in real-time.
        Useful for live meeting bot.
        """
        # Note: Deepgram Python SDK has streaming support
        # This is a placeholder for future implementation
        raise NotImplementedError("Streaming transcription not yet implemented")

    # ============================================
    # COST ESTIMATION
    # ============================================

    def estimate_cost(self, duration_seconds: float, model: str = "nova-2") -> float:
        """
        Estimate Deepgram cost.
        Pricing (as of 2024):
        - Nova-2: $0.0043/min ($0.258/hour)
        - Nova: $0.0059/min ($0.354/hour)
        - Base: $0.0125/min ($0.75/hour)
        """
        pricing = {
            "nova-2": 0.0043,
            "nova": 0.0059,
            "base": 0.0125,
        }

        price_per_minute = pricing.get(model, pricing["nova-2"])
        minutes = duration_seconds / 60
        return minutes * price_per_minute

    # ============================================
    # HEALTH CHECK
    # ============================================

    async def health_check(self) -> bool:
        """Verify Deepgram API key is valid"""
        try:
            # Make a minimal request to verify API key
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/projects",
                    headers={"Authorization": f"Token {self.api_key}"},
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False