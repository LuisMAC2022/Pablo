from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models import Solicitud

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


AREAS = [
    "Mantenimiento y Protección Civil",
    "Seguridad",
    "Servicios Educativos",
    "Servicios de Apoyo",
    "Exposiciones Museográficas",
    "Delegación Administrativa",
]


def generar_folio(db: Session) -> str:
    total = db.query(Solicitud).count()
    return str(total + 1).zfill(3)


@app.get("/solicitud", response_class=HTMLResponse)
async def mostrar_formulario(request: Request):
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
    nombre_usuario: str = Form(...),
    telefono: str = Form(...),
    area_solicitante: str = Form(...),
    descripcion_servicio: str = Form(...),
    infraestructura: Optional[List[str]] = Form(None),
    equipo_parque_vehicular: Optional[List[str]] = Form(None),
):
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

    return templates.TemplateResponse(
        request=request,
        name="confirmacion.html",
        context={
            "folio": folio,
            "fecha": fecha.strftime("%d/%m/%Y"),
            "nombre_usuario": nombre_usuario,
            "area_solicitante": area_solicitante,
        },
    )
