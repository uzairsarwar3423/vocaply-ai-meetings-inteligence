"""
Media Server
WebSocket server for audio streaming and recording
"""

import asyncio
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, parse_qs

import websockets
from websockets.server import WebSocketServerProtocol
import httpx

from server.stream_manager import StreamManager
from server.transcoder import Transcoder
from server.storage_uploader import StorageUploader
from config.media_config import settings


class MediaServer:
    """
    Media server for bot audio streams.
    
    Endpoints:
    - ws://host:port/audio?meeting_id=xxx - Audio stream endpoint
    - http://host:port/health - Health check
    - http://host:port/stats - Statistics
    
    Workflow:
    1. Bot connects WebSocket
    2. Register stream for meeting
    3. Receive audio chunks
    4. Write to WAV file
    5. On disconnect:
       - Finalize WAV
       - Transcode to MP3
       - Upload to Backblaze
       - Send completion webhook
       - Cleanup local files
    """

    def __init__(self):
        self.stream_manager = StreamManager()
        self.transcoder = Transcoder()
        self.uploader = StorageUploader()
        
        # HTTP client for webhooks
        self.http_client: Optional[httpx.AsyncClient] = None
        
        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start(self):
        """Start media server"""
        print("🎙️  Media Server starting...")
        
        # Create directories
        Path(settings.RECORDING_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)
        
        # HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={'Authorization': f"Bearer {settings.WEBHOOK_API_KEY}"},
        )
        
        # Start stream manager
        await self.stream_manager.start()
        
        # Start cleanup task
        if not settings.KEEP_LOCAL_FILES:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Start WebSocket server
        async with websockets.serve(
            self.handle_connection,
            settings.HOST,
            settings.PORT,
            ping_interval=settings.HEARTBEAT_INTERVAL,
            ping_timeout=30,
        ):
            print(f"✅ Media Server listening on ws://{settings.HOST}:{settings.PORT}/audio")
            await asyncio.Future()  # Run forever

    async def stop(self):
        """Stop media server"""
        print("🛑 Media Server stopping...")
        
        # Cancel cleanup
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Stop stream manager
        await self.stream_manager.stop()
        
        # Close HTTP client
        if self.http_client:
            await self.http_client.aclose()
        
        print("✅ Media Server stopped")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WEBSOCKET HANDLER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def handle_connection(
        self,
        websocket: WebSocketServerProtocol,
        path: str,
    ):
        """
        Handle WebSocket connection from bot.
        
        URL format: ws://host:port/audio?meeting_id=xxx&company_id=yyy
        """
        # Extract meeting_id from query params
        meeting_id, company_id = self._parse_url(path)
        
        if not meeting_id:
            await websocket.close(1008, "Missing meeting_id parameter")
            return
        
        print(f"[MediaServer] Bot connected for meeting {meeting_id}")
        
        # Register stream
        stream = await self.stream_manager.register_stream(meeting_id, websocket)
        
        try:
            # Receive audio data
            async for message in websocket:
                if isinstance(message, bytes):
                    await self.stream_manager.handle_audio_data(
                        stream.stream_id,
                        message,
                    )
        
        except websockets.exceptions.ConnectionClosed:
            print(f"[MediaServer] Connection closed for meeting {meeting_id}")
        
        finally:
            # Unregister stream
            await self.stream_manager.unregister_stream(stream.stream_id)
            
            # Process recording
            await self._process_recording(meeting_id, company_id)

    def _parse_url(self, path: str) -> tuple:
        """Extract meeting_id and company_id from URL"""
        parsed = urlparse(path)
        query = parse_qs(parsed.query)
        
        meeting_id = query.get('meeting_id', [None])[0]
        company_id = query.get('company_id', ['default'])[0]
        
        return meeting_id, company_id

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # RECORDING PROCESSING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _process_recording(self, meeting_id: str, company_id: str):
        """
        Process recording after stream ends.
        
        Steps:
        1. Transcode WAV to MP3
        2. Upload to Backblaze
        3. Send webhook
        4. Cleanup local files
        """
        print(f"[MediaServer] Processing recording for {meeting_id}")
        
        # Find WAV file
        wav_path = Path(settings.TEMP_DIR) / f"{meeting_id}.wav"
        
        if not wav_path.exists():
            print(f"[MediaServer] WAV file not found: {wav_path}")
            return
        
        try:
            # 1. Transcode
            output_path = await self.transcoder.transcode(
                wav_path,
                output_format=settings.OUTPUT_FORMAT,
            )
            
            if not output_path:
                print(f"[MediaServer] Transcoding failed for {meeting_id}")
                await self._send_webhook(meeting_id, company_id, None, error="Transcoding failed")
                return
            
            # 2. Upload to B2
            recording_url = await self.uploader.upload(
                output_path,
                meeting_id,
                company_id,
            )
            
            if not recording_url:
                print(f"[MediaServer] Upload failed for {meeting_id}")
                await self._send_webhook(meeting_id, company_id, None, error="Upload failed")
                return
            
            # 3. Get audio info
            audio_info = await self.transcoder.get_audio_info(output_path)
            
            # 4. Send webhook
            await self._send_webhook(meeting_id, company_id, recording_url, audio_info=audio_info)
            
            # 5. Cleanup
            if not settings.KEEP_LOCAL_FILES:
                wav_path.unlink(missing_ok=True)
                output_path.unlink(missing_ok=True)
                print(f"[MediaServer] Cleaned up local files for {meeting_id}")
            
            print(f"[MediaServer] Recording processing complete for {meeting_id}")
            
        except Exception as e:
            print(f"[MediaServer] Processing error for {meeting_id}: {e}")
            await self._send_webhook(meeting_id, company_id, None, error=str(e))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WEBHOOK
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _send_webhook(
        self,
        meeting_id: str,
        company_id: str,
        recording_url: Optional[str],
        audio_info: dict = None,
        error: Optional[str] = None,
    ):
        """Send recording completion webhook to backend"""
        if not self.http_client or not settings.WEBHOOK_URL:
            return
        
        from datetime import datetime
        
        payload = {
            'event_type': 'recording.completed' if recording_url else 'recording.failed',
            'meeting_id': meeting_id,
            'company_id': company_id,
            'recording_url': recording_url,
            'audio_info': audio_info or {},
            'error': error,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        try:
            response = await self.http_client.post(
                settings.WEBHOOK_URL,
                json=payload,
            )
            
            response.raise_for_status()
            print(f"[MediaServer] Webhook sent for {meeting_id}")
            
        except Exception as e:
            print(f"[MediaServer] Webhook delivery failed: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CLEANUP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _cleanup_loop(self):
        """Background task to cleanup old files"""
        while True:
            try:
                await asyncio.sleep(settings.CLEANUP_INTERVAL)
                
                print("[MediaServer] Running cleanup...")
                
                # Cleanup temp directory
                temp_dir = Path(settings.TEMP_DIR)
                
                import time
                for file_path in temp_dir.glob("*"):
                    if file_path.is_file():
                        # Delete files older than 24 hours
                        age = time.time() - file_path.stat().st_mtime
                        if age > 86400:  # 24 hours
                            file_path.unlink()
                            print(f"[MediaServer] Cleaned up old file: {file_path.name}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[MediaServer] Cleanup error: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stats(self) -> dict:
        """Get server statistics"""
        return {
            'server': {
                'host': settings.HOST,
                'port': settings.PORT,
                'audio_format': f"{settings.SAMPLE_RATE}Hz {settings.CHANNELS}ch {settings.BITS_PER_SAMPLE}bit",
            },
            'streams': self.stream_manager.get_stats(),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def main():
    """Run media server"""
    server = MediaServer()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())