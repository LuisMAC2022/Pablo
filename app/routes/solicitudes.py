from typing import List, Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_usuario_actual
from app.permissions import ROLES_SOLICITUDES, usuario_tiene_rol
from app.services.solicitudes import (
    AREAS_SOLICITUD_ACTIVAS,
    AreaSolicitanteInvalida,
    crear_solicitud,
)


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
        },
    )


@router.post("/solicitud", response_class=HTMLResponse)
async def recibir_formulario(
    request: Request,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_usuario_actual),
    nombre_usuario: str = Form(...),
    telefono: str = Form(...),
    area_solicitante: str = Form(...),
    descripcion_servicio: str = Form(...),
    infraestructura: Optional[List[str]] = Form(None),
    equipo_parque_vehicular: Optional[List[str]] = Form(None),
):
    if not usuario_tiene_rol(usuario, ROLES_SOLICITUDES):
        return RedirectResponse(url="/login", status_code=302)

    templates = request.app.state.templates

    try:
        solicitud = crear_solicitud(
            db,
            nombre_usuario=nombre_usuario,
            telefono=telefono,
            area_solicitante=area_solicitante,
            descripcion_servicio=descripcion_servicio,
            infraestructura=infraestructura,
            equipo_parque_vehicular=equipo_parque_vehicular,
        )
    except AreaSolicitanteInvalida as exc:
        return templates.TemplateResponse(
            request=request,
            name="form.html",
            context={
                "areas": AREAS_SOLICITUD_ACTIVAS,
                "error": str(exc),
            },
            status_code=400,
        )

    return templates.TemplateResponse(
        request=request,
        name="confirmacion.html",
        context={
            "folio": solicitud.folio,
            "fecha": solicitud.fecha.strftime("%d/%m/%Y"),
            "nombre_usuario": solicitud.nombre_usuario,
            "area_solicitante": solicitud.area_solicitante,
        },
    )
