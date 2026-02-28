"""
Storage Uploader
Uploads recordings to Backblaze B2
"""

import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime
import uuid

import boto3
from botocore.exceptions import ClientError

from config.media_config import settings


class StorageUploader:
    """
    Uploads recordings to Backblaze B2 (S3-compatible).
    
    Upload path format:
    recordings/{company_id}/{YYYY/MM/DD}/{meeting_id}.mp3
    """

    def __init__(self):
        self.s3_client = None
        
        if settings.B2_ENABLED and settings.B2_KEY_ID and settings.B2_APP_KEY:
            self._init_client()

    def _init_client(self):
        """Initialize S3 client for Backblaze"""
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=f"https://s3.{settings.B2_REGION}.backblazeb2.com",
                aws_access_key_id=settings.B2_KEY_ID,
                aws_secret_access_key=settings.B2_APP_KEY,
            )
            
            print("[StorageUploader] B2 client initialized")
            
        except Exception as e:
            print(f"[StorageUploader] Failed to initialize B2 client: {e}")
            self.s3_client = None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # UPLOAD
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def upload(
        self,
        file_path: Path,
        meeting_id: str,
        company_id: str = "default",
    ) -> Optional[str]:
        """
        Upload file to Backblaze B2.
        
        Args:
            file_path: Local file path
            meeting_id: Meeting identifier
            company_id: Company identifier
        
        Returns:
            Public URL of uploaded file, or None on failure
        """
        if not self.s3_client:
            print("[StorageUploader] B2 client not initialized, skipping upload")
            return None
        
        if not file_path.exists():
            print(f"[StorageUploader] File not found: {file_path}")
            return None
        
        # Build S3 key
        s3_key = self._build_s3_key(meeting_id, company_id, file_path.suffix)
        
        print(f"[StorageUploader] Uploading {file_path.name} to s3://{settings.B2_BUCKET}/{s3_key}")
        
        try:
            # Upload file
            await self._upload_file(file_path, s3_key)
            
            # Build public URL
            url = self._build_public_url(s3_key)
            
            print(f"[StorageUploader] Upload complete: {url}")
            
            return url
            
        except Exception as e:
            print(f"[StorageUploader] Upload failed: {e}")
            return None

    async def _upload_file(self, file_path: Path, s3_key: str):
        """Upload file to S3"""
        # Determine content type
        content_type = self._get_content_type(file_path.suffix)
        
        # Upload in separate thread (boto3 is sync)
        loop = asyncio.get_event_loop()
        
        await loop.run_in_executor(
            None,
            lambda: self.s3_client.upload_file(
                str(file_path),
                settings.B2_BUCKET,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': {
                        'uploaded_at': datetime.utcnow().isoformat(),
                    },
                },
            )
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DELETE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def delete(self, s3_key: str) -> bool:
        """Delete file from B2"""
        if not self.s3_client:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.delete_object(
                    Bucket=settings.B2_BUCKET,
                    Key=s3_key,
                )
            )
            
            print(f"[StorageUploader] Deleted: {s3_key}")
            return True
            
        except ClientError as e:
            print(f"[StorageUploader] Delete failed: {e}")
            return False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HELPERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _build_s3_key(self, meeting_id: str, company_id: str, extension: str) -> str:
        """
        Build S3 object key.
        
        Format: recordings/{company_id}/{YYYY/MM/DD}/{meeting_id}.ext
        """
        now = datetime.utcnow()
        date_path = now.strftime("%Y/%m/%d")
        
        return f"recordings/{company_id}/{date_path}/{meeting_id}{extension}"

    def _build_public_url(self, s3_key: str) -> str:
        """Build public URL for S3 object"""
        # Backblaze B2 public URL format
        return f"https://{settings.B2_BUCKET}.s3.{settings.B2_REGION}.backblazeb2.com/{s3_key}"

    def _get_content_type(self, extension: str) -> str:
        """Get MIME type for file extension"""
        content_types = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/mp4',
            '.ogg': 'audio/ogg',
        }
        
        return content_types.get(extension.lower(), 'application/octet-stream')

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # VALIDATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def exists(self, s3_key: str) -> bool:
        """Check if file exists in B2"""
        if not self.s3_client:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.head_object(
                    Bucket=settings.B2_BUCKET,
                    Key=s3_key,
                )
            )
            
            return True
            
        except ClientError:
            return False

    async def get_file_info(self, s3_key: str) -> dict:
        """Get file metadata from B2"""
        if not self.s3_client:
            return {}
        
        try:
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.s3_client.head_object(
                    Bucket=settings.B2_BUCKET,
                    Key=s3_key,
                )
            )
            
            return {
                'size': response.get('ContentLength', 0),
                'content_type': response.get('ContentType', ''),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag', '').strip('"'),
            }
            
        except ClientError as e:
            print(f"[StorageUploader] Get info failed: {e}")
            return {}