import gspread
from google.oauth2.service_account import Credentials

from app.config import get_settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

SPREADSHEET_ID = "1wdxl0iwjJC6kh5KBt46BsEcan-tK3K0nQCZMElD51cg"

def get_sheet():
    creds = Credentials.from_service_account_file(
        str(get_settings().google_credentials_path),
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    return spreadsheet.sheet1

def agregar_solicitud(solicitud):
    sheet = get_sheet()
    sheet.append_row([
        solicitud.folio,
        solicitud.fecha.strftime("%d/%m/%Y"),
        solicitud.nombre_usuario,
        solicitud.telefono,
        solicitud.responsable_area_solicitante or "",
        solicitud.area_solicitante,
        ", ".join(solicitud.infraestructura or []),
        ", ".join(solicitud.equipo_parque_vehicular or []),
        ", ".join(solicitud.seguridad or []),
        ", ".join(solicitud.transporte or []),
        ", ".join(solicitud.diversos_limpieza or []),
        ", ".join(solicitud.prestamo_de or []),
        ", ".join(solicitud.correspondencia_paqueteria or []),
        ", ".join(solicitud.reproduccion_engargolado or []),
        solicitud.descripcion_servicio,
    ])
