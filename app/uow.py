from __future__ import annotations

"""Unit of Work pattern for coordinating repositories and transactions."""

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repositories import ImprovementRepository, ResumeRepository, UserRepository


class UnitOfWork:
    """Lightweight unit of work holding repositories and an `AsyncSession`."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.resumes = ResumeRepository(session)
        self.improvements = ImprovementRepository(session)

    async def commit(self):
        """Commit the current transaction."""
        await self.session.commit()

    async def rollback(self):
        """Rollback the current transaction."""
        await self.session.rollback()


async def get_uow() -> AsyncIterator[UnitOfWork]:
    """FastAPI dependency yielding a `UnitOfWork` in a managed session."""
    async with AsyncSessionLocal() as session:
        uow = UnitOfWork(session)
        try:
            yield uow
        except Exception:
            try:
                await uow.rollback()
            finally:
                raise
        finally:
            await session.close()
