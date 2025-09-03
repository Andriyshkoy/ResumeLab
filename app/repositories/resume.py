from __future__ import annotations

"""Repository for `Resume` aggregate."""

from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Resume


class ResumeRepository:
    """Data access layer for resumes."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: str, title: str, content: str) -> Resume:
        """Create and persist a resume for the given user."""
        resume = Resume(user_id=user_id, title=title, content=content)
        self.session.add(resume)
        await self.session.flush()
        await self.session.refresh(resume)
        return resume

    async def get_owned(self, resume_id: str, user_id: str) -> Optional[Resume]:
        """Fetch resume by id ensuring it belongs to the user."""
        result = await self.session.execute(
            select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, resume_id: str) -> Optional[Resume]:
        """Fetch resume by primary key."""
        result = await self.session.execute(select(Resume).where(Resume.id == resume_id))
        return result.scalar_one_or_none()

    async def list_owned(self, user_id: str, limit: int, offset: int) -> Tuple[List[Resume], int]:
        """List resumes for a user along with total count for pagination."""
        base = select(Resume).where(Resume.user_id == user_id)
        total_res = await self.session.execute(select(func.count()).select_from(base.subquery()))
        total = int(total_res.scalar_one())
        rows_res = await self.session.execute(
            base.order_by(Resume.created_at.desc()).limit(limit).offset(offset)
        )
        return list(rows_res.scalars().all()), total

    async def update(self, resume: Resume, title: str, content: str) -> Resume:
        """Update title and content for a resume and persist changes."""
        resume.title = title
        resume.content = content
        self.session.add(resume)
        await self.session.flush()
        await self.session.refresh(resume)
        return resume

    async def delete(self, resume: Resume) -> None:
        """Delete the given resume instance."""
        await self.session.delete(resume)
