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

folio_counter = 0

AREAS = [
    "Mantenimiento y Protección Civil",
    "Seguridad",
    "Servicios Educativos",
    "Servicios de Apoyo",
    "Exposiciones Museográficas",
    "Delegación Administrativa",
]

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
    nombre_usuario: str = Form(...),
    telefono: str = Form(...),
    area_solicitante: str = Form(...),
    descripcion_servicio: str = Form(...),
    infraestructura: Optional[List[str]] = Form(None),
    equipo_parque_vehicular: Optional[List[str]] = Form(None),
):
    global folio_counter

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

    folio_counter += 1
    folio = str(folio_counter).zfill(3)
    fecha = date.today().strftime("%d/%m/%Y")

    print("--- SOLICITUD RECIBIDA ---")
    print(f"Folio: {folio}")
    print(f"Fecha: {fecha}")
    print(f"Nombre: {nombre_usuario}")
    print(f"Teléfono: {telefono}")
    print(f"Área: {area_solicitante}")
    print(f"Infraestructura: {infraestructura}")
    print(f"Equipo: {equipo_parque_vehicular}")
    print(f"Descripción: {descripcion_servicio}")

    return templates.TemplateResponse(
        request=request,
        name="confirmacion.html",
        context={
            "folio": folio,
            "fecha": fecha,
            "nombre_usuario": nombre_usuario,
            "area_solicitante": area_solicitante,
        },
    )
