"""
Upload Service
Vocaply Platform - Day 6

Orchestrates complete upload flow with Redis state tracking.
Single upload: validate → presigned_url → B2 → confirm
Multipart:     validate → init → parts (parallel) → complete
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from app.services.storage.backblaze_service import BackblazeService
from app.services.storage.file_validator import FileValidator

UPLOAD_TTL     = 86400   # 24h Redis TTL
STATUS_PENDING  = "pending"
STATUS_UPLOADING = "uploading"
STATUS_DONE     = "completed"
STATUS_FAILED   = "failed"
STATUS_ABORTED  = "aborted"


class UploadService:
    """
    Manages full file upload lifecycle.
    Redis stores upload state for progress tracking and resumption.
    """

    def __init__(self, storage: BackblazeService, validator: FileValidator, redis=None):
        self.storage   = storage
        self.validator = validator
        self.redis     = redis

    # ============================================
    # SINGLE FILE UPLOAD  (< 100 MB)
    # ============================================

    async def request_presigned_url(
        self,
        company_id:   uuid.UUID,
        meeting_id:   uuid.UUID,
        user_id:      uuid.UUID,
        file_name:    str,
        file_size:    int,
        content_type: str,
    ) -> Dict[str, Any]:
        """Step 1 — validate metadata, return presigned PUT URL"""
        result = self.validator.validate_metadata(file_name, file_size, content_type)
        self.validator.assert_valid(result)

        s3_key    = self.storage.build_key(company_id, meeting_id, file_name)
        upload_id = str(uuid.uuid4())

        presigned = self.storage.generate_presigned_upload(
            s3_key       = s3_key,
            content_type = content_type,
            file_size    = file_size,
            metadata     = {
                "company_id": str(company_id),
                "meeting_id": str(meeting_id),
                "user_id":    str(user_id),
                "upload_id":  upload_id,
            },
        )

        await self._set_state(upload_id, {
            "upload_id":    upload_id,
            "type":         "single",
            "company_id":   str(company_id),
            "meeting_id":   str(meeting_id),
            "user_id":      str(user_id),
            "s3_key":       s3_key,
            "file_name":    file_name,
            "file_size":    file_size,
            "content_type": content_type,
            "status":       STATUS_PENDING,
            "created_at":   datetime.utcnow().isoformat(),
        })

        return {
            "upload_id":    upload_id,
            "upload_url":   presigned["upload_url"],
            "method":       "PUT",
            "s3_key":       s3_key,
            "cdn_url":      presigned["cdn_url"],
            "expires_at":   presigned["expires_at"],
            "expires_in":   presigned["expires_in"],
            "file_name":    file_name,
            "file_size":    file_size,
            "content_type": content_type,
        }

    async def complete_upload(
        self,
        upload_id:  str,
        company_id: uuid.UUID,
        etag:       Optional[str] = None,
    ) -> Dict[str, Any]:
        """Step 2 — called after browser finishes PUT to B2"""
        state = await self._get_state(upload_id)
        if not state:
            raise HTTPException(404, f"Upload session '{upload_id}' not found or expired")

        self._check_ownership(state, company_id)

        if state.get("status") == STATUS_DONE:
            return self._done_response(state)

        # Verify file actually landed in B2
        meta = self.storage.get_metadata(state["s3_key"])
        if not meta:
            raise HTTPException(422, "File not found in storage — upload may have failed")

        await self._set_state(upload_id, {
            **state,
            "status":       STATUS_DONE,
            "etag":         etag or meta.get("etag"),
            "actual_size":  meta.get("size"),
            "completed_at": datetime.utcnow().isoformat(),
        })

        return {
            "upload_id":  upload_id,
            "s3_key":     state["s3_key"],
            "cdn_url":    self.storage.get_cdn_url(state["s3_key"]),
            "file_name":  state["file_name"],
            "file_size":  meta.get("size") or state["file_size"],
            "meeting_id": state["meeting_id"],
            "status":     STATUS_DONE,
        }

    # ============================================
    # MULTIPART UPLOAD  (> 100 MB)
    # ============================================

    async def init_multipart(
        self,
        company_id:   uuid.UUID,
        meeting_id:   uuid.UUID,
        user_id:      uuid.UUID,
        file_name:    str,
        file_size:    int,
        content_type: str,
    ) -> Dict[str, Any]:
        """Init multipart — returns upload_id + pre-signed URLs for all parts"""
        result = self.validator.validate_metadata(file_name, file_size, content_type)
        self.validator.assert_valid(result)

        if not result.use_multipart:
            raise HTTPException(422, "File is < 100 MB. Use /presigned-url instead.")

        s3_key    = self.storage.build_key(company_id, meeting_id, file_name)
        upload_id = str(uuid.uuid4())

        mp = self.storage.init_multipart(
            s3_key       = s3_key,
            content_type = content_type,
            metadata     = {"company_id": str(company_id), "meeting_id": str(meeting_id)},
        )

        part_size   = mp["part_size"]
        total_parts = -(-file_size // part_size)   # ceiling division
        b2_id       = mp["upload_id"]

        part_urls = [
            {
                "part_number": i,
                "upload_url":  self.storage.generate_part_url(s3_key, b2_id, i),
            }
            for i in range(1, total_parts + 1)
        ]

        await self._set_state(upload_id, {
            "upload_id":      upload_id,
            "type":           "multipart",
            "b2_upload_id":   b2_id,
            "company_id":     str(company_id),
            "meeting_id":     str(meeting_id),
            "user_id":        str(user_id),
            "s3_key":         s3_key,
            "file_name":      file_name,
            "file_size":      file_size,
            "content_type":   content_type,
            "total_parts":    total_parts,
            "part_size":      part_size,
            "uploaded_parts": [],
            "status":         STATUS_PENDING,
            "created_at":     datetime.utcnow().isoformat(),
        })

        return {
            "upload_id":   upload_id,
            "s3_key":      s3_key,
            "total_parts": total_parts,
            "part_size":   part_size,
            "file_size":   file_size,
            "part_urls":   part_urls,
        }

    async def record_part(
        self,
        upload_id:   str,
        company_id:  uuid.UUID,
        part_number: int,
        etag:        str,
    ) -> Dict[str, Any]:
        """Record one uploaded part (idempotent)"""
        state = await self._require_state(upload_id, company_id)

        parts = [p for p in state.get("uploaded_parts", []) if p["PartNumber"] != part_number]
        parts.append({"PartNumber": part_number, "ETag": etag})

        await self._set_state(upload_id, {**state, "uploaded_parts": parts, "status": STATUS_UPLOADING})

        total = state["total_parts"]
        return {
            "upload_id":      upload_id,
            "part_number":    part_number,
            "parts_uploaded": len(parts),
            "total_parts":    total,
            "progress_pct":   round(len(parts) / total * 100, 1),
        }

    async def complete_multipart(self, upload_id: str, company_id: uuid.UUID) -> Dict[str, Any]:
        """Assemble all parts into final B2 object"""
        state = await self._require_state(upload_id, company_id)

        parts = state.get("uploaded_parts", [])
        total = state.get("total_parts", 0)

        if len(parts) < total:
            raise HTTPException(422, f"Only {len(parts)}/{total} parts uploaded")

        result = self.storage.complete_multipart(
            s3_key    = state["s3_key"],
            upload_id = state["b2_upload_id"],
            parts     = parts,
        )

        await self._set_state(upload_id, {
            **state,
            "status":       STATUS_DONE,
            "cdn_url":      result["cdn_url"],
            "completed_at": datetime.utcnow().isoformat(),
        })

        return {
            "upload_id":  upload_id,
            "s3_key":     result["s3_key"],
            "cdn_url":    result["cdn_url"],
            "file_name":  state["file_name"],
            "file_size":  state["file_size"],
            "meeting_id": state["meeting_id"],
            "status":     STATUS_DONE,
        }

    # ============================================
    # STATUS & RESUMPTION
    # ============================================

    async def get_status(self, upload_id: str, company_id: uuid.UUID) -> Dict[str, Any]:
        state = await self._require_state(upload_id, company_id)
        resp  = {
            "upload_id":  upload_id,
            "status":     state.get("status"),
            "file_name":  state.get("file_name"),
            "file_size":  state.get("file_size"),
            "type":       state.get("type"),
            "created_at": state.get("created_at"),
        }
        if state.get("type") == "multipart":
            done  = len(state.get("uploaded_parts", []))
            total = state.get("total_parts", 1)
            done_nums = {p["PartNumber"] for p in state.get("uploaded_parts", [])}
            resp.update({
                "parts_uploaded": done,
                "total_parts":    total,
                "progress_pct":   round(done / total * 100, 1),
                "missing_parts":  [i for i in range(1, total + 1) if i not in done_nums],
            })
        return resp

    async def abort(self, upload_id: str, company_id: uuid.UUID) -> None:
        state = await self._get_state(upload_id)
        if not state:
            return
        self._check_ownership(state, company_id)
        if state.get("type") == "multipart" and state.get("b2_upload_id"):
            self.storage.abort_multipart(state["s3_key"], state["b2_upload_id"])
        await self._set_state(upload_id, {**state, "status": STATUS_ABORTED,
                                           "aborted_at": datetime.utcnow().isoformat()})

    async def delete_file(self, s3_key: str, company_id: uuid.UUID) -> Dict[str, Any]:
        if str(company_id) not in s3_key:
            raise HTTPException(403, "Forbidden — file does not belong to your company")
        deleted = self.storage.delete(s3_key)
        return {"deleted": deleted, "s3_key": s3_key}

    # ============================================
    # REDIS HELPERS
    # ============================================

    async def _set_state(self, upload_id: str, data: Dict) -> None:
        if self.redis:
            await self.redis.setex(f"upload:{upload_id}", UPLOAD_TTL, json.dumps(data, default=str))

    async def _get_state(self, upload_id: str) -> Optional[Dict]:
        if not self.redis:
            return None
        raw = await self.redis.get(f"upload:{upload_id}")
        return json.loads(raw) if raw else None

    async def _require_state(self, upload_id: str, company_id: uuid.UUID) -> Dict:
        state = await self._get_state(upload_id)
        if not state:
            raise HTTPException(404, f"Upload session '{upload_id}' not found or expired")
        self._check_ownership(state, company_id)
        return state

    def _check_ownership(self, state: Dict, company_id: uuid.UUID) -> None:
        if str(state.get("company_id")) != str(company_id):
            raise HTTPException(403, "Forbidden")

    def _done_response(self, state: Dict) -> Dict[str, Any]:
        return {
            "upload_id":  state["upload_id"],
            "s3_key":     state["s3_key"],
            "cdn_url":    self.storage.get_cdn_url(state["s3_key"]),
            "file_name":  state["file_name"],
            "file_size":  state["file_size"],
            "meeting_id": state["meeting_id"],
            "status":     STATUS_DONE,
        }