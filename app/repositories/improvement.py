from __future__ import annotations

"""Repository for `ResumeImprovement` aggregate."""

from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ImprovementStatus, Resume, ResumeImprovement


class ImprovementRepository:
    """Data access layer for improvements."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_queued(self, resume_id: str, old_content: str) -> ResumeImprovement:
        """Create a queued improvement for a resume.

        Returns the newly created `ResumeImprovement` persisted to the DB.
        """
        imp = ResumeImprovement(
            resume_id=resume_id, status=ImprovementStatus.queued, old_content=old_content
        )
        self.session.add(imp)
        await self.session.flush()
        await self.session.refresh(imp)
        return imp

    async def set_task_id(self, imp: ResumeImprovement, task_id: str) -> None:
        """Attach Celery task id to improvement and persist."""
        imp.task_id = task_id
        self.session.add(imp)
        await self.session.flush()

    async def get_owned(self, improvement_id: str, user_id: str) -> Optional[ResumeImprovement]:
        """Fetch improvement by id ensuring it belongs to the user via resume ownership."""
        q = (
            select(ResumeImprovement)
            .join(Resume, Resume.id == ResumeImprovement.resume_id)
            .where(ResumeImprovement.id == improvement_id, Resume.user_id == user_id)
        )
        res = await self.session.execute(q)
        return res.scalar_one_or_none()

    async def list_for_resume(
        self, resume_id: str, limit: int, offset: int
    ) -> Tuple[List[ResumeImprovement], int]:
        """List improvements for a resume with total count for pagination."""
        base = select(ResumeImprovement).where(ResumeImprovement.resume_id == resume_id)
        total_res = await self.session.execute(select(func.count()).select_from(base.subquery()))
        total = int(total_res.scalar_one())
        rows_res = await self.session.execute(
            base.order_by(ResumeImprovement.created_at.desc()).limit(limit).offset(offset)
        )
        return list(rows_res.scalars().all()), total

    async def get_by_id(self, improvement_id: str) -> Optional[ResumeImprovement]:
        """Get improvement by primary key."""
        res = await self.session.execute(
            select(ResumeImprovement).where(ResumeImprovement.id == improvement_id)
        )
        return res.scalar_one_or_none()

    async def find_active_duplicate(
        self, resume_id: str, old_content: str
    ) -> Optional[ResumeImprovement]:
        """Return queued/processing improvement for the same resume/content."""
        q = select(ResumeImprovement).where(
            ResumeImprovement.resume_id == resume_id,
            ResumeImprovement.old_content == old_content,
            ResumeImprovement.status.in_([ImprovementStatus.queued, ImprovementStatus.processing]),
        )
        res = await self.session.execute(q)
        return res.scalar_one_or_none()
