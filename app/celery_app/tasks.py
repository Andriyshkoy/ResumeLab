from __future__ import annotations

"""Celery tasks for resume improvements.

Contains the synchronous Celery task entrypoint and helpers which run async
database logic on a dedicated background event loop.
"""

import asyncio
import logging
import threading
from datetime import datetime, timezone

from celery.exceptions import SoftTimeLimitExceeded
from sqlalchemy.orm.exc import StaleDataError

from app.celery_app.worker import celery_app
from app.db.session import AsyncSessionLocal
from app.models import ImprovementStatus
from app.uow import UnitOfWork

logger = logging.getLogger(__name__)


@celery_app.task(
    name="improve_resume_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def improve_resume_task(self, improvement_id: str):
    """Improve resume content asynchronously.

    Parameters:
        improvement_id: ID of `ResumeImprovement` to process.

    Notes:
        The function delegates to an async implementation and blocks until completion
        on a persistent background event loop. Retries are handled by Celery; on
        final failure, the improvement is marked as failed in the DB.
    """
    try:
        logger.info(
            "Celery task received",
            extra={"task": "improve_resume_task", "improvement_id": improvement_id},
        )
        _run_async(_improve_resume_task_async(improvement_id))
        logger.info(
            "Celery task completed",
            extra={"task": "improve_resume_task", "improvement_id": improvement_id},
        )
    except Exception as e:  # noqa: BLE001
        # If retries exhausted, mark failed in DB, otherwise propagate for retry
        if getattr(self.request, "retries", 0) >= getattr(self, "max_retries", 3):
            logger.exception(
                "Celery task failed, marking as failed",
                extra={
                    "task": "improve_resume_task",
                    "improvement_id": improvement_id,
                    "retries": getattr(self.request, "retries", 0),
                },
            )
            _run_async(_mark_improvement_failed(improvement_id, str(e)))
        raise


async def _improve_resume_task_async(improvement_id: str):
    """Async implementation of resume improvement pipeline.

    Flow:
    - Load improvement; exit if it was deleted.
    - Mark as processing and commit.
    - Call mocked LLM to get improved text.
    - Update resume content and mark improvement as done.
    - If records were concurrently deleted, exit quietly.
    """
    async with AsyncSessionLocal() as session:
        uow = UnitOfWork(session)
        try:
            # Load improvement; if gone, nothing to do
            imp = await uow.improvements.get_by_id(improvement_id)
            if not imp:
                logger.warning("Improvement not found", extra={"improvement_id": improvement_id})
                return

            # Mark as processing
            try:
                imp.status = ImprovementStatus.processing
                imp.started_at = datetime.now(tz=timezone.utc)
                await uow.session.flush()
                await uow.commit()
            except StaleDataError:
                await uow.rollback()
                logger.info(
                    "Improvement gone before processing",
                    extra={"improvement_id": improvement_id},
                )
                return

            # Mocked LLM call (sleep + echo with [Improved])
            new_content = await _mock_llm_improve(imp.old_content)

            # Finalize: if resume or improvement disappeared, exit quietly
            imp = await uow.improvements.get_by_id(improvement_id)
            if not imp:
                logger.info(
                    "Improvement deleted during processing",
                    extra={"improvement_id": improvement_id},
                )
                return

            resume = await uow.resumes.get_by_id(str(imp.resume_id))
            if not resume:
                logger.info(
                    "Resume deleted; skipping apply",
                    extra={"improvement_id": improvement_id},
                )
                return

            try:
                imp.new_content = new_content
                imp.status = ImprovementStatus.done
                imp.applied = True
                imp.finished_at = datetime.now(tz=timezone.utc)
                resume.content = new_content
                await uow.session.flush()
                await uow.commit()
            except StaleDataError:
                await uow.rollback()
                logger.info(
                    "Record removed before finalize",
                    extra={"improvement_id": improvement_id},
                )
                return

            logger.info(
                "Improvement applied",
                extra={
                    "improvement_id": improvement_id,
                    "resume_id": str(imp.resume_id),
                    "status": imp.status.value,
                },
            )
        except SoftTimeLimitExceeded:
            # Let Celery retry or escalate; wrapper will mark failed on last retry
            await uow.rollback()
            logger.warning("Soft time limit exceeded", extra={"improvement_id": improvement_id})
            raise
        except Exception:
            # Let Celery retry or escalate; wrapper will mark failed on last retry
            await uow.rollback()
            logger.exception("Error during improvement", extra={"improvement_id": improvement_id})
            raise


async def _mock_llm_improve(text: str, delay_seconds: float = 3.0) -> str:
    """Mock LLM call: wait `delay_seconds` and return improved text.

    Keeps task structure stable for easy future swap to a real client.
    """
    await asyncio.sleep(delay_seconds)
    return f"{text} [Improved]"


async def _mark_improvement_failed(improvement_id: str, error: str):
    """Mark an improvement as failed and persist error message."""
    async with AsyncSessionLocal() as session:
        uow = UnitOfWork(session)
        imp = await uow.improvements.get_by_id(improvement_id)
        if imp:
            imp.status = ImprovementStatus.failed
            imp.error = error
            imp.finished_at = datetime.now(tz=timezone.utc)
            await uow.session.flush()
            await uow.commit()
            logger.info(
                "Marked improvement as failed",
                extra={"improvement_id": improvement_id, "error": error},
            )


_bg_loop: asyncio.AbstractEventLoop | None = None
_bg_thread: threading.Thread | None = None
_bg_loop_ready = threading.Event()


def _ensure_background_loop() -> asyncio.AbstractEventLoop:
    """Create or return a persistent background event loop per worker process."""
    global _bg_loop, _bg_thread
    if _bg_loop and _bg_loop.is_running():
        return _bg_loop

    def _run_loop(loop: asyncio.AbstractEventLoop):
        asyncio.set_event_loop(loop)
        _bg_loop_ready.set()
        loop.run_forever()

    _bg_loop = asyncio.new_event_loop()
    _bg_thread = threading.Thread(
        target=_run_loop, args=(_bg_loop,), name="celery-asyncio-loop", daemon=True
    )
    _bg_thread.start()
    _bg_loop_ready.wait()
    return _bg_loop


def _run_async(coro):
    """Run an async coroutine on the background loop and wait for result."""
    loop = _ensure_background_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()


__all__ = ["improve_resume_task"]
