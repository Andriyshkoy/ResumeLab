"""
init

Revision ID: 20250903_090000
Revises:
Create Date: 2025-09-03 09:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "20250903_090000"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        "user",
        sa.Column("id", sa.CHAR(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("users_email_key", "user", ["email"], unique=True)

    # resumes
    op.create_table(
        "resume",
        sa.Column("id", sa.CHAR(length=36), nullable=False),
        sa.Column("user_id", sa.CHAR(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_resume_user_created", "resume", ["user_id", "created_at"], unique=False)

    # improvements
    op.create_table(
        "resumeimprovement",
        sa.Column("id", sa.CHAR(length=36), nullable=False),
        sa.Column("resume_id", sa.CHAR(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=100), nullable=True),
        sa.Column(
            "status",
            sa.Enum("queued", "processing", "done", "failed", name="improvement_status"),
            nullable=False,
        ),
        sa.Column("old_content", sa.Text(), nullable=False),
        sa.Column("new_content", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("applied", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["resume_id"], ["resume.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_improvements_resume_created",
        "resumeimprovement",
        ["resume_id", "created_at"],
        unique=False,
    )
    op.create_index("ix_improvements_status", "resumeimprovement", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_improvements_status", table_name="resumeimprovement")
    op.drop_index("ix_improvements_resume_created", table_name="resumeimprovement")
    op.drop_table("resumeimprovement")
    op.drop_index("ix_resume_user_created", table_name="resume")
    op.drop_table("resume")
    op.drop_index("users_email_key", table_name="user")
    op.drop_table("user")
