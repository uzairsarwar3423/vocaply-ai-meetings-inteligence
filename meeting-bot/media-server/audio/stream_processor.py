"""
Stream Processor
Processes audio streams (convert PCM to WAV, MP3, etc.)
"""

import wave
import subprocess
from pathlib import Path
from typing import Optional


class StreamProcessor:
    """Processes audio streams after recording completes"""

    @staticmethod
    def pcm_to_wav(
        pcm_path: Path,
        wav_path: Path,
        sample_rate: int = 16000,
        channels: int = 1,
        bits_per_sample: int = 16,
    ) -> bool:
        """
        Convert raw PCM audio to WAV format.
        
        Args:
            pcm_path: Path to PCM file
            wav_path: Output WAV path
            sample_rate: Sample rate in Hz
            channels: Number of channels
            bits_per_sample: Bits per sample (8, 16, 24, 32)
        """
        try:
            with open(pcm_path, 'rb') as pcm_file:
                pcm_data = pcm_file.read()
            
            with wave.open(str(wav_path), 'wb') as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(bits_per_sample // 8)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm_data)
            
            print(f"[Processor] Converted {pcm_path} → {wav_path}")
            return True
            
        except Exception as e:
            print(f"[Processor] PCM to WAV failed: {e}")
            return False

    @staticmethod
    def wav_to_mp3(
        wav_path: Path,
        mp3_path: Path,
        bitrate: str = "128k",
    ) -> bool:
        """
        Convert WAV to MP3 using ffmpeg.
        
        Requires ffmpeg installed: apt install ffmpeg
        """
        try:
            cmd = [
                "ffmpeg",
                "-i", str(wav_path),
                "-codec:a", "libmp3lame",
                "-b:a", bitrate,
                "-y",  # Overwrite
                str(mp3_path),
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 min timeout
            )
            
            if result.returncode == 0:
                print(f"[Processor] Converted {wav_path} → {mp3_path}")
                return True
            else:
                print(f"[Processor] ffmpeg error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("[Processor] ffmpeg not found. Install: apt install ffmpeg")
            return False
        except Exception as e:
            print(f"[Processor] WAV to MP3 failed: {e}")
            return False

    @staticmethod
    def process_recording(
        pcm_path: Path,
        output_format: str = "wav",
        cleanup_pcm: bool = True,
    ) -> Optional[Path]:
        """
        Process a completed PCM recording.
        
        Args:
            pcm_path: Path to PCM file
            output_format: "wav" or "mp3"
            cleanup_pcm: Delete PCM file after conversion
        
        Returns:
            Path to output file, or None on failure
        """
        # Convert to WAV
        wav_path = pcm_path.with_suffix('.wav')
        
        if not StreamProcessor.pcm_to_wav(pcm_path, wav_path):
            return None
        
        output_path = wav_path
        
        # Convert to MP3 if requested
        if output_format == "mp3":
            mp3_path = wav_path.with_suffix('.mp3')
            
            if StreamProcessor.wav_to_mp3(wav_path, mp3_path):
                output_path = mp3_path
                # Cleanup WAV
                wav_path.unlink(missing_ok=True)
            else:
                # Keep WAV on MP3 conversion failure
                pass
        
        # Cleanup PCM
        if cleanup_pcm:
            pcm_path.unlink(missing_ok=True)
        
        return output_path