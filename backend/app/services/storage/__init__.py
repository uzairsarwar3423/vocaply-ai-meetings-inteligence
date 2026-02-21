"""Storage service package"""
from app.services.storage.backblaze_service import BackblazeService
from app.services.storage.upload_service import UploadService
from app.services.storage.file_validator import FileValidator

__all__ = ["BackblazeService", "UploadService", "FileValidator"]


def create_upload_service(redis=None) -> UploadService:
    return UploadService(
        storage   = BackblazeService(),
        validator = FileValidator(),
        redis     = redis,
    )