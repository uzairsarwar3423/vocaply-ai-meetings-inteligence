"""
Pagination Schemas
Vocaply Platform - Day 4
File: backend/app/schemas/pagination.py
"""
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel, Field
import base64
import json

T = TypeVar("T")

# ============================================
# OFFSET PAGINATION
# ============================================

class OffsetPaginationParams(BaseModel):
    page:     int = Field(default=1,  ge=1,  description="Page number (1-indexed)")
    per_page: int = Field(default=20, ge=1,  le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page


PaginationParams = OffsetPaginationParams


class OffsetPaginationMeta(BaseModel):
    page:        int  = Field(description="Current page")
    per_page:    int  = Field(description="Items per page")
    total_items: int  = Field(description="Total items")
    total_pages: int  = Field(description="Total pages")
    has_next:    bool = Field(description="Has next page")
    has_prev:    bool = Field(description="Has previous page")

    @classmethod
    def create(cls, page: int, per_page: int, total_items: int) -> "OffsetPaginationMeta":
        total_pages = max(1, -(-total_items // per_page))
        return cls(
            page=page,
            per_page=per_page,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )


PaginationMeta = OffsetPaginationMeta


class PaginatedResponse(BaseModel, Generic[T]):
    data:       List[T]              = Field(description="List of items")
    pagination: OffsetPaginationMeta = Field(description="Pagination metadata")
    filters:    Optional[dict]       = Field(default=None, description="Applied filters")

    class Config:
        arbitrary_types_allowed = True


# ============================================
# CURSOR PAGINATION
# ============================================

class CursorPaginationParams(BaseModel):
    cursor:    Optional[str] = Field(default=None, description="Cursor from previous response")
    limit:     int           = Field(default=20, ge=1, le=100)
    direction: str           = Field(default="next")


class CursorPaginationMeta(BaseModel):
    next_cursor:  Optional[str] = Field(default=None)
    prev_cursor:  Optional[str] = Field(default=None)
    has_more:     bool
    limit:        int
    total_items:  Optional[int] = None


class CursorPaginatedResponse(BaseModel, Generic[T]):
    data:       List[T]              = Field(description="List of items")
    pagination: CursorPaginationMeta = Field(description="Cursor pagination metadata")

    class Config:
        arbitrary_types_allowed = True


# ============================================
# HELPERS
# ============================================

def encode_cursor(data: dict) -> str:
    """Encode a dict into a base64 cursor string"""
    return base64.b64encode(json.dumps(data).encode()).decode()


def decode_cursor(cursor: str) -> dict:
    """Decode a base64 cursor string into a dict"""
    try:
        return json.loads(base64.b64decode(cursor.encode()).decode())
    except Exception:
        raise ValueError("Invalid cursor")