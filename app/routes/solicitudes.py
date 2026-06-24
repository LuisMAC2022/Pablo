import json
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Solicitud
from app.dependencies import get_usuario_actual
from app.permissions import ROLES_SOLICITUDES, puede_editar_datos_solicitante, usuario_tiene_rol
from app.services.catalogo_solicitudes import AREAS_SOLICITUD_ACTIVAS, CATALOGO_SERVICIOS
from app.services.plantilla_solicitud import (
    NOMBRE_ARCHIVO_SOLICITUD,
    generar_plantilla_solicitud,
)
from app.services.solicitudes_pdf import (
    CARPETA_SOLICITUDES,
    ErrorConversionSolicitudPDF,
    guardar_solicitud_pdf,
    listar_solicitudes_pdf,
)
from app.services.solicitudes import (
    AreaSolicitanteInvalida,
    OpcionServicioInvalida,
    SubcategoriaServicioInvalida,
    crear_solicitud,
)


router = APIRouter()

TELEFONO_JEFE_MANTENIMIENTO = "5556228222 ext. 82581"
RUTA_DIRECTORIO_AUTOCOMPLETE = Path(__file__).resolve().parents[2] / "dir_autocomplete.json"


def cargar_personas_autocomplete() -> list[dict[str, str]]:
    with RUTA_DIRECTORIO_AUTOCOMPLETE.open(encoding="utf-8") as archivo:
        directorio = json.load(archivo)

    personas = []
    for persona in directorio.get("personas", []):
        nombre = str(persona.get("nombre", "")).strip()
        if not nombre:
            continue

        etiqueta = str(persona.get("etiqueta", "")).strip()
        personas.append({"nombre": nombre, "etiqueta": etiqueta})

    return personas


def contexto_formulario(usuario: dict, **valores) -> dict:
    puede_editar = puede_editar_datos_solicitante(usuario)
    return {
        "areas": AREAS_SOLICITUD_ACTIVAS,
        "catalogo_servicios": CATALOGO_SERVICIOS,
        "nombre_usuario": valores.get("nombre_usuario", usuario.get("nombre", "")),
        "responsable_area_solicitante": valores.get("responsable_area_solicitante", ""),
        "telefono": valores.get("telefono", TELEFONO_JEFE_MANTENIMIENTO),
        "area_solicitante": valores.get("area_solicitante", ""),
        "subcategoria_servicio": valores.get("subcategoria_servicio", ""),
        "descripcion_servicio": valores.get("descripcion_servicio", ""),
        "personas_autocomplete": cargar_personas_autocomplete(),
        "puede_editar_datos_solicitante": puede_editar,
    }


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
        context=contexto_formulario(usuario),
    )


@router.get("/solicitud/{folio}/plantilla")
async def descargar_plantilla_solicitud(
    folio: str,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_usuario_actual),
):
    if not usuario_tiene_rol(usuario, ROLES_SOLICITUDES):
        return RedirectResponse(url="/login", status_code=302)

    solicitud = db.query(Solicitud).filter(Solicitud.folio == folio).first()
    if solicitud is None:
        return RedirectResponse(url="/solicitud", status_code=302)

    contenido = generar_plantilla_solicitud(solicitud)
    nombre_descarga = f"{solicitud.folio}_{NOMBRE_ARCHIVO_SOLICITUD}"
    return Response(
        content=contenido,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nombre_descarga}"'},
    )


@router.post("/solicitud", response_class=HTMLResponse)
async def recibir_formulario(
    request: Request,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_usuario_actual),
    area_solicitante: str = Form(...),
    nombre_usuario: str = Form(...),
    responsable_area_solicitante: str = Form(...),
    telefono: str = Form(TELEFONO_JEFE_MANTENIMIENTO),
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

    nombre_usuario = nombre_usuario.strip()
    responsable_area_solicitante = responsable_area_solicitante.strip()
    telefono = telefono.strip() or TELEFONO_JEFE_MANTENIMIENTO

    if not puede_editar_datos_solicitante(usuario):
        nombre_usuario = str(usuario.get("nombre", "")).strip()
        responsable_area_solicitante = responsable_area_solicitante or nombre_usuario

    try:
        solicitud = crear_solicitud(
            db,
            nombre_usuario=nombre_usuario,
            telefono=telefono,
            responsable_area_solicitante=responsable_area_solicitante,
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
                **contexto_formulario(
                    usuario,
                    nombre_usuario=nombre_usuario,
                    responsable_area_solicitante=responsable_area_solicitante,
                    telefono=telefono,
                    area_solicitante=area_solicitante,
                    subcategoria_servicio=subcategoria_servicio,
                    descripcion_servicio=descripcion_servicio,
                ),
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
            "responsable_area_solicitante": solicitud.responsable_area_solicitante,
            "telefono": solicitud.telefono,
            "area_solicitante": solicitud.area_solicitante,
        },
    )


@router.post("/solicitud/{folio}/confirmar", response_class=HTMLResponse)
async def confirmar_solicitud(
    request: Request,
    folio: str,
    db: Session = Depends(get_db),
    usuario: dict = Depends(get_usuario_actual),
):
    if not usuario_tiene_rol(usuario, ROLES_SOLICITUDES):
        return RedirectResponse(url="/login", status_code=302)

    solicitud = db.query(Solicitud).filter(Solicitud.folio == folio).first()
    if solicitud is None:
        return RedirectResponse(url="/solicitud", status_code=302)

    templates = request.app.state.templates
    try:
        ruta_pdf = guardar_solicitud_pdf(solicitud)
    except ErrorConversionSolicitudPDF as exc:
        return templates.TemplateResponse(
            request=request,
            name="confirmacion.html",
            context={
                "folio": solicitud.folio,
                "fecha": solicitud.fecha.strftime("%d/%m/%Y"),
                "nombre_usuario": solicitud.nombre_usuario,
                "responsable_area_solicitante": solicitud.responsable_area_solicitante,
                "telefono": solicitud.telefono,
                "area_solicitante": solicitud.area_solicitante,
                "error": str(exc),
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        request=request,
        name="confirmacion.html",
        context={
            "folio": solicitud.folio,
            "fecha": solicitud.fecha.strftime("%d/%m/%Y"),
            "nombre_usuario": solicitud.nombre_usuario,
            "responsable_area_solicitante": solicitud.responsable_area_solicitante,
            "telefono": solicitud.telefono,
            "area_solicitante": solicitud.area_solicitante,
            "mensaje_exito": "Solicitud confirmada y guardada como PDF.",
            "url_pdf": f"/solicitudes/{ruta_pdf.name}",
        },
    )


@router.get("/solicitudes", response_class=HTMLResponse)
async def solicitudes_guardadas(
    request: Request,
    usuario: dict = Depends(get_usuario_actual),
):
    if not usuario_tiene_rol(usuario, ROLES_SOLICITUDES):
        return RedirectResponse(url="/login", status_code=302)

    templates = request.app.state.templates
    archivos = [
        {"nombre": ruta.name, "url": f"/solicitudes/{ruta.name}"}
        for ruta in listar_solicitudes_pdf()
    ]
    return templates.TemplateResponse(
        request=request,
        name="solicitudes_guardadas.html",
        context={"archivos": archivos},
    )


@router.get("/solicitudes/{nombre_archivo}")
async def descargar_solicitud_guardada(
    nombre_archivo: str,
    usuario: dict = Depends(get_usuario_actual),
):
    if not usuario_tiene_rol(usuario, ROLES_SOLICITUDES):
        return RedirectResponse(url="/login", status_code=302)

    ruta = CARPETA_SOLICITUDES / nombre_archivo
    if ruta.name != nombre_archivo or ruta.suffix.lower() != ".pdf" or not ruta.exists():
        return RedirectResponse(url="/solicitudes", status_code=302)

    return FileResponse(
        ruta,
        media_type="application/pdf",
        filename=nombre_archivo,
        headers={"Content-Disposition": f'inline; filename="{nombre_archivo}"'},
    )
