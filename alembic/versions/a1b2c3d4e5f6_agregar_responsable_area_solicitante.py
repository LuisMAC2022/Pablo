"""agregar responsable area solicitante

Revision ID: a1b2c3d4e5f6
Revises: 7b9f4c1d2e6a
Create Date: 2026-06-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "7b9f4c1d2e6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("solicitudes", sa.Column("responsable_area_solicitante", sa.String(length=100), nullable=True))
    op.alter_column("solicitudes", "telefono", existing_type=sa.String(length=20), type_=sa.String(length=30), existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("solicitudes", "telefono", existing_type=sa.String(length=30), type_=sa.String(length=20), existing_nullable=False)
    op.drop_column("solicitudes", "responsable_area_solicitante")
