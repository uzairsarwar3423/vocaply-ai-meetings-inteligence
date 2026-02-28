"""
Audio Handler
Captures audio from Zoom Meeting SDK and streams to media server
"""

import asyncio
import wave
import struct
from typing import Optional
from datetime import datetime
from pathlib import Path

import websockets
import numpy as np

from config.zoom_config import settings


class AudioHandler:
    """
    Handles audio capture from Zoom and streaming to media server.
    
    Audio format:
    - Sample rate: 16kHz (16000 Hz)
    - Channels: Mono (1)
    - Bit depth: 16-bit PCM
    - Buffer size: 1024 samples (~64ms at 16kHz)
    """

    def __init__(self, meeting_id: str):
        self.meeting_id = meeting_id
        self.is_recording = False
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        
        # Audio buffers
        self.audio_buffer = bytearray()
        self.sample_rate = settings.AUDIO_SAMPLE_RATE
        self.channels = settings.AUDIO_CHANNELS
        self.bits_per_sample = settings.AUDIO_BITS_PER_SAMPLE
        
        # File recording (fallback)
        self.recording_path: Optional[Path] = None
        self.wave_file: Optional[wave.Wave_write] = None
        
        # Stats
        self.bytes_captured = 0
        self.started_at: Optional[datetime] = None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start(self):
        """Start audio capture"""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.started_at = datetime.utcnow()
        
        # Connect to media server
        try:
            self.websocket = await websockets.connect(
                f"{settings.MEDIA_SERVER_URL}?meeting_id={self.meeting_id}",
                ping_interval=10,
                ping_timeout=5,
            )
            print(f"Connected to media server for meeting {self.meeting_id}")
        except Exception as e:
            print(f"Failed to connect to media server: {e}")
            print("Falling back to file recording")
            self._init_file_recording()

    async def stop(self):
        """Stop audio capture"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        # Close websocket
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        # Close wave file
        if self.wave_file:
            self.wave_file.close()
            self.wave_file = None
        
        print(f"Audio capture stopped. Total bytes: {self.bytes_captured}")

    def _init_file_recording(self):
        """Initialize WAV file recording as fallback"""
        recording_dir = Path("/tmp/recordings")
        recording_dir.mkdir(parents=True, exist_ok=True)
        
        self.recording_path = recording_dir / f"{self.meeting_id}.wav"
        
        self.wave_file = wave.open(str(self.recording_path), 'wb')
        self.wave_file.setnchannels(self.channels)
        self.wave_file.setsampwidth(self.bits_per_sample // 8)
        self.wave_file.setframerate(self.sample_rate)
        
        print(f"Recording to file: {self.recording_path}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AUDIO CAPTURE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def on_audio_raw_data(self, data: bytes):
        """
        Called by Zoom SDK with raw PCM audio data.
        
        Args:
            data: Raw PCM audio bytes (16-bit signed integers)
        """
        if not self.is_recording:
            return
        
        self.bytes_captured += len(data)
        
        # Stream to media server
        if self.websocket:
            try:
                await self.websocket.send(data)
            except Exception as e:
                print(f"Failed to stream audio: {e}")
                # Fall back to file
                if not self.wave_file:
                    self._init_file_recording()
        
        # Write to file (if fallback)
        if self.wave_file:
            self.wave_file.writeframes(data)

    def on_mixed_audio_raw_data(
        self,
        data: bytes,
        sample_rate: int,
        number_of_channels: int,
    ):
        """
        Called by Zoom SDK with mixed audio (all participants).
        This is preferred for recording meetings.
        """
        # Resample if needed
        if sample_rate != self.sample_rate:
            data = self._resample_audio(data, sample_rate, self.sample_rate)
        
        # Convert stereo to mono if needed
        if number_of_channels > 1:
            data = self._to_mono(data, number_of_channels)
        
        # Process
        asyncio.create_task(self.on_audio_raw_data(data))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AUDIO PROCESSING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _to_mono(self, data: bytes, channels: int) -> bytes:
        """Convert multi-channel audio to mono"""
        # Convert bytes to numpy array
        samples = np.frombuffer(data, dtype=np.int16)
        
        # Reshape to (n_samples, n_channels)
        samples = samples.reshape(-1, channels)
        
        # Average across channels
        mono = samples.mean(axis=1).astype(np.int16)
        
        return mono.tobytes()

    def _resample_audio(self, data: bytes, from_rate: int, to_rate: int) -> bytes:
        """Resample audio to target sample rate"""
        if from_rate == to_rate:
            return data
        
        # Convert bytes to numpy array
        samples = np.frombuffer(data, dtype=np.int16)
        
        # Calculate resampling ratio
        ratio = to_rate / from_rate
        new_length = int(len(samples) * ratio)
        
        # Simple linear interpolation
        resampled = np.interp(
            np.linspace(0, len(samples) - 1, new_length),
            np.arange(len(samples)),
            samples,
        ).astype(np.int16)
        
        return resampled.tobytes()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stats(self) -> dict:
        """Get audio capture statistics"""
        duration = 0
        if self.started_at:
            duration = (datetime.utcnow() - self.started_at).total_seconds()
        
        return {
            "is_recording": self.is_recording,
            "bytes_captured": self.bytes_captured,
            "duration_seconds": duration,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "recording_path": str(self.recording_path) if self.recording_path else None,
            "streaming": self.websocket is not None,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUDIO CALLBACK ADAPTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AudioCallback:
    """
    Adapter to bridge Zoom SDK C callbacks to Python AudioHandler.
    Zoom SDK uses C-style function pointers for callbacks.
    """

    def __init__(self, audio_handler: AudioHandler):
        self.handler = audio_handler

    def on_mixed_audio_raw_data_received(
        self,
        data_ptr,      # Pointer to audio data
        data_length,   # Length in bytes
        sample_rate,   # Sample rate (Hz)
        channels,      # Number of channels
    ):
        """
        C callback function that receives audio from Zoom SDK.
        This gets called from C code, so we need to be careful.
        """
        try:
            # Convert C pointer to Python bytes
            import ctypes
            data = ctypes.string_at(data_ptr, data_length)
            
            # Pass to async handler
            self.handler.on_mixed_audio_raw_data(data, sample_rate, channels)
            
        except Exception as e:
            print(f"Audio callback error: {e}")