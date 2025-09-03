from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    description="Return a simple health status payload to indicate the API is running.",
    responses={
        200: {
            "description": "Service healthy",
            "content": {"application/json": {"example": {"status": "ok"}}},
        }
    },
)
def health():
    """Basic liveness endpoint."""
    return {"status": "ok"}
