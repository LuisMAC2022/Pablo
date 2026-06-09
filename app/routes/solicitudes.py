from typing import List, Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_usuario_actual
from app.permissions import ROLES_SOLICITUDES, usuario_tiene_rol
from app.services.catalogo_solicitudes import AREAS_SOLICITUD_ACTIVAS, CATALOGO_SERVICIOS
from app.services.solicitudes import (
    AreaSolicitanteInvalida,
    OpcionServicioInvalida,
    SubcategoriaServicioInvalida,
    crear_solicitud,
)
from app.services.plantilla_solicitud import generar_archivo_solicitud


router = APIRouter()


@router.get("/solicitud", response_class=HTMLResponse)
async def mostrar_formulario(
    request: Request,
    usuario: dict = Depends(get_usuario_actual),
):
    if not usuario_tiene_rol(usuario, ROLES_SOLICITUDES):
        return RedirectResponse(url="/login", status_code=302)

    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="form.html",
        context={
            "areas": AREAS_SOLICITUD_ACTIVAS,
            "catalogo_servicios": CATALOGO_SERVICIOS,
            "nombre_usuario": usuario.get("nombre", ""),
            "telefono": usuario.get("telefono", ""),
            "area_solicitante": "",
        },
    )


@router.post("/solicitud")
async def recibir_formulario(
    request: Request,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_usuario_actual),
    area_solicitante: str = Form(...),
    descripcion_servicio: str = Form(...),
    subcategoria_servicio: Optional[str] = Form(None),
    infraestructura: Optional[List[str]] = Form(None),
    equipo_parque_vehicular: Optional[List[str]] = Form(None),
    seguridad: Optional[List[str]] = Form(None),
    transporte: Optional[List[str]] = Form(None),
    diversos_limpieza: Optional[List[str]] = Form(None),
    prestamo_de: Optional[List[str]] = Form(None),
    correspondencia_paqueteria: Optional[List[str]] = Form(None),
    reproduccion_engargolado: Optional[List[str]] = Form(None),
):
    if not usuario_tiene_rol(usuario, ROLES_SOLICITUDES):
        return RedirectResponse(url="/login", status_code=302)

    templates = request.app.state.templates

    nombre_usuario = usuario.get("nombre", "")
    telefono = usuario.get("telefono", "") or ""

    try:
        solicitud = crear_solicitud(
            db,
            nombre_usuario=nombre_usuario,
            telefono=telefono,
            area_solicitante=area_solicitante,
            descripcion_servicio=descripcion_servicio,
            subcategoria_servicio=subcategoria_servicio,
            infraestructura=infraestructura,
            equipo_parque_vehicular=equipo_parque_vehicular,
            seguridad=seguridad,
            transporte=transporte,
            diversos_limpieza=diversos_limpieza,
            prestamo_de=prestamo_de,
            correspondencia_paqueteria=correspondencia_paqueteria,
            reproduccion_engargolado=reproduccion_engargolado,
        )
    except (AreaSolicitanteInvalida, SubcategoriaServicioInvalida, OpcionServicioInvalida) as exc:
        return templates.TemplateResponse(
            request=request,
            name="form.html",
            context={
                "areas": AREAS_SOLICITUD_ACTIVAS,
                "catalogo_servicios": CATALOGO_SERVICIOS,
                "nombre_usuario": nombre_usuario,
                "telefono": telefono,
                "area_solicitante": area_solicitante,
                "subcategoria_servicio": subcategoria_servicio,
                "error": str(exc),
            },
            status_code=400,
        )

    archivo_solicitud = generar_archivo_solicitud(solicitud)
    nombre_archivo = f"solicitud_{solicitud.folio}.xlsx"

    return StreamingResponse(
        archivo_solicitud,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
    )
