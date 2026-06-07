from datetime import date
from typing import List, Optional

from fastapi import Cookie, Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import crear_token, verificar_password, verificar_token
from app.config import get_settings
from app.database import get_db
from app.models import Solicitud, Usuario
from app.sheets import agregar_solicitud
from app.visitantes import registrar_visitantes


settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)
templates = Jinja2Templates(directory="app/templates")


AREAS = [
    "Mantenimiento y Protección Civil",
    "Seguridad",
    "Servicios Educativos",
    "Servicios de Apoyo",
    "Exposiciones Museográficas",
    "Delegación Administrativa",
]


ROLES_SOLICITUDES = {"biologo", "admin", "desarrollador"}
ROLES_VISITANTES = {"seguridad", "admin", "desarrollador"}


def get_usuario_actual(token: Optional[str] = Cookie(None)):
    if not token:
        return None
    return verificar_token(token)


def usuario_tiene_rol(usuario: Optional[dict], roles_permitidos: set[str]) -> bool:
    return bool(usuario and usuario.get("rol") in roles_permitidos)


def generar_folio(db: Session) -> str:
    total = db.query(Solicitud).count()
    return str(total + 1).zfill(3)


# --- RUTA RAÍZ ---

@app.get("/")
async def raiz():
    return RedirectResponse(url="/inicio", status_code=302)


# --- LOGIN ---

@app.get("/login", response_class=HTMLResponse)
async def mostrar_login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None,
        },
    )


@app.post("/login")
async def recibir_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario or not verificar_password(password, usuario.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Correo o contraseña incorrectos.",
            },
            status_code=400,
        )

    token = crear_token(
        {
            "sub": usuario.email,
            "rol": usuario.rol,
            "nombre": usuario.nombre,
        }
    )

    response = RedirectResponse(url="/inicio", status_code=302)
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        samesite="lax",
    )
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("token")
    return response


# --- INICIO ---

@app.get("/inicio", response_class=HTMLResponse)
async def inicio(request: Request, usuario: dict = Depends(get_usuario_actual)):
    if not usuario:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="inicio.html",
        context={
            "usuario": usuario,
        },
    )


# --- SOLICITUDES ---

@app.get("/solicitud", response_class=HTMLResponse)
async def mostrar_formulario(
    request: Request,
    usuario: dict = Depends(get_usuario_actual),
):
    if not usuario_tiene_rol(usuario, ROLES_SOLICITUDES):
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="form.html",
        context={
            "areas": AREAS,
        },
    )


@app.post("/solicitud", response_class=HTMLResponse)
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

    if area_solicitante not in AREAS:
        return templates.TemplateResponse(
            request=request,
            name="form.html",
            context={
                "areas": AREAS,
                "error": "Área solicitante inválida.",
            },
            status_code=400,
        )

    folio = generar_folio(db)
    fecha = date.today()

    solicitud = Solicitud(
        folio=folio,
        fecha=fecha,
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


# --- VISITANTES ---

@app.get("/visitantes", response_class=HTMLResponse)
async def mostrar_visitantes(
    request: Request,
    usuario: dict = Depends(get_usuario_actual),
):
    if not usuario_tiene_rol(usuario, ROLES_VISITANTES):
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="visitantes.html",
        context={},
    )


@app.post("/visitantes", response_class=HTMLResponse)
async def recibir_visitantes(
    request: Request,
    usuario: dict = Depends(get_usuario_actual),
    cantidad: int = Form(...),
):
    if not usuario_tiene_rol(usuario, ROLES_VISITANTES):
        return RedirectResponse(url="/login", status_code=302)

    if cantidad <= 0:
        return templates.TemplateResponse(
            request=request,
            name="visitantes.html",
            context={
                "error": "La cantidad de visitantes debe ser mayor que cero.",
            },
            status_code=400,
        )

    registrar_visitantes(cantidad)

    return templates.TemplateResponse(
        request=request,
        name="visitantes_confirmacion.html",
        context={
            "cantidad": cantidad,
        },
    )
