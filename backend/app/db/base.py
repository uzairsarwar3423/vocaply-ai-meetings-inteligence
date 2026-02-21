# Import all models here so that Alembic can find them
from app.models.base import Base
from app.models import (
    Company, User, UserSession, Meeting, 
    Transcript, TranscriptMetadata, ActionItem, MeetingSummary
)
