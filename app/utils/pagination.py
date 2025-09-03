from __future__ import annotations

"""Helpers for pagination parameters normalization."""

from typing import Tuple


def parse_pagination(limit: int = 20, offset: int = 0) -> Tuple[int, int]:
    """Clamp provided pagination parameters into safe bounds.

    Returns a tuple ``(limit, offset)`` where limit is within [1;100] and offset
    is non-negative.
    """
    limit = max(1, min(100, limit or 20))
    offset = max(0, offset or 0)
    return limit, offset
