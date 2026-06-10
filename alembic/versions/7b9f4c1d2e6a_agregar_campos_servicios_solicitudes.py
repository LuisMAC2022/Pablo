"""agregar campos servicios solicitudes

Revision ID: 7b9f4c1d2e6a
Revises: 92fc0c2a648a
Create Date: 2026-06-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b9f4c1d2e6a"
down_revision: Union[str, Sequence[str], None] = "92fc0c2a648a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


COLUMNAS_SERVICIO = (
    "seguridad",
    "transporte",
    "diversos_limpieza",
    "prestamo_de",
    "correspondencia_paqueteria",
    "reproduccion_engargolado",
)


def upgrade() -> None:
    """Upgrade schema."""
    for columna in COLUMNAS_SERVICIO:
        op.add_column("solicitudes", sa.Column(columna, sa.ARRAY(sa.String()), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    for columna in reversed(COLUMNAS_SERVICIO):
        op.drop_column("solicitudes", columna)
