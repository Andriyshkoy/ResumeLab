from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.jwt import create_access_token
from app.core.security import hash_password, verify_password
from app.schemas import ErrorResponse, LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.uow import UnitOfWork, get_uow

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with an email and password.",
    responses={
        409: {
            "model": ErrorResponse,
            "description": "Email is already taken",
            "content": {
                "application/json": {
                    "example": {"error": {"code": "conflict", "message": "Email is already taken"}}
                }
            },
        }
    },
)
async def register(payload: RegisterRequest, uow: UnitOfWork = Depends(get_uow)):
    """Register a user and return public user data."""
    existing = await uow.users.get_by_email(payload.email)
    if existing:
        logger.warning("Registration conflict", extra={"email": payload.email})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "conflict", "message": "Email is already taken"},
        )

    user = await uow.users.create(
        email=payload.email, password_hash=hash_password(payload.password)
    )
    await uow.commit()
    logger.info("User registered", extra={"user_id": str(user.id), "email": user.email})
    return UserOut(id=str(user.id), email=user.email, created_at=user.created_at)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get access token",
    description="Authenticate with email and password and receive a JWT access token.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"error": {"code": "unauthorized", "message": "Invalid credentials"}}
                }
            },
        }
    },
)
async def login(payload: LoginRequest, uow: UnitOfWork = Depends(get_uow)):
    """Authenticate user and return a bearer token."""
    user = await uow.users.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        logger.warning("Login failed", extra={"email": payload.email})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "unauthorized", "message": "Invalid credentials"},
        )

    token = create_access_token(subject=str(user.id), expires_in=settings.ACCESS_TOKEN_TTL)
    logger.info("Login success", extra={"user_id": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, expires_in=settings.ACCESS_TOKEN_TTL)
