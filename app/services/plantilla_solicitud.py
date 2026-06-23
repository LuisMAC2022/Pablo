"""Generación de copias llenas de la plantilla de solicitud única.

Estrategia en dos fases:

1. openpyxl abre la plantilla y escribe los valores de la solicitud. openpyxl
   entiende el formato XLSX, así que el archivo nunca queda "ilegible" como
   ocurría al reescribir el XML a mano.

2. Restauración de dibujos. openpyxl reconstruye los dibujos (logo e imágenes)
   a su manera: usa el namespace de dibujo sin el prefijo `xdr:` que Excel
   espera, renombra `image2.jpg` a `.jpeg` y descarta autoformas/líneas. El
   resultado abre, pero Excel NO muestra las imágenes. Para evitarlo, después de
   guardar se reinyectan tal cual, desde la plantilla original, las piezas de
   `xl/drawings/` y `xl/media/`, junto con la relación de la hoja hacia el
   dibujo y la declaración de tipos de imagen. Así las imágenes se conservan
   idénticas al original.
"""

import zipfile
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

# Nombre de la hoja dentro de la plantilla. Si se renombra la hoja en Excel,
# actualizar este valor (o usar libro.active).
NOMBRE_HOJA = "SOL_UNICA"

# Piezas internas del XLSX que contienen los dibujos e imágenes. Se restauran
# desde la plantilla original tras guardar con openpyxl.
PREFIJOS_PIEZAS_DIBUJO: Tuple[str, ...] = ("xl/drawings/", "xl/media/")
RUTA_RELS_HOJA = "xl/worksheets/_rels/sheet1.xml.rels"
RUTA_CONTENT_TYPES = "[Content_Types].xml"

# Tipo MIME por extensión de imagen, para declarar en [Content_Types].xml las
# extensiones que use la plantilla original (Excel lo exige).
TIPOS_CONTENIDO_IMAGEN: Dict[str, str] = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "emf": "image/x-emf",
    "wmf": "image/x-wmf",
    "tiff": "image/tiff",
}

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
    cualquier otra celda del rango lanza error o se pierde. Resolver la ancla
    aquí mantiene el código correcto aunque a futuro se combinen más celdas.
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
        # resuelve la ancla automáticamente, así que "B37" o "B38" terminan
        # escribiendo en B37. Se deja "B37" por claridad.
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


def _restaurar_dibujos(xlsx_generado: bytes) -> bytes:
    """Reinyecta los dibujos e imágenes de la plantilla original en el archivo
    generado por openpyxl, para que Excel los muestre correctamente."""
    with zipfile.ZipFile(RUTA_PLANTILLA_SOLICITUD, "r") as original:
        piezas_originales = {
            nombre: original.read(nombre)
            for nombre in original.namelist()
            if nombre.startswith(PREFIJOS_PIEZAS_DIBUJO)
        }
        try:
            rels_hoja_original = original.read(RUTA_RELS_HOJA)
        except KeyError:
            rels_hoja_original = None

    # Si la plantilla no tiene dibujos, no hay nada que restaurar.
    if not piezas_originales:
        return xlsx_generado

    extensiones_imagen = {
        nombre.rsplit(".", 1)[1].lower()
        for nombre in piezas_originales
        if nombre.startswith("xl/media/") and "." in nombre
    }

    with zipfile.ZipFile(BytesIO(xlsx_generado), "r") as generado:
        nombres_a_descartar = {
            nombre
            for nombre in generado.namelist()
            if nombre.startswith(PREFIJOS_PIEZAS_DIBUJO)
        }

        content_types = generado.read(RUTA_CONTENT_TYPES).decode("utf-8")
        for extension in extensiones_imagen:
            if f'Extension="{extension}"' not in content_types:
                declaracion = (
                    f'<Default Extension="{extension}" '
                    f'ContentType="{TIPOS_CONTENIDO_IMAGEN.get(extension, "application/octet-stream")}"/>'
                )
                content_types = content_types.replace("</Types>", declaracion + "</Types>")

        salida = BytesIO()
        with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as resultado:
            for item in generado.infolist():
                nombre = item.filename
                if nombre in nombres_a_descartar:
                    continue
                if nombre == RUTA_RELS_HOJA and rels_hoja_original is not None:
                    resultado.writestr(nombre, rels_hoja_original)
                    continue
                if nombre == RUTA_CONTENT_TYPES:
                    resultado.writestr(nombre, content_types)
                    continue
                resultado.writestr(item, generado.read(nombre))

            # La relación de la hoja hacia el dibujo puede no existir en el
            # archivo de openpyxl si éste la nombró distinto; garantizarla.
            if rels_hoja_original is not None and RUTA_RELS_HOJA not in generado.namelist():
                resultado.writestr(RUTA_RELS_HOJA, rels_hoja_original)

            for nombre, datos in piezas_originales.items():
                resultado.writestr(nombre, datos)

    return salida.getvalue()


def generar_plantilla_solicitud(solicitud: Solicitud) -> bytes:
    """Devuelve una copia XLSX de la plantilla llena con los datos de la solicitud."""
    libro = load_workbook(RUTA_PLANTILLA_SOLICITUD)
    hoja = libro[NOMBRE_HOJA]

    for referencia, valor in _valores_solicitud(solicitud).items():
        if valor is None:
            continue
        _asignar_valor_celda(hoja, referencia, valor)

    buffer = BytesIO()
    libro.save(buffer)
    return _restaurar_dibujos(buffer.getvalue())