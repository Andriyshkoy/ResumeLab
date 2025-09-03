"""
Convert CHAR(36) IDs to UUID

Revision ID: 20250903_200500
Revises: 20250903_090000
Create Date: 2025-09-03 20:05:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as psql

revision = "20250903_200500"
down_revision = "20250903_090000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop foreign keys that reference columns we are changing
    op.drop_constraint("resume_user_id_fkey", "resume", type_="foreignkey")
    op.drop_constraint("resumeimprovement_resume_id_fkey", "resumeimprovement", type_="foreignkey")

    # Convert primary key and foreign key columns to UUID
    op.alter_column(
        "user",
        "id",
        type_=psql.UUID(as_uuid=True),
        postgresql_using="id::uuid",
    )

    op.alter_column(
        "resume",
        "id",
        type_=psql.UUID(as_uuid=True),
        postgresql_using="id::uuid",
    )
    op.alter_column(
        "resume",
        "user_id",
        type_=psql.UUID(as_uuid=True),
        postgresql_using="user_id::uuid",
    )

    op.alter_column(
        "resumeimprovement",
        "id",
        type_=psql.UUID(as_uuid=True),
        postgresql_using="id::uuid",
    )
    op.alter_column(
        "resumeimprovement",
        "resume_id",
        type_=psql.UUID(as_uuid=True),
        postgresql_using="resume_id::uuid",
    )

    # Recreate foreign keys with the new UUID types
    op.create_foreign_key(
        "resume_user_id_fkey",
        "resume",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "resumeimprovement_resume_id_fkey",
        "resumeimprovement",
        "resume",
        ["resume_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # Drop FKs first
    op.drop_constraint("resumeimprovement_resume_id_fkey", "resumeimprovement", type_="foreignkey")
    op.drop_constraint("resume_user_id_fkey", "resume", type_="foreignkey")

    # Revert types back to CHAR(36)
    char36 = sa.CHAR(length=36)

    op.alter_column(
        "resumeimprovement",
        "resume_id",
        type_=char36,
        postgresql_using="resume_id::text",
    )
    op.alter_column(
        "resumeimprovement",
        "id",
        type_=char36,
        postgresql_using="id::text",
    )

    op.alter_column(
        "resume",
        "user_id",
        type_=char36,
        postgresql_using="user_id::text",
    )
    op.alter_column(
        "resume",
        "id",
        type_=char36,
        postgresql_using="id::text",
    )

    op.alter_column(
        "user",
        "id",
        type_=char36,
        postgresql_using="id::text",
    )

    # Recreate original foreign keys
    op.create_foreign_key(
        "resumeimprovement_resume_id_fkey",
        "resumeimprovement",
        "resume",
        ["resume_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "resume_user_id_fkey",
        "resume",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
