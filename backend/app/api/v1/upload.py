"""
Upload API Router
Vocaply Platform - Day 6
"""

import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.schemas.upload import (
    PresignedUrlRequest, PresignedUrlResponse,
    MultipartInitRequest, MultipartInitResponse,
    PartUploadRequest, PartUploadResponse,
    MultipartCompleteRequest, ConfirmUploadRequest,
    UploadCompleteResponse, UploadStatusResponse,
    DeleteResponse,
)
from app.services.storage import create_upload_service, UploadService
from app.api.deps import get_current_user

router = APIRouter(tags=["File Upload"])


async def get_service() -> UploadService:
    # Inject redis in production: redis = Depends(get_redis)
    return create_upload_service(redis=None)


# ── Single Upload ──────────────────────────────────────────────────────

@router.post(
    "/presigned-url",
    response_model=PresignedUrlResponse,
    status_code=201,
    summary="Get presigned URL for direct upload (< 100 MB)",
    description=(
        "Returns a presigned PUT URL. Browser uploads **directly** to Backblaze B2 "
        "— no bytes flow through our API. Then call `/upload/complete`."
    ),
)
async def get_presigned_url(
    body: PresignedUrlRequest,
    user = Depends(get_current_user),
    svc: UploadService = Depends(get_service),
):
    result = await svc.request_presigned_url(
        company_id   = user.company_id,
        meeting_id   = body.meeting_id,
        user_id      = user.id,
        file_name    = body.file_name,
        file_size    = body.file_size,
        content_type = body.content_type,
    )
    return PresignedUrlResponse(**result)


@router.post(
    "/complete",
    response_model=UploadCompleteResponse,
    summary="Confirm upload complete",
    description="Call after browser PUT succeeds. Verifies file in B2 and triggers transcription.",
)
async def complete_upload(
    body: ConfirmUploadRequest,
    user = Depends(get_current_user),
    svc: UploadService = Depends(get_service),
):
    result = await svc.complete_upload(
        upload_id  = body.upload_id,
        company_id = user.company_id,
        etag       = body.etag,
    )
    return UploadCompleteResponse(**result)


# ── Multipart Upload ───────────────────────────────────────────────────

@router.post(
    "/multipart-init",
    response_model=MultipartInitResponse,
    status_code=201,
    summary="Initialize multipart upload (> 100 MB)",
    description=(
        "Initialises B2 multipart upload and returns pre-signed URLs for every part. "
        "Upload parts concurrently, save each ETag, then call `/multipart-upload` + `/multipart-complete`."
    ),
)
async def multipart_init(
    body: MultipartInitRequest,
    user = Depends(get_current_user),
    svc: UploadService = Depends(get_service),
):
    result = await svc.init_multipart(
        company_id   = user.company_id,
        meeting_id   = body.meeting_id,
        user_id      = user.id,
        file_name    = body.file_name,
        file_size    = body.file_size,
        content_type = body.content_type,
    )
    return MultipartInitResponse(**result)


@router.post(
    "/multipart-upload",
    response_model=PartUploadResponse,
    summary="Record a completed part",
    description="Call for each part after successful PUT. Provide the ETag from response headers. Idempotent.",
)
async def record_part(
    body: PartUploadRequest,
    user = Depends(get_current_user),
    svc: UploadService = Depends(get_service),
):
    result = await svc.record_part(
        upload_id   = body.upload_id,
        company_id  = user.company_id,
        part_number = body.part_number,
        etag        = body.etag,
    )
    return PartUploadResponse(**result)


@router.post(
    "/multipart-complete",
    response_model=UploadCompleteResponse,
    summary="Complete multipart upload",
    description="Assembles all parts in B2. All parts must be recorded first.",
)
async def complete_multipart(
    body: MultipartCompleteRequest,
    user = Depends(get_current_user),
    svc: UploadService = Depends(get_service),
):
    result = await svc.complete_multipart(
        upload_id  = body.upload_id,
        company_id = user.company_id,
    )
    return UploadCompleteResponse(**result)


# ── Status & Resumption ────────────────────────────────────────────────

@router.get(
    "/status/{upload_id}",
    response_model=UploadStatusResponse,
    summary="Get upload status",
    description="Returns upload progress. For multipart, shows missing parts for resumption.",
)
async def get_status(
    upload_id: str,
    user = Depends(get_current_user),
    svc: UploadService = Depends(get_service),
):
    return await svc.get_status(upload_id=upload_id, company_id=user.company_id)


@router.delete(
    "/abort/{upload_id}",
    status_code=204,
    summary="Abort an upload",
    description="Cancels in-progress upload and cleans up B2 parts.",
)
async def abort_upload(
    upload_id: str,
    user = Depends(get_current_user),
    svc: UploadService = Depends(get_service),
):
    await svc.abort(upload_id=upload_id, company_id=user.company_id)
    return JSONResponse(status_code=204, content=None)


# ── Delete ─────────────────────────────────────────────────────────────

@router.delete(
    "/{file_key:path}",
    response_model=DeleteResponse,
    summary="Delete a file from storage",
    description="Permanently removes file from B2. Only files owned by your company can be deleted.",
)
async def delete_file(
    file_key: str,
    user = Depends(get_current_user),
    svc: UploadService = Depends(get_service),
):
    result = await svc.delete_file(s3_key=file_key, company_id=user.company_id)
    return DeleteResponse(**result)