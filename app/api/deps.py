from __future__ import annotations

"""Reusable FastAPI dependencies (auth, UoW, etc.)."""

import logging
from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from app.core.jwt import decode_token
from app.middleware.request_id import set_user_id
from app.models import User
from app.uow import UnitOfWork, get_uow

logger = logging.getLogger(__name__)


def get_authorization_token(authorization: Optional[str] = Header(default=None)) -> str:
    """Extract Bearer token from Authorization header or raise 401."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "unauthorized", "message": "Missing Authorization header"},
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "unauthorized", "message": "Invalid Authorization header"},
        )
    return parts[1]


async def get_current_user(
    uow: UnitOfWork = Depends(get_uow), token: str = Depends(get_authorization_token)
) -> User:
    """Resolve the current authenticated user from a JWT access token.

    Returns the `User` instance or raises 401 if token is invalid or user not found.
    Also stores `user_id` in logging context for structured logs.
    """
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        ttype = payload.get("type")
        if not sub or ttype != "access":
            raise ValueError("invalid token claims")
    except Exception:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "unauthorized", "message": "Invalid or expired token"},
        )

    user = await uow.users.get_by_id(sub)
    if not user:
        logger.warning("User not found for token", extra={"user_id": sub})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "unauthorized", "message": "User not found"},
        )
    # propagate user id to logging context
    try:
        set_user_id(str(user.id))
    except Exception:
        pass
    return user
