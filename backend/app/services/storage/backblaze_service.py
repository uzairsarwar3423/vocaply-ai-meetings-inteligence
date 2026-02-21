"""
Backblaze B2 Service
Vocaply Platform - Day 6

S3-compatible API wrapper for Backblaze B2.
Handles presigned URLs, multipart uploads, CDN URL generation.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import settings

PART_SIZE_BYTES   = 50 * 1024 * 1024   # 50 MB per part
MIN_PART_SIZE     = 5  * 1024 * 1024   # 5 MB S3 minimum
PRESIGNED_URL_TTL = 3600               # 1 hour


class BackblazeService:
    """
    Backblaze B2 via S3-compatible API (boto3).
    Endpoint: https://s3.{region}.backblazeb2.com
    """

    def __init__(self):
        self._client  = None
        self._bucket  = settings.BACKBLAZE_BUCKET_NAME
        self._region  = settings.BACKBLAZE_REGION
        self._endpoint = f"https://s3.{settings.BACKBLAZE_REGION}.backblazeb2.com"

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url        = self._endpoint,
                aws_access_key_id   = settings.BACKBLAZE_KEY_ID,
                aws_secret_access_key = settings.BACKBLAZE_APPLICATION_KEY,
                region_name         = self._region,
                config=Config(
                    signature_version    = "s3v4",
                    retries              = {"max_attempts": 3, "mode": "adaptive"},
                    max_pool_connections = 25,
                ),
            )
        return self._client

    # ============================================
    # KEY & URL HELPERS
    # ============================================

    def build_key(
        self,
        company_id: uuid.UUID,
        meeting_id: uuid.UUID,
        filename:   str,
        prefix:     str = "recordings",
    ) -> str:
        """Build structured storage key: recordings/{company}/{date}/{meeting}_{uid}.ext"""
        ext       = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
        date_path = datetime.utcnow().strftime("%Y/%m/%d")
        uid       = uuid.uuid4().hex[:8]
        return f"{prefix}/{company_id}/{date_path}/{meeting_id}_{uid}.{ext}"

    def get_cdn_url(self, s3_key: str) -> str:
        """Return CDN-fronted URL (Cloudflare in front of B2)"""
        base = settings.CDN_URL.rstrip("/") if settings.CDN_URL else self._endpoint
        return f"{base}/{s3_key}"

    def get_public_url(self, s3_key: str) -> str:
        """Direct B2 URL (no CDN)"""
        return f"{self._endpoint}/{self._bucket}/{s3_key}"

    # ============================================
    # PRESIGNED URLS — Single Upload
    # ============================================

    def generate_presigned_upload(
        self,
        s3_key:       str,
        content_type: str,
        file_size:    int,
        metadata:     Optional[Dict[str, str]] = None,
        expires_in:   int = PRESIGNED_URL_TTL,
    ) -> Dict[str, Any]:
        """
        Generate presigned PUT URL for direct browser → B2 upload.
        File bytes never pass through our servers.
        """
        try:
            params: Dict[str, Any] = {
                "Bucket":      self._bucket,
                "Key":         s3_key,
                "ContentType": content_type,
            }
            if metadata:
                params["Metadata"] = {k: str(v) for k, v in metadata.items()}

            url = self.client.generate_presigned_url(
                "put_object",
                Params      = params,
                ExpiresIn   = expires_in,
                HttpMethod  = "PUT",
            )

            expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()

            return {
                "upload_url": url,
                "method":     "PUT",
                "s3_key":     s3_key,
                "cdn_url":    self.get_cdn_url(s3_key),
                "expires_at": expires_at,
                "expires_in": expires_in,
            }
        except ClientError as e:
            raise RuntimeError(f"Failed to generate presigned URL: {e}") from e

    def generate_presigned_download(
        self,
        s3_key:     str,
        expires_in: int = 3600,
        filename:   Optional[str] = None,
    ) -> str:
        """Generate time-limited download URL"""
        params: Dict[str, Any] = {"Bucket": self._bucket, "Key": s3_key}
        if filename:
            params["ResponseContentDisposition"] = f'attachment; filename="{filename}"'
        return self.client.generate_presigned_url(
            "get_object", Params=params, ExpiresIn=expires_in
        )

    # ============================================
    # MULTIPART UPLOAD — Large Files
    # ============================================

    def init_multipart(
        self,
        s3_key:       str,
        content_type: str,
        metadata:     Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Initiate a multipart upload, returns B2 upload_id"""
        try:
            kwargs: Dict[str, Any] = {
                "Bucket":      self._bucket,
                "Key":         s3_key,
                "ContentType": content_type,
            }
            if metadata:
                kwargs["Metadata"] = {k: str(v) for k, v in metadata.items()}

            resp = self.client.create_multipart_upload(**kwargs)
            return {
                "upload_id":     resp["UploadId"],
                "s3_key":        s3_key,
                "part_size":     PART_SIZE_BYTES,
                "min_part_size": MIN_PART_SIZE,
            }
        except ClientError as e:
            raise RuntimeError(f"Failed to init multipart upload: {e}") from e

    def generate_part_url(
        self,
        s3_key:      str,
        upload_id:   str,
        part_number: int,
        expires_in:  int = PRESIGNED_URL_TTL,
    ) -> str:
        """Presigned URL for a single part upload"""
        if not 1 <= part_number <= 10000:
            raise ValueError(f"Part number must be 1–10,000, got {part_number}")
        try:
            return self.client.generate_presigned_url(
                "upload_part",
                Params={
                    "Bucket":     self._bucket,
                    "Key":        s3_key,
                    "UploadId":   upload_id,
                    "PartNumber": part_number,
                },
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            raise RuntimeError(f"Failed to generate part URL: {e}") from e

    def complete_multipart(
        self,
        s3_key:    str,
        upload_id: str,
        parts:     List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Assemble all parts into a final object. parts = [{PartNumber, ETag}]"""
        try:
            sorted_parts = sorted(parts, key=lambda p: p["PartNumber"])
            resp = self.client.complete_multipart_upload(
                Bucket    = self._bucket,
                Key       = s3_key,
                UploadId  = upload_id,
                MultipartUpload={"Parts": sorted_parts},
            )
            cdn_url = self.get_cdn_url(s3_key)
            return {
                "s3_key":   s3_key,
                "cdn_url":  cdn_url,
                "etag":     resp.get("ETag", "").strip('"'),
                "location": resp.get("Location", cdn_url),
            }
        except ClientError as e:
            self._abort_multipart(s3_key, upload_id)
            raise RuntimeError(f"Failed to complete multipart upload: {e}") from e

    def abort_multipart(self, s3_key: str, upload_id: str) -> None:
        self._abort_multipart(s3_key, upload_id)

    def _abort_multipart(self, s3_key: str, upload_id: str) -> None:
        try:
            self.client.abort_multipart_upload(
                Bucket=self._bucket, Key=s3_key, UploadId=upload_id
            )
        except ClientError:
            pass  # Best-effort cleanup

    def list_parts(self, s3_key: str, upload_id: str) -> List[Dict[str, Any]]:
        """List already-uploaded parts (supports resumption)"""
        try:
            resp = self.client.list_parts(
                Bucket=self._bucket, Key=s3_key, UploadId=upload_id
            )
            return [
                {"PartNumber": p["PartNumber"], "ETag": p["ETag"], "Size": p["Size"]}
                for p in resp.get("Parts", [])
            ]
        except ClientError as e:
            raise RuntimeError(f"Failed to list parts: {e}") from e

    # ============================================
    # FILE OPERATIONS
    # ============================================

    def get_metadata(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """HEAD request — get file metadata without downloading"""
        try:
            resp = self.client.head_object(Bucket=self._bucket, Key=s3_key)
            return {
                "size":         resp.get("ContentLength"),
                "content_type": resp.get("ContentType"),
                "modified":     resp.get("LastModified"),
                "etag":         resp.get("ETag", "").strip('"'),
                "metadata":     resp.get("Metadata", {}),
            }
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
                return None
            raise

    def exists(self, s3_key: str) -> bool:
        return self.get_metadata(s3_key) is not None

    def delete(self, s3_key: str) -> bool:
        try:
            self.client.delete_object(Bucket=self._bucket, Key=s3_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return False
            raise RuntimeError(f"Failed to delete: {e}") from e

    def delete_many(self, s3_keys: List[str]) -> Dict[str, Any]:
        try:
            resp = self.client.delete_objects(
                Bucket=self._bucket,
                Delete={"Objects": [{"Key": k} for k in s3_keys], "Quiet": False},
            )
            return {
                "deleted": [d["Key"] for d in resp.get("Deleted", [])],
                "errors":  resp.get("Errors", []),
            }
        except ClientError as e:
            raise RuntimeError(f"Batch delete failed: {e}") from e

    def copy(self, source_key: str, dest_key: str) -> Dict[str, Any]:
        try:
            self.client.copy_object(
                Bucket      = self._bucket,
                CopySource  = {"Bucket": self._bucket, "Key": source_key},
                Key         = dest_key,
            )
            return {"source": source_key, "dest": dest_key, "cdn_url": self.get_cdn_url(dest_key)}
        except ClientError as e:
            raise RuntimeError(f"Copy failed: {e}") from e