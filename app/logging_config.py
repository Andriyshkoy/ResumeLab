from __future__ import annotations

"""Structured JSON logging configuration with request/user correlation IDs."""

import json
import logging
import sys
from datetime import datetime, timezone

from app.core.config import settings
from app.middleware.request_id import get_request_id, get_user_id


class JsonFormatter(logging.Formatter):
    """Format log records as JSON with timestamp and correlation identifiers."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        payload = {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "request_id": get_request_id(),
            "user_id": get_user_id(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging():
    """Install JSON formatter on root logger and set level from settings."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
