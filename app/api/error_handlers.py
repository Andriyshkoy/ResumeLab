from __future__ import annotations

"""Global error handlers for FastAPI app with structured JSON responses."""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def install_error_handlers(app: FastAPI) -> None:
    """Register HTTP, validation, and unhandled exception handlers."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ):  # type: ignore[override]
        detail = exc.detail
        if isinstance(detail, dict) and "code" in detail:
            payload = {"error": detail}
        else:
            payload = {
                "error": {
                    "code": "error",
                    "message": str(detail) if detail else "HTTP error",
                }
            }
        try:
            logger.warning(
                "HTTPException",
                extra={
                    "status": exc.status_code,
                    "error_code": payload["error"].get("code"),
                },
            )
        except Exception:
            pass
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):  # type: ignore[override]
        payload = {
            "error": {
                "code": "validation_error",
                "message": jsonable_encoder(exc.errors()),
            }
        }
        try:
            logger.warning("RequestValidationError", extra={"errors": payload["error"]["message"]})
        except Exception:
            pass
        return JSONResponse(status_code=422, content=payload)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ):  # type: ignore[override]
        try:
            logger.exception("Unhandled exception")
        except Exception:
            pass
        payload = {"error": {"code": "internal_error", "message": "Internal Server Error"}}
        return JSONResponse(status_code=500, content=payload)
