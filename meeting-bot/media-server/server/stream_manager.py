"""
Stream Manager
Manages WebSocket connections and audio streams
"""

import asyncio
from typing import Dict, Optional
from datetime import datetime
import uuid

from websockets.server import WebSocketServerProtocol

from server.recorder import Recorder
from config.media_config import settings


class AudioStream:
    """Represents a single audio stream from a bot"""
    
    def __init__(
        self,
        stream_id: str,
        meeting_id: str,
        websocket: WebSocketServerProtocol,
    ):
        self.stream_id = stream_id
        self.meeting_id = meeting_id
        self.websocket = websocket
        
        # State
        self.connected_at = datetime.utcnow()
        self.last_data_at: Optional[datetime] = None
        self.is_active = True
        
        # Stats
        self.bytes_received = 0
        self.chunks_received = 0
        
        # Recorder
        self.recorder: Optional[Recorder] = None

    def update_activity(self, bytes_count: int):
        """Update stream activity metrics"""
        self.last_data_at = datetime.utcnow()
        self.bytes_received += bytes_count
        self.chunks_received += 1

    def get_duration(self) -> float:
        """Get stream duration in seconds"""
        if not self.connected_at:
            return 0.0
        
        end = self.last_data_at or datetime.utcnow()
        return (end - self.connected_at).total_seconds()

    def to_dict(self) -> dict:
        """Convert to dict for metrics"""
        return {
            'stream_id': self.stream_id,
            'meeting_id': self.meeting_id,
            'connected_at': self.connected_at.isoformat(),
            'last_data_at': self.last_data_at.isoformat() if self.last_data_at else None,
            'is_active': self.is_active,
            'bytes_received': self.bytes_received,
            'chunks_received': self.chunks_received,
            'duration': self.get_duration(),
        }


class StreamManager:
    """
    Manages all active audio streams.
    
    Responsibilities:
    - Accept WebSocket connections
    - Register streams per meeting
    - Distribute audio to recorders
    - Handle disconnections
    - Monitor stream health
    """

    def __init__(self):
        # Active streams: meeting_id → AudioStream
        self.streams: Dict[str, AudioStream] = {}
        
        # Stream ID counter
        self._stream_counter = 0
        
        # Monitoring task
        self._monitor_task: Optional[asyncio.Task] = None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start(self):
        """Start stream manager"""
        print("[StreamManager] Starting...")
        
        # Start monitoring task
        self._monitor_task = asyncio.create_task(self._monitor_streams())
        
        print("[StreamManager] Started")

    async def stop(self):
        """Stop stream manager"""
        print("[StreamManager] Stopping...")
        
        # Cancel monitoring
        if self._monitor_task:
            self._monitor_task.cancel()
        
        # Close all streams
        for stream in list(self.streams.values()):
            await self.unregister_stream(stream.stream_id)
        
        print("[StreamManager] Stopped")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STREAM REGISTRATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def register_stream(
        self,
        meeting_id: str,
        websocket: WebSocketServerProtocol,
    ) -> AudioStream:
        """
        Register a new audio stream.
        
        Returns:
            AudioStream instance
        """
        # Check max streams
        if len(self.streams) >= settings.MAX_STREAMS:
            raise RuntimeError(f"Max streams ({settings.MAX_STREAMS}) reached")
        
        # Generate stream ID
        stream_id = f"stream_{self._stream_counter}"
        self._stream_counter += 1
        
        # Create stream
        stream = AudioStream(stream_id, meeting_id, websocket)
        
        # Create recorder
        stream.recorder = Recorder(meeting_id)
        await stream.recorder.start()
        
        # Store stream
        self.streams[stream_id] = stream
        
        print(f"[StreamManager] Registered stream {stream_id} for meeting {meeting_id}")
        
        return stream

    async def unregister_stream(self, stream_id: str):
        """Unregister and cleanup stream"""
        stream = self.streams.get(stream_id)
        if not stream:
            return
        
        print(f"[StreamManager] Unregistering stream {stream_id}")
        
        # Mark inactive
        stream.is_active = False
        
        # Finalize recording
        if stream.recorder:
            await stream.recorder.finalize()
        
        # Remove from active streams
        del self.streams[stream_id]
        
        print(f"[StreamManager] Stream {stream_id} unregistered")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AUDIO HANDLING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def handle_audio_data(self, stream_id: str, data: bytes):
        """
        Handle incoming audio data from stream.
        
        Args:
            stream_id: Stream identifier
            data: Raw audio bytes (PCM or WAV)
        """
        stream = self.streams.get(stream_id)
        if not stream or not stream.is_active:
            return
        
        # Update activity
        stream.update_activity(len(data))
        
        # Write to recorder
        if stream.recorder:
            await stream.recorder.write(data)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # QUERIES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stream(self, stream_id: str) -> Optional[AudioStream]:
        """Get stream by ID"""
        return self.streams.get(stream_id)

    def get_active_streams(self) -> list:
        """Get all active streams"""
        return [s for s in self.streams.values() if s.is_active]

    def get_stream_count(self) -> int:
        """Get number of active streams"""
        return len(self.get_active_streams())

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MONITORING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _monitor_streams(self):
        """Background task to monitor stream health"""
        while True:
            try:
                await asyncio.sleep(settings.HEARTBEAT_INTERVAL)
                
                # Check for idle streams
                now = datetime.utcnow()
                
                for stream_id, stream in list(self.streams.items()):
                    if not stream.is_active:
                        continue
                    
                    # Check timeout
                    if stream.last_data_at:
                        idle_time = (now - stream.last_data_at).total_seconds()
                        
                        if idle_time > settings.STREAM_TIMEOUT:
                            print(f"[StreamManager] Stream {stream_id} idle timeout ({idle_time}s)")
                            await self.unregister_stream(stream_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[StreamManager] Monitor error: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stats(self) -> dict:
        """Get stream manager statistics"""
        return {
            'active_streams': self.get_stream_count(),
            'total_streams': len(self.streams),
            'max_streams': settings.MAX_STREAMS,
            'streams': [s.to_dict() for s in self.get_active_streams()],
        }