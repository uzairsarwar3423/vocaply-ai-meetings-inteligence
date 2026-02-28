"""
Audio Mixer
Mixes multiple audio streams in real-time

Note: Currently not used as bots stream one stream per meeting.
This is for future multi-bot scenarios where we want to mix
audio from multiple bots in the same meeting.
"""

import asyncio
from typing import Dict, List
import numpy as np

from config.media_config import settings


class AudioMixer:
    """
    Mixes multiple audio streams into a single output.
    
    Use case:
    - Multiple bots in same meeting (different audio sources)
    - Mixing different audio channels
    - Volume normalization
    
    Currently: Single stream per meeting (no mixing needed)
    Future: Multi-bot meetings require mixing
    """

    def __init__(self, meeting_id: str):
        self.meeting_id = meeting_id
        
        # Audio buffers: stream_id → buffer
        self.buffers: Dict[str, bytearray] = {}
        
        # Mixed output buffer
        self.output_buffer = bytearray()
        
        # Configuration
        self.sample_rate = settings.SAMPLE_RATE
        self.channels = settings.CHANNELS
        self.bits_per_sample = settings.BITS_PER_SAMPLE

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STREAM MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def add_stream(self, stream_id: str):
        """Add a stream to the mixer"""
        if stream_id not in self.buffers:
            self.buffers[stream_id] = bytearray()
            print(f"[AudioMixer] Added stream {stream_id}")

    def remove_stream(self, stream_id: str):
        """Remove a stream from the mixer"""
        if stream_id in self.buffers:
            del self.buffers[stream_id]
            print(f"[AudioMixer] Removed stream {stream_id}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AUDIO PROCESSING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def add_audio(self, stream_id: str, data: bytes):
        """
        Add audio data from a stream.
        
        Args:
            stream_id: Stream identifier
            data: Audio bytes (PCM 16-bit)
        """
        if stream_id not in self.buffers:
            self.add_stream(stream_id)
        
        self.buffers[stream_id].extend(data)

    async def mix(self, chunk_size: int = 4096) -> bytes:
        """
        Mix audio from all streams.
        
        Args:
            chunk_size: Size of chunk to mix (bytes)
        
        Returns:
            Mixed audio bytes
        """
        if not self.buffers:
            return b''
        
        # Check if all streams have enough data
        if not all(len(buf) >= chunk_size for buf in self.buffers.values()):
            return b''
        
        # Extract chunks from each stream
        chunks = []
        for stream_id, buffer in self.buffers.items():
            chunk = bytes(buffer[:chunk_size])
            chunks.append(chunk)
            # Remove consumed data
            del buffer[:chunk_size]
        
        # Mix chunks
        mixed = self._mix_chunks(chunks)
        
        return mixed

    def _mix_chunks(self, chunks: List[bytes]) -> bytes:
        """
        Mix multiple audio chunks.
        
        Method: Average mixing (simple, prevents clipping)
        """
        if not chunks:
            return b''
        
        if len(chunks) == 1:
            return chunks[0]
        
        # Convert to numpy arrays (int16)
        arrays = [np.frombuffer(chunk, dtype=np.int16) for chunk in chunks]
        
        # Ensure all arrays same length (pad if needed)
        max_len = max(len(arr) for arr in arrays)
        padded = [
            np.pad(arr, (0, max_len - len(arr)), 'constant')
            for arr in arrays
        ]
        
        # Stack and average
        stacked = np.stack(padded)
        mixed = stacked.mean(axis=0).astype(np.int16)
        
        return mixed.tobytes()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # VOLUME NORMALIZATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def normalize_volume(self, data: bytes, target_level: float = 0.7) -> bytes:
        """
        Normalize audio volume.
        
        Args:
            data: Audio bytes
            target_level: Target amplitude (0.0-1.0)
        
        Returns:
            Normalized audio
        """
        # Convert to numpy
        samples = np.frombuffer(data, dtype=np.int16)
        
        # Calculate current peak
        peak = np.abs(samples).max()
        
        if peak == 0:
            return data
        
        # Calculate gain
        max_amplitude = 32767  # int16 max
        current_level = peak / max_amplitude
        gain = target_level / current_level
        
        # Apply gain (clip to prevent overflow)
        normalized = np.clip(samples * gain, -32768, 32767).astype(np.int16)
        
        return normalized.tobytes()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stats(self) -> dict:
        """Get mixer statistics"""
        return {
            'meeting_id': self.meeting_id,
            'active_streams': len(self.buffers),
            'buffer_sizes': {
                stream_id: len(buffer)
                for stream_id, buffer in self.buffers.items()
            },
        }