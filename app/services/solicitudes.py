from datetime import date
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import Solicitud
from app.sheets import agregar_solicitud

from app.services.catalogo_solicitudes import (
    AREAS_SOLICITUD_ACTIVAS,
    CAMPOS_OPCIONES_SERVICIO,
    SUBCATEGORIAS_POR_AREA,
)

# Áreas existentes reservadas para uso futuro: Servicios Educativos,
# Exposiciones Museográficas, Delegación Administrativa.
AREAS_SOLICITUD_INACTIVAS = [
    "Servicios Educativos",
    "Exposiciones Museográficas",
    "Delegación Administrativa",
]


class AreaSolicitanteInvalida(ValueError):
    """Se lanza cuando el área solicitante no pertenece al catálogo permitido."""


class SubcategoriaServicioInvalida(ValueError):
    """Se lanza cuando la subcategoría no corresponde al área seleccionada."""


class OpcionServicioInvalida(ValueError):
    """Se lanza cuando una opción no pertenece a la subcategoría seleccionada."""


def generar_folio(db: Session) -> str:
    total = db.query(Solicitud).count()
    return str(total + 1).zfill(3)


def _normalizar_opciones_servicio(
    area_solicitante: str,
    subcategoria_servicio: Optional[str],
    opciones_por_campo: Dict[str, Optional[List[str]]],
) -> Dict[str, Optional[List[str]]]:
    if area_solicitante not in AREAS_SOLICITUD_ACTIVAS:
        raise AreaSolicitanteInvalida("Área solicitante inválida.")

    subcategorias = SUBCATEGORIAS_POR_AREA[area_solicitante]
    if subcategoria_servicio not in subcategorias:
        raise SubcategoriaServicioInvalida("Seleccione una subcategoría válida para el área solicitante.")

    subcategoria = subcategorias[subcategoria_servicio]
    valores_validos = {opcion["valor"] for opcion in subcategoria["opciones"]}
    opciones_seleccionadas = opciones_por_campo.get(subcategoria_servicio) or []

    if len(opciones_seleccionadas) != 1:
        raise OpcionServicioInvalida("Seleccione exactamente una opción para la subcategoría elegida.")

    if any(opcion not in valores_validos for opcion in opciones_seleccionadas):
        raise OpcionServicioInvalida("Seleccione una opción válida para la subcategoría elegida.")

    return {
        campo: opciones_seleccionadas if campo == subcategoria_servicio else None
        for campo in CAMPOS_OPCIONES_SERVICIO
    }


def crear_solicitud(
    db: Session,
    *,
    nombre_usuario: str,
    telefono: str,
    responsable_area_solicitante: Optional[str],
    area_solicitante: str,
    descripcion_servicio: str,
    subcategoria_servicio: Optional[str] = None,
    infraestructura: Optional[List[str]] = None,
    equipo_parque_vehicular: Optional[List[str]] = None,
    seguridad: Optional[List[str]] = None,
    transporte: Optional[List[str]] = None,
    diversos_limpieza: Optional[List[str]] = None,
    prestamo_de: Optional[List[str]] = None,
    correspondencia_paqueteria: Optional[List[str]] = None,
    reproduccion_engargolado: Optional[List[str]] = None,
) -> Solicitud:
    opciones_servicio = _normalizar_opciones_servicio(
        area_solicitante,
        subcategoria_servicio,
        {
            "infraestructura": infraestructura,
            "equipo_parque_vehicular": equipo_parque_vehicular,
            "seguridad": seguridad,
            "transporte": transporte,
            "diversos_limpieza": diversos_limpieza,
            "prestamo_de": prestamo_de,
            "correspondencia_paqueteria": correspondencia_paqueteria,
            "reproduccion_engargolado": reproduccion_engargolado,
        },
    )

    solicitud = Solicitud(
        folio=generar_folio(db),
        fecha=date.today(),
        nombre_usuario=nombre_usuario,
        telefono=telefono,
        responsable_area_solicitante=responsable_area_solicitante,
        area_solicitante=area_solicitante,
        descripcion_servicio=descripcion_servicio,
        **opciones_servicio,
    )

    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    agregar_solicitud(solicitud)

    return solicitud
