"""Generación de copias llenadas de la plantilla de solicitud única."""

from io import BytesIO
from pathlib import Path
from typing import Dict, Iterable, Optional
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from app.models import Solicitud
from app.services.catalogo_solicitudes import SUBCATEGORIAS_SERVICIO

NAMESPACE_SPREADSHEET = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
ET.register_namespace("", NAMESPACE_SPREADSHEET)

PLANTILLA_SOLICITUD = Path("plantilla_solicitud_unica_servicios_pabellon.xlsx")
MARCA_OPCION = "☒"

CELDAS_OPCIONES_SERVICIO = {
    "infraestructura": {
        "albanileria": "C17",
        "carpinteria": "B19",
        "electricidad": "B21",
        "herreria": "C23",
        "pintura": "H17",
        "plomeria": "H19",
        "otro": "H21",
    },
    "equipo_parque_vehicular": {
        "mecanica": "N17",
        "refrigeracion": "N19",
        "aire_acondicionado": "N21",
        "equipo_computo": "N23",
        "reparacion_equipo": "T17",
        "planta_luz": "T19",
        "otro": "T21",
    },
    "seguridad": {
        "vigilancia_eventos": "AA17",
        "control_accesos": "AA20",
        "otro": "AA23",
    },
    "transporte": {
        "local": "C28",
        "foraneo": "C30",
        "pasajeros": "C32",
        "carga": "C34",
    },
    "diversos_limpieza": {
        "cafeteria": "P28",
        "cerrajeria": "P30",
        "limpieza": "P32",
        "otro": "P34",
    },
    "prestamo_de": {
        "salas_aulas": "I30",
        "auditorio": "I32",
        "equipo_audiovisual": "H34",
    },
    "correspondencia_paqueteria": {
        "propio": "T30",
        "correo_ordinario": "T32",
        "mensajeria_especializada": "T34",
    },
    "reproduccion_engargolado": {
        "reproduccion": "AA30",
        "engargolado": "AA32",
        "otro": "AA34",
    },
}


def generar_archivo_solicitud(solicitud: Solicitud) -> BytesIO:
    """Devuelve una copia XLSX de la plantilla llenada con los datos de la solicitud."""
    libro = BytesIO()

    with ZipFile(PLANTILLA_SOLICITUD, "r") as plantilla, ZipFile(libro, "w", ZIP_DEFLATED) as salida:
        for item in plantilla.infolist():
            contenido = plantilla.read(item.filename)

            if item.filename == "xl/worksheets/sheet1.xml":
                contenido = _llenar_hoja_solicitud(contenido, solicitud)

            salida.writestr(item, contenido)

    libro.seek(0)
    return libro


def _llenar_hoja_solicitud(contenido: bytes, solicitud: Solicitud) -> bytes:
    hoja = ET.fromstring(contenido)
    valores = {
        "H7": solicitud.area_solicitante,
        "AC7": solicitud.folio,
        "L9": solicitud.nombre_usuario,
        "AD9": str(solicitud.fecha.day),
        "AE9": str(solicitud.fecha.month),
        "AF9": str(solicitud.fecha.year),
        "I11": solicitud.nombre_usuario,
        "AC11": solicitud.telefono,
        "B38": solicitud.descripcion_servicio,
        "U56": solicitud.nombre_usuario,
    }

    for celda, valor in valores.items():
        _establecer_texto(hoja, celda, valor)

    for celda, texto in _opciones_seleccionadas(solicitud).items():
        _establecer_texto(hoja, celda, f"{MARCA_OPCION} {texto}")

    return ET.tostring(hoja, encoding="utf-8", xml_declaration=True)


def _opciones_seleccionadas(solicitud: Solicitud) -> Dict[str, str]:
    opciones = {}

    for subcategoria_id, celdas in CELDAS_OPCIONES_SERVICIO.items():
        seleccionadas: Optional[Iterable[str]] = getattr(solicitud, subcategoria_id, None)
        if not seleccionadas:
            continue

        etiquetas = {
            opcion["valor"]: opcion["etiqueta"].upper()
            for opcion in SUBCATEGORIAS_SERVICIO[subcategoria_id]["opciones"]
        }

        for opcion in seleccionadas:
            celda = celdas.get(opcion)
            if celda:
                opciones[celda] = etiquetas[opcion]

    return opciones


def _establecer_texto(hoja: ET.Element, celda: str, texto: str) -> None:
    elemento_celda = hoja.find(f'.//{{{NAMESPACE_SPREADSHEET}}}c[@r="{celda}"]')
    if elemento_celda is None:
        raise ValueError(f"La celda {celda} no existe en la plantilla de solicitud.")

    elemento_celda.set("t", "inlineStr")

    for hijo in list(elemento_celda):
        if hijo.tag in {
            f"{{{NAMESPACE_SPREADSHEET}}}v",
            f"{{{NAMESPACE_SPREADSHEET}}}is",
        }:
            elemento_celda.remove(hijo)

    inline_string = ET.SubElement(elemento_celda, f"{{{NAMESPACE_SPREADSHEET}}}is")
    texto_elemento = ET.SubElement(inline_string, f"{{{NAMESPACE_SPREADSHEET}}}t")
    texto_elemento.text = texto or ""
