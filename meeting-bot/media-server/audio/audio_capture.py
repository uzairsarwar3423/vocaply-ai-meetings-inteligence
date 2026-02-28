"""
Audio Capture Server
WebSocket server that receives audio streams from bots
"""

import asyncio
import os
from pathlib import Path
from typing import Dict
from datetime import datetime

import websockets
from websockets.server import WebSocketServerProtocol


class AudioCaptureServer:
    """
    WebSocket server for receiving audio streams from Zoom bots.
    
    Each bot connects via WebSocket and streams PCM audio data.
    Server writes audio to files for later transcription.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8002,
        recording_dir: str = "/tmp/recordings",
    ):
        self.host = host
        self.port = port
        self.recording_dir = Path(recording_dir)
        self.recording_dir.mkdir(parents=True, exist_ok=True)
        
        # Active connections: meeting_id → websocket
        self.connections: Dict[str, WebSocketServerProtocol] = {}
        
        # Active file handles: meeting_id → file
        self.files: Dict[str, any] = {}

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SERVER LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start(self):
        """Start WebSocket server"""
        print(f"[AudioServer] Starting on {self.host}:{self.port}")
        
        async with websockets.serve(
            self.handle_connection,
            self.host,
            self.port,
            ping_interval=10,
            ping_timeout=5,
        ):
            print(f"[AudioServer] Listening on ws://{self.host}:{self.port}/audio")
            await asyncio.Future()  # Run forever

    async def handle_connection(
        self,
        websocket: WebSocketServerProtocol,
        path: str,
    ):
        """Handle incoming WebSocket connection"""
        # Extract meeting_id from query params
        # URL format: ws://host:port/audio?meeting_id=xxx
        meeting_id = self._extract_meeting_id(path)
        
        if not meeting_id:
            await websocket.close(1008, "Missing meeting_id")
            return
        
        print(f"[AudioServer] Bot connected for meeting {meeting_id}")
        
        # Store connection
        self.connections[meeting_id] = websocket
        
        # Open file for writing
        recording_path = self.recording_dir / f"{meeting_id}.pcm"
        file_handle = open(recording_path, 'wb')
        self.files[meeting_id] = file_handle
        
        try:
            async for message in websocket:
                # Receive audio bytes
                if isinstance(message, bytes):
                    # Write to file
                    file_handle.write(message)
                    file_handle.flush()
                
        except websockets.exceptions.ConnectionClosed:
            print(f"[AudioServer] Connection closed for meeting {meeting_id}")
        
        finally:
            # Cleanup
            self.connections.pop(meeting_id, None)
            
            if meeting_id in self.files:
                self.files[meeting_id].close()
                del self.files[meeting_id]
            
            print(f"[AudioServer] Cleaned up meeting {meeting_id}")

    def _extract_meeting_id(self, path: str) -> str:
        """Extract meeting_id from URL path"""
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(path)
        query = parse_qs(parsed.query)
        
        if 'meeting_id' in query:
            return query['meeting_id'][0]
        
        return ""

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stats(self) -> dict:
        """Get server statistics"""
        return {
            "active_connections": len(self.connections),
            "meetings": list(self.connections.keys()),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def main():
    """Run audio capture server"""
    server = AudioCaptureServer(
        host="0.0.0.0",
        port=8002,
        recording_dir=os.getenv("RECORDING_PATH", "/tmp/recordings"),
    )
    
    await server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[AudioServer] Shutting down...")