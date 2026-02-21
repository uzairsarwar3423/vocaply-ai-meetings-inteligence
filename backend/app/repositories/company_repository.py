from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import CRUDBase
from app.models.company import Company
from pydantic import BaseModel

class CompanyCreate(BaseModel):
    name: str
    slug: str

class CompanyUpdate(BaseModel):
    name: Optional[str] = None

class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Company]:
        return db.query(Company).filter(Company.slug == slug).first()

company_repo = CRUDCompany(Company)
