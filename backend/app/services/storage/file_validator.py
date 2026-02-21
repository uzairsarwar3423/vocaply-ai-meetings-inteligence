"""
File Validator
Vocaply Platform - Day 6

Validates: size, MIME (magic bytes), ClamAV virus scan.
"""

import hashlib
import os
import socket
import struct
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from fastapi import HTTPException, UploadFile, status


# ============================================
# CONSTANTS
# ============================================

MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024   # 500 MB
MULTIPART_THRESHOLD = 100 * 1024 * 1024   # 100 MB - use multipart above

CLAMD_HOST    = os.getenv("CLAMD_HOST", "localhost")
CLAMD_PORT    = int(os.getenv("CLAMD_PORT", "3310"))
CLAMD_TIMEOUT = 30

ALLOWED_MIME_TYPES = {
    "audio/mpeg":      {"extensions": [".mp3"],          "label": "MP3"},
    "audio/mp3":       {"extensions": [".mp3"],          "label": "MP3"},
    "audio/wav":       {"extensions": [".wav"],          "label": "WAV"},
    "audio/x-wav":     {"extensions": [".wav"],          "label": "WAV"},
    "audio/m4a":       {"extensions": [".m4a"],          "label": "M4A"},
    "audio/x-m4a":     {"extensions": [".m4a"],          "label": "M4A"},
    "audio/ogg":       {"extensions": [".ogg"],          "label": "OGG"},
    "audio/webm":      {"extensions": [".webm"],         "label": "WebM"},
    "audio/aac":       {"extensions": [".aac"],          "label": "AAC"},
    "audio/flac":      {"extensions": [".flac"],         "label": "FLAC"},
    "video/mp4":       {"extensions": [".mp4"],          "label": "MP4"},
    "video/webm":      {"extensions": [".webm"],         "label": "WebM Video"},
    "video/mpeg":      {"extensions": [".mpeg", ".mpg"], "label": "MPEG"},
    "video/quicktime": {"extensions": [".mov"],          "label": "MOV"},
    "video/x-msvideo": {"extensions": [".avi"],          "label": "AVI"},
}

MAGIC_SIGNATURES = [
    (b"ID3",              "audio/mpeg"),
    (b"\xff\xfb",         "audio/mpeg"),
    (b"\xff\xf3",         "audio/mpeg"),
    (b"\xff\xf2",         "audio/mpeg"),
    (b"RIFF",             "audio/wav"),
    (b"OggS",             "audio/ogg"),
    (b"fLaC",             "audio/flac"),
    (b"\x1aE\xdf\xa3",    "video/webm"),
    (b"\x00\x00\x00\x20ftyp", "video/mp4"),
    (b"\x00\x00\x00\x18ftyp", "video/mp4"),
    (b"\x00\x00\x00\x1cftyp", "video/mp4"),
]

EXT_TO_MIME = {
    ".mp3": "audio/mpeg",   ".wav": "audio/wav",
    ".m4a": "audio/m4a",    ".ogg": "audio/ogg",
    ".aac": "audio/aac",    ".flac": "audio/flac",
    ".mp4": "video/mp4",    ".webm": "video/webm",
    ".mov": "video/quicktime", ".avi": "video/x-msvideo",
    ".mpeg": "video/mpeg",  ".mpg": "video/mpeg",
}

MIME_NORMALIZATIONS = {
    "audio/x-mpeg": "audio/mpeg",
    "audio/x-mp3":  "audio/mpeg",
    "audio/x-wav":  "audio/wav",
    "audio/x-m4a":  "audio/m4a",
    "video/x-mp4":  "video/mp4",
}


# ============================================
# RESULT
# ============================================

@dataclass
class FileValidationResult:
    is_valid:      bool
    file_size:     int
    mime_type:     str
    extension:     str
    file_name:     str
    sha256_hash:   str = ""
    error_message: Optional[str] = None
    use_multipart: bool = False
    virus_scanned: bool = False
    virus_found:   bool = False


# ============================================
# VALIDATOR CLASS
# ============================================

class FileValidator:

    def __init__(
        self,
        max_size_bytes: int = MAX_FILE_SIZE_BYTES,
        virus_scan:     bool = True,
        allowed_types:  dict = None,
    ):
        self.max_size_bytes = max_size_bytes
        self.virus_scan     = virus_scan
        self.allowed_types  = allowed_types or ALLOWED_MIME_TYPES

    # ─── Full validation (has file content) ──────
    async def validate(self, file: UploadFile) -> FileValidationResult:
        content = await file.read()
        await file.seek(0)

        file_name = self._sanitize(file.filename or "upload")
        extension = Path(file_name).suffix.lower()
        file_size = len(content)

        if file_size == 0:
            return self._fail(file_name, extension, 0, "File is empty")

        if file_size > self.max_size_bytes:
            return self._fail(file_name, extension, file_size,
                f"File is {file_size / 1e6:.1f} MB — max is {self.max_size_bytes / 1e6:.0f} MB")

        mime = self._detect_mime(content, file.content_type, extension)
        if mime not in self.allowed_types:
            labels = list(dict.fromkeys(v["label"] for v in self.allowed_types.values()))
            return self._fail(file_name, extension, file_size,
                f"'{mime}' not allowed. Supported: {', '.join(labels)}")

        sha256 = hashlib.sha256(content).hexdigest()

        virus_scanned = virus_found = False
        if self.virus_scan:
            virus_scanned, virus_found = self._clamav_scan(content)
            if virus_found:
                return self._fail(file_name, extension, file_size,
                    "File failed virus scan and was rejected")

        return FileValidationResult(
            is_valid=True, file_size=file_size, mime_type=mime,
            extension=extension or self._mime_to_ext(mime),
            file_name=file_name, sha256_hash=sha256,
            use_multipart=file_size > MULTIPART_THRESHOLD,
            virus_scanned=virus_scanned, virus_found=virus_found,
        )

    # ─── Metadata-only validation (presigned URL flow) ─
    def validate_metadata(self, file_name: str, file_size: int, content_type: str) -> FileValidationResult:
        name = self._sanitize(file_name)
        ext  = Path(name).suffix.lower()

        if file_size <= 0:
            return self._fail(name, ext, file_size, "Invalid file size")
        if file_size > self.max_size_bytes:
            return self._fail(name, ext, file_size,
                f"File exceeds {self.max_size_bytes / 1e6:.0f} MB limit")

        mime = self._normalize_mime(content_type)
        if mime not in self.allowed_types:
            return self._fail(name, ext, file_size,
                f"'{content_type}' is not a supported file type")

        return FileValidationResult(
            is_valid=True, file_size=file_size, mime_type=mime,
            extension=ext or self._mime_to_ext(mime), file_name=name,
            use_multipart=file_size > MULTIPART_THRESHOLD,
        )

    def assert_valid(self, result: FileValidationResult) -> None:
        if not result.is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.error_message or "Invalid file",
            )

    # ─── ClamAV Virus Scan ────────────────────────
    def _clamav_scan(self, content: bytes) -> Tuple[bool, bool]:
        """
        Stream bytes to ClamAV daemon via INSTREAM protocol.
        Returns (scanned, virus_found). Falls back gracefully if clamd unavailable.
        """
        try:
            with socket.create_connection((CLAMD_HOST, CLAMD_PORT), timeout=CLAMD_TIMEOUT) as sock:
                sock.sendall(b"zINSTREAM\0")
                chunk_size = 8192
                for i in range(0, len(content), chunk_size):
                    chunk = content[i: i + chunk_size]
                    sock.sendall(struct.pack("!L", len(chunk)) + chunk)
                sock.sendall(struct.pack("!L", 0))  # Terminator

                response = b""
                while chunk := sock.recv(1024):
                    response += chunk

            result      = response.decode("utf-8", errors="ignore").strip()
            virus_found = "FOUND" in result and "OK" not in result
            return True, virus_found
        except (socket.error, ConnectionRefusedError, TimeoutError, OSError):
            # ClamAV not reachable — log and continue (non-blocking)
            return False, False

    # ─── MIME Detection ───────────────────────────
    def _detect_mime(self, content: bytes, declared: Optional[str], ext: str) -> str:
        header = content[:16]
        for magic, mime in MAGIC_SIGNATURES:
            if header.startswith(magic):
                return mime
        # MP4 ftyp box sometimes appears at offset 4
        if len(content) >= 8 and content[4:8] == b"ftyp":
            return "video/mp4"
        if declared:
            norm = self._normalize_mime(declared)
            if norm in self.allowed_types:
                return norm
        return EXT_TO_MIME.get(ext, declared or "application/octet-stream")

    def _normalize_mime(self, mime: str) -> str:
        cleaned = mime.lower().strip().split(";")[0].strip()
        return MIME_NORMALIZATIONS.get(cleaned, cleaned)

    def _mime_to_ext(self, mime: str) -> str:
        exts = self.allowed_types.get(mime, {}).get("extensions", [])
        return exts[0] if exts else ".bin"

    def _sanitize(self, filename: str) -> str:
        name = os.path.basename(filename)
        name = re.sub(r"[\x00-\x1f\x7f]", "", name)
        name = re.sub(r"[^\w\s\-\.]", "", name).strip()
        name = re.sub(r"\.{2,}", ".", name)
        return name or "upload"