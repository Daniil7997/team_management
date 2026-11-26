"""seed admin

Revision ID: db299dffea39
Revises: fd569295c9a2
Create Date: 2026-11-26 10:18:15.015380

"""
from typing import Sequence, Union
import datetime as dt
import uuid

from alembic import op
import sqlalchemy as sa

from app.core.config import settings

# revision identifiers, used by Alembic.
revision: str = 'db299dffea39'
down_revision: Union[str, Sequence[str], None] = 'fd569295c9a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


now = dt.datetime.now(dt.UTC)


def upgrade():
    users_table = sa.table(
        "users",
        sa.column("id", sa.UUID),
        sa.column("name", sa.String),
        sa.column("email", sa.String),
        sa.column("password", sa.String),
        sa.column("is_admin", sa.Boolean),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )

    op.bulk_insert(
        users_table,
        [
            {
                "id": uuid.uuid7(),
                "name": "Admin",
                "email": "admin@example.com",
                "password": settings.app.hashed_admin_password,
                "is_admin": True,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
