from typing import Optional, Union
import uuid
from sqlalchemy.orm import Session
from app.repositories.base import CRUDBase
from app.models.user_session import UserSession
from pydantic import BaseModel
from datetime import datetime

class SessionCreate(BaseModel):
    user_id: Union[str, uuid.UUID]
    refresh_token: str
    expires_at: datetime
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

class SessionUpdate(BaseModel):
    is_revoked: bool

class CRUDSession(CRUDBase[UserSession, SessionCreate, SessionUpdate]):
    def get_by_refresh_token(self, db: Session, *, refresh_token: str) -> Optional[UserSession]:
        return db.query(UserSession).filter(UserSession.refresh_token == refresh_token).first()

session_repo = CRUDSession(UserSession)
