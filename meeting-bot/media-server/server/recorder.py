"""
Recorder
Records audio streams to WAV files
"""

import asyncio
import wave
from pathlib import Path
from typing import Optional
from datetime import datetime

from config.media_config import settings


class Recorder:
    """
    Records audio stream to WAV file.
    
    Audio format:
    - Sample rate: 16kHz
    - Channels: Mono (1)
    - Bit depth: 16-bit PCM
    """

    def __init__(self, meeting_id: str):
        self.meeting_id = meeting_id
        
        # File paths
        self.temp_dir = Path(settings.TEMP_DIR)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.wav_path = self.temp_dir / f"{meeting_id}.wav"
        
        # WAV file
        self.wav_file: Optional[wave.Wave_write] = None
        
        # State
        self.is_recording = False
        self.started_at: Optional[datetime] = None
        self.finalized_at: Optional[datetime] = None
        
        # Stats
        self.bytes_written = 0
        self.chunks_written = 0

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start(self):
        """Start recording"""
        if self.is_recording:
            return
        
        print(f"[Recorder] Starting for meeting {self.meeting_id}")
        
        # Open WAV file
        self.wav_file = wave.open(str(self.wav_path), 'wb')
        
        # Set parameters
        self.wav_file.setnchannels(settings.CHANNELS)
        self.wav_file.setsampwidth(settings.BITS_PER_SAMPLE // 8)
        self.wav_file.setframerate(settings.SAMPLE_RATE)
        
        self.is_recording = True
        self.started_at = datetime.utcnow()
        
        print(f"[Recorder] Recording to: {self.wav_path}")

    async def write(self, data: bytes):
        """Write audio data to file"""
        if not self.is_recording or not self.wav_file:
            return
        
        try:
            # Write frames
            self.wav_file.writeframes(data)
            
            # Update stats
            self.bytes_written += len(data)
            self.chunks_written += 1
            
        except Exception as e:
            print(f"[Recorder] Write error: {e}")

    async def finalize(self) -> Path:
        """
        Finalize recording and close file.
        
        Returns:
            Path to WAV file
        """
        if not self.is_recording:
            return self.wav_path
        
        print(f"[Recorder] Finalizing recording for {self.meeting_id}")
        
        self.is_recording = False
        self.finalized_at = datetime.utcnow()
        
        # Close WAV file
        if self.wav_file:
            self.wav_file.close()
            self.wav_file = None
        
        # Calculate duration
        duration = self._calculate_duration()
        
        print(f"[Recorder] Recording complete: {self.bytes_written} bytes, {duration:.1f}s")
        
        return self.wav_path

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HELPERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _calculate_duration(self) -> float:
        """Calculate audio duration from file size"""
        if not self.wav_path.exists():
            return 0.0
        
        # Duration = bytes / (sample_rate * channels * bytes_per_sample)
        bytes_per_sample = settings.BITS_PER_SAMPLE // 8
        bytes_per_second = settings.SAMPLE_RATE * settings.CHANNELS * bytes_per_sample
        
        file_size = self.wav_path.stat().st_size
        
        # Subtract WAV header (44 bytes)
        audio_bytes = file_size - 44
        
        if bytes_per_second > 0:
            return audio_bytes / bytes_per_second
        
        return 0.0

    def get_duration(self) -> float:
        """Get recording duration"""
        if not self.started_at:
            return 0.0
        
        end = self.finalized_at or datetime.utcnow()
        return (end - self.started_at).total_seconds()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stats(self) -> dict:
        """Get recording statistics"""
        return {
            'meeting_id': self.meeting_id,
            'is_recording': self.is_recording,
            'wav_path': str(self.wav_path),
            'bytes_written': self.bytes_written,
            'chunks_written': self.chunks_written,
            'duration': self.get_duration(),
            'file_exists': self.wav_path.exists(),
            'file_size': self.wav_path.stat().st_size if self.wav_path.exists() else 0,
        }