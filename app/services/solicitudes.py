from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Solicitud
from app.sheets import agregar_solicitud


AREAS_SOLICITUD_ACTIVAS = [
    "Mantenimiento y Protección Civil",
    "Seguridad",
    "Servicios de Apoyo",
]

# Áreas existentes reservadas para uso futuro: Servicios Educativos,
# Exposiciones Museográficas, Delegación Administrativa.
AREAS_SOLICITUD_INACTIVAS = [
    "Servicios Educativos",
    "Exposiciones Museográficas",
    "Delegación Administrativa",
]


class AreaSolicitanteInvalida(ValueError):
    """Se lanza cuando el área solicitante no pertenece al catálogo permitido."""


def generar_folio(db: Session) -> str:
    total = db.query(Solicitud).count()
    return str(total + 1).zfill(3)


def crear_solicitud(
    db: Session,
    *,
    nombre_usuario: str,
    telefono: str,
    area_solicitante: str,
    descripcion_servicio: str,
    infraestructura: Optional[List[str]] = None,
    equipo_parque_vehicular: Optional[List[str]] = None,
) -> Solicitud:
    if area_solicitante not in AREAS_SOLICITUD_ACTIVAS:
        raise AreaSolicitanteInvalida("Área solicitante inválida.")

    solicitud = Solicitud(
        folio=generar_folio(db),
        fecha=date.today(),
        nombre_usuario=nombre_usuario,
        telefono=telefono,
        area_solicitante=area_solicitante,
        descripcion_servicio=descripcion_servicio,
        infraestructura=infraestructura,
        equipo_parque_vehicular=equipo_parque_vehicular,
    )

    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    agregar_solicitud(solicitud)

    return solicitud
