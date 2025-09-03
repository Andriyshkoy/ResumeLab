from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ResumeCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content: str = Field(..., max_length=50_000)


class ResumeUpdate(BaseModel):
    title: str = Field(..., max_length=200)
    content: str = Field(..., max_length=50_000)


class ResumeOut(BaseModel):
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class ResumeListItem(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ResumeListResponse(BaseModel):
    items: List[ResumeListItem]
    total: int
    limit: int
    offset: int
