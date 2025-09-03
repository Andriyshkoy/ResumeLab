from __future__ import annotations

import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models._types import GUID


class ImprovementStatus(str, enum.Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    failed = "failed"


class ResumeImprovement(Base):
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    resume_id = Column(
        GUID, ForeignKey("resume.id", ondelete="CASCADE"), index=True, nullable=False
    )
    task_id = Column(String(100), nullable=True)
    status = Column(
        Enum(ImprovementStatus, name="improvement_status", native_enum=False), nullable=False
    )
    old_content = Column(Text, nullable=False)
    new_content = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    applied = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    resume = relationship("Resume", backref="improvements")

    __table_args__ = (
        Index("ix_improvements_resume_created", "resume_id", "created_at"),
        Index("ix_improvements_status", "status"),
    )
