from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel

ImprovementStatusLiteral = Literal["queued", "processing", "done", "failed"]


class ImprovementQueuedResponse(BaseModel):
    improvement_id: str
    status: ImprovementStatusLiteral


class ImprovementOut(BaseModel):
    id: str
    resume_id: str
    status: ImprovementStatusLiteral
    old_content: str
    new_content: Optional[str] = None
    error: Optional[str] = None
    applied: bool
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class ImprovementListItem(BaseModel):
    id: str
    status: ImprovementStatusLiteral
    applied: bool
    created_at: datetime


class ImprovementListResponse(BaseModel):
    items: List[ImprovementListItem]
    total: int
    limit: int
    offset: int
