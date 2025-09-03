from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user
from app.celery_app.tasks import improve_resume_task
from app.core.config import settings
from app.models import User
from app.schemas import (
    ErrorResponse,
    ImprovementListItem,
    ImprovementListResponse,
    ImprovementOut,
    ImprovementQueuedResponse,
)
from app.uow import UnitOfWork, get_uow
from app.utils.pagination import parse_pagination

router = APIRouter(prefix="/resume", tags=["improvements"])
alt_router = APIRouter(tags=["improvements"])  # for /improvements/{id}
logger = logging.getLogger(__name__)


@router.post(
    "/{resume_id}/improve",
    response_model=ImprovementQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enqueue resume improvement",
    description="Queue an asynchronous improvement job for the given resume.",
    responses={
        404: {"model": ErrorResponse, "description": "Resume not found"},
        409: {"model": ErrorResponse, "description": "Duplicate improvement in progress"},
    },
)
async def enqueue_improvement(
    resume_id: str, uow: UnitOfWork = Depends(get_uow), user: User = Depends(get_current_user)
):
    resume = await uow.resumes.get_owned(resume_id, str(user.id))
    if not resume:
        logger.warning("Resume not found for improvement enqueue", extra={"resume_id": resume_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Resume not found"},
        )

    # Optional idempotency: reject duplicate queued/processing improvement for same content
    if settings.IMPROVEMENT_DEDUP_ENABLED:
        dup = await uow.improvements.find_active_duplicate(str(resume.id), resume.content)
        if dup:
            logger.warning(
                "Duplicate improvement detected",
                extra={"resume_id": str(resume.id), "improvement_id": str(dup.id)},
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "duplicate",
                    "message": "Improvement already queued or processing for this content",
                },
            )

    improvement = await uow.improvements.create_queued(
        resume_id=str(resume.id), old_content=resume.content
    )
    await uow.commit()

    async_result = improve_resume_task.delay(str(improvement.id))
    await uow.improvements.set_task_id(improvement, async_result.id)
    await uow.commit()
    logger.info(
        "Improvement enqueued",
        extra={
            "resume_id": str(resume.id),
            "improvement_id": str(improvement.id),
            "task_id": async_result.id,
        },
    )

    return {"improvement_id": str(improvement.id), "status": improvement.status.value}


@router.get(
    "/improvements/{improvement_id}",
    response_model=ImprovementOut,
    summary="Get improvement status",
    description="Get status/details of a specific improvement belonging to the user.",
    responses={404: {"model": ErrorResponse, "description": "Improvement not found"}},
)
async def get_improvement(
    improvement_id: str, uow: UnitOfWork = Depends(get_uow), user: User = Depends(get_current_user)
):
    return await _get_improvement_impl(improvement_id, uow, user)


@alt_router.get(
    "/improvements/{improvement_id}", response_model=ImprovementOut, include_in_schema=False
)
async def get_improvement_no_prefix(
    improvement_id: str, uow: UnitOfWork = Depends(get_uow), user: User = Depends(get_current_user)
):
    return await _get_improvement_impl(improvement_id, uow, user)


async def _get_improvement_impl(improvement_id: str, uow: UnitOfWork, user: User) -> ImprovementOut:
    imp = await uow.improvements.get_owned(improvement_id, str(user.id))
    if not imp:
        logger.warning(
            "Improvement not found",
            extra={"improvement_id": improvement_id, "user_id": str(user.id)},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Improvement not found"},
        )
    return ImprovementOut(
        id=str(imp.id),
        resume_id=str(imp.resume_id),
        status=imp.status.value,
        old_content=imp.old_content,
        new_content=imp.new_content,
        error=imp.error,
        applied=imp.applied,
        created_at=imp.created_at,
        started_at=imp.started_at,
        finished_at=imp.finished_at,
    )


@router.get(
    "/{resume_id}/improvements",
    response_model=ImprovementListResponse,
    summary="List improvements for resume",
    description="List improvement attempts for a resume with pagination.",
    responses={404: {"model": ErrorResponse, "description": "Resume not found"}},
)
async def list_improvements(
    resume_id: str,
    user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100, description="Max items to return (1-100)"),
    offset: int = Query(0, ge=0, description="Items to skip for pagination"),
    uow: UnitOfWork = Depends(get_uow),
):
    resume = await uow.resumes.get_owned(resume_id, str(user.id))
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Resume not found"},
        )
    limit, offset = parse_pagination(limit, offset)
    rows, total = await uow.improvements.list_for_resume(str(resume.id), limit, offset)
    items = [
        ImprovementListItem(
            id=str(r.id), status=r.status.value, applied=r.applied, created_at=r.created_at
        )
        for r in rows
    ]
    return {"items": items, "total": total, "limit": limit, "offset": offset}
