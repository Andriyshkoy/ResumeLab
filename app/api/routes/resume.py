from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user
from app.models import User
from app.schemas import (
    ErrorResponse,
    ResumeCreate,
    ResumeListItem,
    ResumeListResponse,
    ResumeOut,
    ResumeUpdate,
)
from app.uow import UnitOfWork, get_uow
from app.utils.pagination import parse_pagination

router = APIRouter(prefix="/resume", tags=["resume"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=ResumeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a resume",
    description="Create a resume for the authenticated user.",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
async def create_resume(
    payload: ResumeCreate,
    uow: UnitOfWork = Depends(get_uow),
    user: User = Depends(get_current_user),
):
    resume = await uow.resumes.create(
        user_id=str(user.id), title=payload.title, content=payload.content
    )
    await uow.commit()
    logger.info("Resume created", extra={"user_id": str(user.id), "resume_id": str(resume.id)})
    return ResumeOut(
        id=str(resume.id),
        title=resume.title,
        content=resume.content,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )


@router.get(
    "",
    response_model=ResumeListResponse,
    summary="List resumes",
    description="List resumes owned by the authenticated user with pagination.",
)
async def list_resumes(
    user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100, description="Max items to return (1-100)"),
    offset: int = Query(0, ge=0, description="Items to skip for pagination"),
    uow: UnitOfWork = Depends(get_uow),
):
    limit, offset = parse_pagination(limit, offset)
    rows, total = await uow.resumes.list_owned(user_id=str(user.id), limit=limit, offset=offset)
    items = [
        ResumeListItem(
            id=str(r.id), title=r.title, created_at=r.created_at, updated_at=r.updated_at
        )
        for r in rows
    ]
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get(
    "/{resume_id}",
    response_model=ResumeOut,
    summary="Get a resume",
    description="Fetch a single resume by its ID if it belongs to the authenticated user.",
    responses={404: {"model": ErrorResponse, "description": "Resume not found"}},
)
async def get_resume(
    resume_id: str, uow: UnitOfWork = Depends(get_uow), user: User = Depends(get_current_user)
):
    resume = await uow.resumes.get_owned(resume_id, str(user.id))
    if not resume:
        logger.warning(
            "Resume not found for get", extra={"resume_id": resume_id, "user_id": str(user.id)}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Resume not found"},
        )
    return ResumeOut(
        id=str(resume.id),
        title=resume.title,
        content=resume.content,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )


@router.put(
    "/{resume_id}",
    response_model=ResumeOut,
    summary="Update a resume",
    description="Update the title/content of a resume owned by the authenticated user.",
    responses={404: {"model": ErrorResponse, "description": "Resume not found"}},
)
async def update_resume(
    resume_id: str,
    payload: ResumeUpdate,
    uow: UnitOfWork = Depends(get_uow),
    user: User = Depends(get_current_user),
):
    resume = await uow.resumes.get_owned(resume_id, str(user.id))
    if not resume:
        logger.warning(
            "Resume not found for update", extra={"resume_id": resume_id, "user_id": str(user.id)}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Resume not found"},
        )
    resume = await uow.resumes.update(resume, title=payload.title, content=payload.content)
    await uow.commit()
    logger.info("Resume updated", extra={"user_id": str(user.id), "resume_id": str(resume.id)})
    return ResumeOut(
        id=str(resume.id),
        title=resume.title,
        content=resume.content,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resume",
    description="Delete a resume owned by the authenticated user.",
    responses={404: {"model": ErrorResponse, "description": "Resume not found"}},
)
async def delete_resume(
    resume_id: str, uow: UnitOfWork = Depends(get_uow), user: User = Depends(get_current_user)
):
    resume = await uow.resumes.get_owned(resume_id, str(user.id))
    if not resume:
        logger.warning(
            "Resume not found for delete", extra={"resume_id": resume_id, "user_id": str(user.id)}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Resume not found"},
        )
    await uow.resumes.delete(resume)
    await uow.commit()
    logger.info("Resume deleted", extra={"user_id": str(user.id), "resume_id": resume_id})
    return None
