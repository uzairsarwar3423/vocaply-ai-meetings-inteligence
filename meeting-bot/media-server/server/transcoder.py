"""
Transcoder
Converts audio files using FFmpeg
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Optional

from config.media_config import settings


class Transcoder:
    """
    Transcodes audio files using FFmpeg.
    
    Supported conversions:
    - WAV → MP3
    - WAV → M4A (AAC)
    - WAV → OGG
    """

    def __init__(self):
        pass

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TRANSCODING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def transcode(
        self,
        input_path: Path,
        output_format: str = "mp3",
    ) -> Optional[Path]:
        """
        Transcode audio file.
        
        Args:
            input_path: Path to input WAV file
            output_format: Output format (mp3, m4a, ogg)
        
        Returns:
            Path to output file, or None on failure
        """
        if not input_path.exists():
            print(f"[Transcoder] Input file not found: {input_path}")
            return None
        
        # Build output path
        output_path = input_path.with_suffix(f".{output_format}")
        
        print(f"[Transcoder] Converting {input_path.name} → {output_format}")
        
        try:
            # Transcode based on format
            if output_format == "mp3":
                success = await self._to_mp3(input_path, output_path)
            elif output_format == "m4a":
                success = await self._to_m4a(input_path, output_path)
            elif output_format == "ogg":
                success = await self._to_ogg(input_path, output_path)
            else:
                print(f"[Transcoder] Unsupported format: {output_format}")
                return None
            
            if success:
                print(f"[Transcoder] Conversion complete: {output_path}")
                return output_path
            else:
                return None
                
        except Exception as e:
            print(f"[Transcoder] Conversion failed: {e}")
            return None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FORMAT-SPECIFIC CONVERSIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _to_mp3(self, input_path: Path, output_path: Path) -> bool:
        """Convert to MP3 using LAME codec"""
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-codec:a', 'libmp3lame',
            '-b:a', settings.MP3_BITRATE,
            '-q:a', str(settings.MP3_QUALITY),
            '-y',  # Overwrite
            str(output_path),
        ]
        
        return await self._run_ffmpeg(cmd)

    async def _to_m4a(self, input_path: Path, output_path: Path) -> bool:
        """Convert to M4A (AAC) for Apple compatibility"""
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-codec:a', 'aac',
            '-b:a', settings.MP3_BITRATE,
            '-y',
            str(output_path),
        ]
        
        return await self._run_ffmpeg(cmd)

    async def _to_ogg(self, input_path: Path, output_path: Path) -> bool:
        """Convert to OGG Vorbis"""
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-codec:a', 'libvorbis',
            '-q:a', '4',  # Quality (0-10)
            '-y',
            str(output_path),
        ]
        
        return await self._run_ffmpeg(cmd)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FFMPEG EXECUTION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _run_ffmpeg(self, cmd: list, timeout: int = 300) -> bool:
        """
        Run FFmpeg command asynchronously.
        
        Args:
            cmd: FFmpeg command list
            timeout: Timeout in seconds
        
        Returns:
            True on success, False on failure
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # Wait with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
            
            if process.returncode == 0:
                return True
            else:
                error = stderr.decode('utf-8')
                print(f"[Transcoder] FFmpeg error: {error}")
                return False
                
        except asyncio.TimeoutError:
            print(f"[Transcoder] FFmpeg timeout after {timeout}s")
            return False
        except FileNotFoundError:
            print("[Transcoder] FFmpeg not found. Install: apt install ffmpeg")
            return False
        except Exception as e:
            print(f"[Transcoder] FFmpeg execution error: {e}")
            return False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # VALIDATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def validate_audio(self, file_path: Path) -> bool:
        """
        Validate audio file with FFprobe.
        
        Returns:
            True if valid, False otherwise
        """
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(file_path),
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                duration = stdout.decode('utf-8').strip()
                return float(duration) > 0
            
            return False
            
        except Exception as e:
            print(f"[Transcoder] Validation error: {e}")
            return False

    async def get_audio_info(self, file_path: Path) -> dict:
        """
        Get audio file information using FFprobe.
        
        Returns:
            {duration, sample_rate, channels, codec, bitrate}
        """
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration,bit_rate:stream=codec_name,sample_rate,channels',
            '-of', 'json',
            str(file_path),
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                import json
                data = json.loads(stdout.decode('utf-8'))
                
                format_info = data.get('format', {})
                stream_info = data.get('streams', [{}])[0] if data.get('streams') else {}
                
                return {
                    'duration': float(format_info.get('duration', 0)),
                    'bitrate': int(format_info.get('bit_rate', 0)),
                    'codec': stream_info.get('codec_name', 'unknown'),
                    'sample_rate': int(stream_info.get('sample_rate', 0)),
                    'channels': int(stream_info.get('channels', 0)),
                }
            
            return {}
            
        except Exception as e:
            print(f"[Transcoder] Info extraction error: {e}")
            return {}