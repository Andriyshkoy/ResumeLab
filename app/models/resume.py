from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models._types import GUID


class Resume(Base):
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", backref="resumes")

    # Children improvements; rely solely on DB ON DELETE CASCADE.
    # passive_deletes=True prevents ORM from emitting UPDATE resume_id=NULL.
    improvements = relationship(
        "ResumeImprovement",
        back_populates="resume",
        passive_deletes=True,
    )

    __table_args__ = (Index("ix_resume_user_created", "user_id", "created_at"),)
