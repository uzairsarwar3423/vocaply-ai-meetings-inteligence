"""
Audio Capture
Captures browser audio via PulseAudio + FFmpeg
"""

import asyncio
import subprocess
import os
from typing import Optional
from pathlib import Path

import websockets


class AudioCapture:
    """
    Captures audio from Chrome via PulseAudio virtual sink.
    
    Method:
    1. Create PulseAudio virtual sink
    2. Redirect Chrome audio to virtual sink
    3. Use FFmpeg to capture from sink
    4. Stream to media server via WebSocket
    """

    def __init__(
        self,
        meeting_id: str,
        media_server_url: str = "ws://localhost:8002/audio",
    ):
        self.meeting_id = meeting_id
        self.media_server_url = media_server_url
        
        # PulseAudio
        self.sink_name = f"vocaply_meet_{meeting_id}"
        self.sink_created = False
        
        # FFmpeg process
        self.ffmpeg_process: Optional[subprocess.Popen] = None
        
        # WebSocket
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        
        # Recording fallback
        self.recording_path = Path(f"/tmp/recordings/{meeting_id}.wav")
        self.recording_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Stats
        self.bytes_captured = 0
        self.is_capturing = False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start(self):
        """Start audio capture"""
        if self.is_capturing:
            return
        
        print(f"[Audio] Starting capture for meeting {self.meeting_id}")
        
        # Create virtual sink
        self._create_virtual_sink()
        
        # Connect to media server
        try:
            self.websocket = await websockets.connect(
                f"{self.media_server_url}?meeting_id={self.meeting_id}",
                ping_interval=10,
            )
            print("[Audio] Connected to media server")
        except Exception as e:
            print(f"[Audio] Failed to connect to media server: {e}")
            print("[Audio] Will record to file instead")
        
        # Start FFmpeg capture
        await self._start_ffmpeg()
        
        self.is_capturing = True
        print("[Audio] Capture started")

    async def stop(self):
        """Stop audio capture"""
        if not self.is_capturing:
            return
        
        print("[Audio] Stopping capture")
        
        self.is_capturing = False
        
        # Stop FFmpeg
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            try:
                self.ffmpeg_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ffmpeg_process.kill()
            self.ffmpeg_process = None
        
        # Close websocket
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        # Remove virtual sink
        self._remove_virtual_sink()
        
        print(f"[Audio] Stopped. Total bytes: {self.bytes_captured}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PULSEAUDIO SETUP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _create_virtual_sink(self):
        """Create PulseAudio virtual sink"""
        try:
            # Create null sink (virtual audio device)
            result = subprocess.run([
                'pactl',
                'load-module',
                'module-null-sink',
                f'sink_name={self.sink_name}',
                f'sink_properties=device.description="Vocaply_Meet_{self.meeting_id}"'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.sink_created = True
                print(f"[Audio] Created virtual sink: {self.sink_name}")
            else:
                print(f"[Audio] Failed to create sink: {result.stderr}")
                
        except FileNotFoundError:
            print("[Audio] PulseAudio not available, audio capture disabled")

    def _remove_virtual_sink(self):
        """Remove PulseAudio virtual sink"""
        if not self.sink_created:
            return
        
        try:
            subprocess.run([
                'pactl',
                'unload-module',
                'module-null-sink'
            ], check=False)
            
            print(f"[Audio] Removed virtual sink: {self.sink_name}")
            self.sink_created = False
            
        except Exception as e:
            print(f"[Audio] Failed to remove sink: {e}")

    def get_sink_monitor(self) -> str:
        """Get monitor source name for the sink"""
        return f"{self.sink_name}.monitor"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FFMPEG CAPTURE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _start_ffmpeg(self):
        """Start FFmpeg to capture audio from PulseAudio"""
        if not self.sink_created:
            print("[Audio] No sink created, skipping FFmpeg")
            return
        
        monitor_source = self.get_sink_monitor()
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg',
            '-f', 'pulse',                    # Input format
            '-i', monitor_source,             # Input source (sink monitor)
            '-acodec', 'pcm_s16le',           # Audio codec: 16-bit PCM
            '-ar', '16000',                   # Sample rate: 16kHz
            '-ac', '1',                       # Channels: mono
            '-f', 'wav',                      # Output format
            'pipe:1',                         # Output to stdout
        ]
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            print("[Audio] FFmpeg started")
            
            # Start reading output in background
            asyncio.create_task(self._read_ffmpeg_output())
            
        except FileNotFoundError:
            print("[Audio] FFmpeg not found. Install: apt install ffmpeg")
        except Exception as e:
            print(f"[Audio] Failed to start FFmpeg: {e}")

    async def _read_ffmpeg_output(self):
        """Read audio data from FFmpeg and stream it (non-blocking via executor)"""
        if not self.ffmpeg_process:
            return
        
        chunk_size = 4096
        loop = asyncio.get_event_loop()
        
        try:
            while self.is_capturing and self.ffmpeg_process:
                # Read in a thread so we don't block the asyncio event loop
                chunk = await loop.run_in_executor(
                    None,
                    self.ffmpeg_process.stdout.read,
                    chunk_size,
                )
                
                if not chunk:
                    break
                
                self.bytes_captured += len(chunk)
                
                # Stream to media server
                if self.websocket:
                    try:
                        await self.websocket.send(chunk)
                    except Exception as e:
                        print(f"[Audio] WebSocket send failed: {e}")
                        self._write_to_file(chunk)
                else:
                    self._write_to_file(chunk)
                
        except Exception as e:
            print(f"[Audio] FFmpeg read error: {e}")

    def _write_to_file(self, chunk: bytes):
        """Write audio chunk to file (fallback)"""
        with open(self.recording_path, 'ab') as f:
            f.write(chunk)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CHROME AUDIO ROUTING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def redirect_chrome_audio(self, chrome_pid: Optional[int] = None):
        """
        Redirect Chrome's audio to our virtual sink.
        
        This needs to be called after Chrome starts.
        """
        if not self.sink_created:
            return
        
        try:
            # Find Chrome audio streams
            result = subprocess.run(
                ['pactl', 'list', 'sink-inputs'],
                capture_output=True,
                text=True,
            )
            
            # Parse output to find Chrome streams
            # Format: Sink Input #N
            import re
            
            for match in re.finditer(r'Sink Input #(\d+)', result.stdout):
                sink_input_id = match.group(1)
                
                # Check if this is Chrome (look for "Chromium" in the output)
                if 'Chromium' in result.stdout or 'Chrome' in result.stdout:
                    # Move this stream to our sink
                    subprocess.run([
                        'pactl',
                        'move-sink-input',
                        sink_input_id,
                        self.sink_name
                    ], check=False)
                    
                    print(f"[Audio] Redirected Chrome stream {sink_input_id} to virtual sink")
            
        except Exception as e:
            print(f"[Audio] Failed to redirect Chrome audio: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stats(self) -> dict:
        """Get capture statistics"""
        return {
            'is_capturing': self.is_capturing,
            'bytes_captured': self.bytes_captured,
            'sink_created': self.sink_created,
            'streaming': self.websocket is not None,
            'recording_path': str(self.recording_path),
        }