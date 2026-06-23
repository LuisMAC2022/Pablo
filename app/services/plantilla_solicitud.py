"""Generación de copias llenas de la plantilla de solicitud única.

Esta versión usa openpyxl en lugar de manipular el XML a mano. openpyxl
entiende el formato XLSX, por lo que conserva por sí mismo los dibujos
(el logo), las imágenes, las relaciones y las celdas combinadas. Eso elimina
la clase de errores de "archivo ilegible" que aparecían al reescribir el XML
con la librería estándar.
"""

from copy import copy
from io import BytesIO
from pathlib import Path
from typing import Dict, Iterable, Tuple, Union

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, range_boundaries
from openpyxl.utils.cell import coordinate_to_tuple
from openpyxl.worksheet.worksheet import Worksheet

from app.models import Solicitud

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_PLANTILLA_SOLICITUD = RAIZ_PROYECTO / "plantilla_solicitud_unica_servicios_pabellon.xlsx"

MARCA_OPCION = "X"
NOMBRE_ARCHIVO_SOLICITUD = "plantilla_solicitud_unica_de_servicios.xlsx"

# Nombre de la hoja dentro de la plantilla. Si algún día se renombra la hoja en
# Excel, hay que actualizar este valor (o usar wb.active).
NOMBRE_HOJA = "SOL_UNICA"

# Las marcas se colocan en la celda indicada para cada opción seleccionada.
CELDAS_OPCIONES_SERVICIO: Dict[str, Dict[str, str]] = {
    "infraestructura": {
        "albanileria": "F17",
        "carpinteria": "F19",
        "electricidad": "F21",
        "herreria": "F23",
        "pintura": "K17",
        "plomeria": "K19",
        "otro": "K21",
    },
    "equipo_parque_vehicular": {
        "mecanica": "R17",
        "refrigeracion": "R19",
        "aire_acondicionado": "R21",
        "equipo_computo": "R23",
        "reparacion_equipo": "X17",
        "planta_luz": "X19",
        "otro": "X21",
    },
    "seguridad": {
        "vigilancia_eventos": "AE17",
        "control_accesos": "AE20",
        "otro": "AE23",
    },
    "transporte": {
        "local": "F28",
        "foraneo": "F30",
        "pasajeros": "F32",
        "carga": "F34",
    },
    "prestamo_de": {
        "salas_aulas": "N30",
        "auditorio": "N32",
        "equipo_audiovisual": "N34",
    },
    "diversos_limpieza": {
        "cafeteria": "R28",
        "cerrajeria": "R30",
        "limpieza": "R32",
        "otro": "R34",
    },
    "correspondencia_paqueteria": {
        "propio": "X30",
        "correo_ordinario": "X32",
        "mensajeria_especializada": "X34",
    },
    "reproduccion_engargolado": {
        "reproduccion": "AE30",
        "engargolado": "AE32",
        "otro": "AE34",
    },
}

CAMPOS_OPCIONES: Tuple[str, ...] = tuple(CELDAS_OPCIONES_SERVICIO.keys())
ValorCelda = Union[int, str]


def _opciones_seleccionadas(solicitud: Solicitud, campo: str) -> Iterable[str]:
    return getattr(solicitud, campo) or []


def _resolver_celda_ancla(hoja: Worksheet, referencia: str) -> str:
    """Devuelve la celda superior-izquierda del rango combinado que contiene
    `referencia`. Si la celda no está combinada, devuelve la misma referencia.

    En un rango combinado solo la celda ancla guarda el valor; escribir en
    cualquier otra celda del rango lanza un error o se pierde. Resolver la
    ancla aquí evita ese problema aunque a futuro se combinen más celdas en la
    plantilla.
    """
    fila, columna = coordinate_to_tuple(referencia)
    for rango in hoja.merged_cells.ranges:
        min_col, min_fila, max_col, max_fila = range_boundaries(str(rango))
        if min_fila <= fila <= max_fila and min_col <= columna <= max_col:
            return f"{get_column_letter(min_col)}{min_fila}"
    return referencia


def _asignar_valor_celda(hoja: Worksheet, referencia: str, valor: ValorCelda) -> None:
    """Escribe `valor` en la celda, resolviendo la ancla si está combinada y
    conservando el formato (fuente, bordes, relleno) que ya tenía la celda."""
    ancla = _resolver_celda_ancla(hoja, referencia)
    celda = hoja[ancla]
    estilo_previo = copy(celda._style)
    celda.value = valor
    celda._style = estilo_previo


def _valores_solicitud(solicitud: Solicitud) -> Dict[str, ValorCelda]:
    valores: Dict[str, ValorCelda] = {
        "H7": solicitud.area_solicitante,
        "AC7": solicitud.folio,
        "L9": solicitud.nombre_usuario,
        "AD9": solicitud.fecha.day,
        "AE9": solicitud.fecha.month,
        "AF9": solicitud.fecha.year,
        "I11": solicitud.responsable_area_solicitante or solicitud.nombre_usuario,
        "AC11": solicitud.telefono,
        # La descripción cae en el bloque combinado B37:AF41; _asignar_valor_celda
        # resuelve la ancla automáticamente, así que tanto "B37" como "B38"
        # terminan escribiendo en B37. Se deja "B37" por claridad.
        "B37": solicitud.descripcion_servicio,
        "U56": solicitud.nombre_usuario,
    }

    for campo in CAMPOS_OPCIONES:
        celdas_por_opcion = CELDAS_OPCIONES_SERVICIO[campo]
        for opcion in _opciones_seleccionadas(solicitud, campo):
            celda = celdas_por_opcion.get(opcion)
            if celda:
                valores[celda] = MARCA_OPCION

    return valores


def generar_plantilla_solicitud(solicitud: Solicitud) -> bytes:
    """Devuelve una copia XLSX de la plantilla llena con los datos de la solicitud."""
    libro = load_workbook(RUTA_PLANTILLA_SOLICITUD)
    hoja = libro[NOMBRE_HOJA]

    for referencia, valor in _valores_solicitud(solicitud).items():
        if valor is None:
            continue
        _asignar_valor_celda(hoja, referencia, valor)

    salida = BytesIO()
    libro.save(salida)
    return salida.getvalue()