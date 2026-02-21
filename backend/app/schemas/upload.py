"""Upload Schemas — Vocaply Day 6"""

import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


# ── Requests ──────────────────────────────────────────────────────────

class PresignedUrlRequest(BaseModel):
    meeting_id:   uuid.UUID = Field(...)
    file_name:    str       = Field(..., min_length=1, max_length=255)
    file_size:    int       = Field(..., gt=0, description="Bytes")
    content_type: str       = Field(...)

    @validator("content_type")
    def norm(cls, v): return v.lower().strip()


class MultipartInitRequest(BaseModel):
    meeting_id:   uuid.UUID = Field(...)
    file_name:    str       = Field(..., min_length=1, max_length=255)
    file_size:    int       = Field(..., gt=100 * 1024 * 1024, description="> 100 MB required")
    content_type: str       = Field(...)


class PartUploadRequest(BaseModel):
    upload_id:   str = Field(...)
    part_number: int = Field(..., ge=1, le=10000)
    etag:        str = Field(...)


class MultipartCompleteRequest(BaseModel):
    upload_id: str = Field(...)


class ConfirmUploadRequest(BaseModel):
    upload_id: str           = Field(...)
    etag:      Optional[str] = None


# ── Responses ─────────────────────────────────────────────────────────

class PresignedUrlResponse(BaseModel):
    upload_id:    str
    upload_url:   str
    method:       str = "PUT"
    s3_key:       str
    cdn_url:      str
    expires_at:   str
    expires_in:   int
    file_name:    str
    file_size:    int
    content_type: str


class MultipartInitResponse(BaseModel):
    upload_id:   str
    s3_key:      str
    total_parts: int
    part_size:   int
    file_size:   int
    part_urls:   List[Dict[str, Any]]


class PartUploadResponse(BaseModel):
    upload_id:      str
    part_number:    int
    parts_uploaded: int
    total_parts:    int
    progress_pct:   float


class UploadCompleteResponse(BaseModel):
    upload_id:  str
    s3_key:     str
    cdn_url:    str
    file_name:  str
    file_size:  int
    meeting_id: str
    status:     str


class UploadStatusResponse(BaseModel):
    upload_id:     str
    status:        str
    file_name:     Optional[str]
    file_size:     Optional[int]
    type:          Optional[str]
    created_at:    Optional[str]
    parts_uploaded: Optional[int] = None
    total_parts:    Optional[int] = None
    progress_pct:   Optional[float] = None
    missing_parts:  Optional[List[int]] = None


class DeleteResponse(BaseModel):
    deleted: bool
    s3_key:  str