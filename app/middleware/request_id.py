from __future__ import annotations

"""Middleware and helpers for request/user correlation IDs in logs and headers."""

import contextvars
import uuid
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")
user_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("user_id", default="-")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach `X-Request-ID` to requests and response; expose it to logs via ContextVar."""

    async def dispatch(self, request: Request, call_next: Callable):  # type: ignore[override]
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_ctx.set(req_id)
        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(token)
        response.headers["X-Request-ID"] = req_id
        return response


def get_request_id() -> str:
    """Return current request id or '-' if missing."""
    return request_id_ctx.get()


def set_user_id(user_id: str | None):
    """Set current user id for log correlation; use '-' if not authenticated."""
    user_id_ctx.set(user_id or "-")


def get_user_id() -> str:
    """Return current user id or '-' if missing."""
    return user_id_ctx.get()
