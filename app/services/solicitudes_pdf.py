"""Conversión y almacenamiento de solicitudes en PDF."""

import re
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from app.models import Solicitud
from app.services.plantilla_solicitud import RAIZ_PROYECTO, generar_plantilla_solicitud

CARPETA_SOLICITUDES = RAIZ_PROYECTO / "solicitudes"


class ErrorConversionSolicitudPDF(RuntimeError):
    """Error claro para fallos al convertir una solicitud XLSX a PDF."""


def _nombre_seguro_pdf(folio: str) -> str:
    folio_seguro = re.sub(r"[^A-Za-z0-9_-]+", "_", folio).strip("_")
    if not folio_seguro:
        raise ErrorConversionSolicitudPDF("El folio de la solicitud no permite crear un nombre de archivo seguro.")
    return f"{folio_seguro}_solicitud.pdf"


def _comando_libreoffice() -> str:
    comando = shutil.which("libreoffice") or shutil.which("soffice")
    if comando is None:
        raise ErrorConversionSolicitudPDF(
            "No se encontró LibreOffice en el entorno para convertir la solicitud a PDF."
        )
    return comando


def guardar_solicitud_pdf(solicitud: Solicitud) -> Path:
    """Genera, convierte y guarda la solicitud como PDF de forma idempotente.

    Si ya existe un PDF para el folio de la solicitud, devuelve esa ruta sin
    sobrescribirlo para evitar reemplazos accidentales.
    """
    CARPETA_SOLICITUDES.mkdir(parents=True, exist_ok=True)
    ruta_pdf = CARPETA_SOLICITUDES / _nombre_seguro_pdf(solicitud.folio)
    if ruta_pdf.exists():
        return ruta_pdf

    contenido_xlsx = generar_plantilla_solicitud(solicitud)
    comando = _comando_libreoffice()

    with TemporaryDirectory() as directorio_temporal:
        ruta_temporal = Path(directorio_temporal)
        ruta_xlsx = ruta_temporal / f"{Path(ruta_pdf.stem).name}.xlsx"
        ruta_xlsx.write_bytes(contenido_xlsx)

        resultado = subprocess.run(
            [
                comando,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(ruta_temporal),
                str(ruta_xlsx),
            ],
            capture_output=True,
            check=False,
            text=True,
            timeout=60,
        )

        if resultado.returncode != 0:
            detalle = (resultado.stderr or resultado.stdout or "sin detalle").strip()
            raise ErrorConversionSolicitudPDF(
                f"No se pudo convertir la solicitud {solicitud.folio} a PDF: {detalle}"
            )

        pdf_convertido = ruta_xlsx.with_suffix(".pdf")
        if not pdf_convertido.exists():
            raise ErrorConversionSolicitudPDF(
                f"LibreOffice terminó sin generar el PDF de la solicitud {solicitud.folio}."
            )

        shutil.move(str(pdf_convertido), ruta_pdf)

    return ruta_pdf


def listar_solicitudes_pdf() -> list[Path]:
    """Devuelve los PDF guardados, ordenados por nombre de archivo."""
    CARPETA_SOLICITUDES.mkdir(parents=True, exist_ok=True)
    return sorted(CARPETA_SOLICITUDES.glob("*.pdf"), key=lambda ruta: ruta.name.lower())
