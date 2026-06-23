from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies import get_usuario_actual
from app.permissions import ROLES_VISITANTES, usuario_tiene_rol
from app.visitantes import registrar_visitantes


router = APIRouter()


@router.get("/visitantes", response_class=HTMLResponse)
async def mostrar_visitantes(
    request: Request,
    usuario: dict = Depends(get_usuario_actual),
):
    if not usuario_tiene_rol(usuario, ROLES_VISITANTES):
        return RedirectResponse(url="/login", status_code=302)

    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="visitantes.html",
        context={"usuario": usuario},
    )


@router.post("/visitantes", response_class=HTMLResponse)
async def recibir_visitantes(
    request: Request,
    usuario: dict = Depends(get_usuario_actual),
    cantidad: int = Form(...),
):
    if not usuario_tiene_rol(usuario, ROLES_VISITANTES):
        return RedirectResponse(url="/login", status_code=302)

    templates = request.app.state.templates

    if cantidad <= 0:
        return templates.TemplateResponse(
            request=request,
            name="visitantes.html",
            context={
                "error": "La cantidad de visitantes debe ser mayor que cero.",
                "usuario": usuario,
            },
            status_code=400,
        )

    registrar_visitantes(cantidad)

    return templates.TemplateResponse(
        request=request,
        name="visitantes_confirmacion.html",
        context={
            "cantidad": cantidad,
            "usuario": usuario,
        },
    )
