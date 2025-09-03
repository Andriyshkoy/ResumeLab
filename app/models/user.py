from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, Index, String, func

from app.db.base import Base
from app.models._types import GUID


class User(Base):
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (Index("users_email_key", "email", unique=True),)
