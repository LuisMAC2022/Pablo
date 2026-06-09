"""Generación de copias llenas de la plantilla de solicitud única."""

from io import BytesIO
from pathlib import Path
from typing import Dict, Iterable, Tuple, Union
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from app.models import Solicitud

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_PLANTILLA_SOLICITUD = RAIZ_PROYECTO / "plantilla_solicitud_unica_servicios_pabellon.xlsx"

MARCA_OPCION = "X"
NOMBRE_ARCHIVO_SOLICITUD = "plantilla_solicitud_unica_de_servicios.xlsx"

ESPACIO_NOMBRES_HOJA = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
ET.register_namespace("", ESPACIO_NOMBRES_HOJA)

# La marca se coloca en la celda a la derecha del texto de la opción, no antes.
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


def _nombre_etiqueta(nombre: str) -> str:
    return f"{{{ESPACIO_NOMBRES_HOJA}}}{nombre}"


def _dividir_referencia_celda(referencia: str) -> Tuple[str, int]:
    columna = "".join(caracter for caracter in referencia if caracter.isalpha())
    fila = int("".join(caracter for caracter in referencia if caracter.isdigit()))
    return columna, fila


def _indice_columna(columna: str) -> int:
    indice = 0
    for caracter in columna:
        indice = indice * 26 + ord(caracter.upper()) - ord("A") + 1
    return indice


def _orden_celda(celda: ET.Element) -> Tuple[int, int]:
    columna, fila = _dividir_referencia_celda(celda.attrib["r"])
    return fila, _indice_columna(columna)


def _obtener_o_crear_fila(sheet_data: ET.Element, numero_fila: int) -> ET.Element:
    for fila in sheet_data.findall(_nombre_etiqueta("row")):
        if int(fila.attrib["r"]) == numero_fila:
            return fila

    fila = ET.Element(_nombre_etiqueta("row"), {"r": str(numero_fila)})
    sheet_data.append(fila)
    sheet_data[:] = sorted(sheet_data, key=lambda elemento: int(elemento.attrib["r"]))
    return fila


def _obtener_o_crear_celda(hoja: ET.Element, referencia: str) -> ET.Element:
    sheet_data = hoja.find(_nombre_etiqueta("sheetData"))
    if sheet_data is None:
        sheet_data = ET.SubElement(hoja, _nombre_etiqueta("sheetData"))

    columna, numero_fila = _dividir_referencia_celda(referencia)
    fila = _obtener_o_crear_fila(sheet_data, numero_fila)

    for celda in fila.findall(_nombre_etiqueta("c")):
        if celda.attrib["r"] == referencia:
            return celda

    celda = ET.Element(_nombre_etiqueta("c"), {"r": referencia})
    fila.append(celda)
    fila[:] = sorted(fila, key=_orden_celda)
    return celda


def _asignar_valor_celda(hoja: ET.Element, referencia: str, valor: ValorCelda) -> None:
    celda = _obtener_o_crear_celda(hoja, referencia)
    for hijo in list(celda):
        celda.remove(hijo)

    if isinstance(valor, int):
        celda.attrib.pop("t", None)
        ET.SubElement(celda, _nombre_etiqueta("v")).text = str(valor)
        return

    celda.attrib["t"] = "inlineStr"
    texto_en_linea = ET.SubElement(celda, _nombre_etiqueta("is"))
    texto = ET.SubElement(texto_en_linea, _nombre_etiqueta("t"))
    texto.text = valor


def _valores_solicitud(solicitud: Solicitud) -> Dict[str, ValorCelda]:
    valores: Dict[str, ValorCelda] = {
        "H7": solicitud.area_solicitante,
        "AC7": solicitud.folio,
        "L9": solicitud.nombre_usuario,
        "AD9": solicitud.fecha.day,
        "AE9": solicitud.fecha.month,
        "AF9": solicitud.fecha.year,
        "I11": solicitud.nombre_usuario,
        "AC11": solicitud.telefono,
        "B38": solicitud.descripcion_servicio,
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
    with ZipFile(RUTA_PLANTILLA_SOLICITUD, "r") as plantilla:
        hoja = ET.fromstring(plantilla.read("xl/worksheets/sheet1.xml"))

        for referencia, valor in _valores_solicitud(solicitud).items():
            _asignar_valor_celda(hoja, referencia, valor)

        hoja_serializada = ET.tostring(hoja, encoding="utf-8", xml_declaration=True)
        salida = BytesIO()
        with ZipFile(salida, "w", ZIP_DEFLATED) as copia:
            for elemento in plantilla.infolist():
                contenido = hoja_serializada if elemento.filename == "xl/worksheets/sheet1.xml" else plantilla.read(elemento.filename)
                copia.writestr(elemento, contenido)

    return salida.getvalue()
