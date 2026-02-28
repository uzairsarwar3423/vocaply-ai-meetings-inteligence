
import asyncio
import os
import sys
from pathlib import Path

# Add the media-server directory to sys.path
sys.path.append(str(Path(__file__).parent))

from server.main import MediaServer
from config.media_config import settings
import websockets
import numpy as np

async def test_media_server_smoke():
    # Override settings for testing
    settings.B2_ENABLED = False
    settings.WEBHOOK_URL = "" # Disable webhook for smoke test
    settings.RECORDING_DIR = "/tmp/test_recordings"
    settings.TEMP_DIR = "/tmp/test_recordings/temp"
    
    # Create directories
    Path(settings.RECORDING_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)

    server = MediaServer()
    
    # Start server in a background task
    server_task = asyncio.create_task(server.start())
    
    # Give it a moment to start
    await asyncio.sleep(2)
    
    uri = f"ws://{settings.HOST}:{settings.PORT}/audio?meeting_id=test_meeting_123"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            
            # Send 1 second of dummy audio (16kHz, 16-bit, mono)
            # 16000 samples * 2 bytes/sample = 32000 bytes
            dummy_audio = np.zeros(16000, dtype=np.int16).tobytes()
            
            # Send in chunks
            chunk_size = 4096
            for i in range(0, len(dummy_audio), chunk_size):
                chunk = dummy_audio[i:i+chunk_size]
                await websocket.send(chunk)
                await asyncio.sleep(0.05)
            
            print("Sent audio data, closing connection...")
        
        # Wait for processing to complete
        await asyncio.sleep(5)
        
        # Check if WAV file was created (it might be deleted if KEEP_LOCAL_FILES is False)
        # In our case, it should have been transcoded to MP3 and then deleted
        print("Smoke test finished. Check logs above for processing status.")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
        await server.stop()

if __name__ == "__main__":
    asyncio.run(test_media_server_smoke())
