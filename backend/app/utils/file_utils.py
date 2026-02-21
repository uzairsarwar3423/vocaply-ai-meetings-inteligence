"""File Utilities — Vocaply Day 6"""

import hashlib
import os
import re
import uuid
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional


def format_bytes(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    filename = unicodedata.normalize("NFKD", filename)
    filename = os.path.basename(filename)
    filename = re.sub(r"[\x00-\x1f\x7f]", "", filename)
    filename = re.sub(r"[^\w\s\-\.]", "", filename).strip()
    filename = re.sub(r"\.{2,}", ".", filename)
    if len(filename) > max_length:
        stem, ext = os.path.splitext(filename)
        filename  = stem[: max_length - len(ext)] + ext
    return filename or "upload"


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def extension_to_mime(ext: str) -> str:
    mapping = {
        ".mp3": "audio/mpeg", ".wav": "audio/wav",
        ".m4a": "audio/m4a",  ".ogg": "audio/ogg",
        ".aac": "audio/aac",  ".flac": "audio/flac",
        ".mp4": "video/mp4",  ".webm": "video/webm",
        ".mov": "video/quicktime", ".avi": "video/x-msvideo",
    }
    return mapping.get(ext.lower(), "application/octet-stream")


def calc_parts(file_size: int, part_size: int = 50 * 1024 * 1024) -> Tuple[int, int]:
    """Returns (total_parts, part_size_bytes)"""
    return -(-file_size // part_size), part_size


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_s3_key(
    company_id: uuid.UUID,
    meeting_id: uuid.UUID,
    filename:   str,
    prefix:     str = "recordings",
) -> str:
    ext  = get_extension(filename) or ".bin"
    date = datetime.utcnow().strftime("%Y/%m/%d")
    uid  = uuid.uuid4().hex[:8]
    return f"{prefix}/{company_id}/{date}/{meeting_id}_{uid}{ext}"


def is_audio(filename: str) -> bool:
    return get_extension(filename) in {".mp3", ".wav", ".m4a", ".ogg", ".aac", ".flac"}


def is_video(filename: str) -> bool:
    return get_extension(filename) in {".mp4", ".webm", ".mov", ".avi", ".mpeg"}