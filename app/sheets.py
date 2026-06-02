import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

SPREADSHEET_ID = "1wdxl0iwjJC6kh5KBt46BsEcan-tK3K0nQCZMElD51cg"

def get_sheet():
    creds = Credentials.from_service_account_file(
        "credentials.json",
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
        solicitud.area_solicitante,
        ", ".join(solicitud.infraestructura or []),
        ", ".join(solicitud.equipo_parque_vehicular or []),
        solicitud.descripcion_servicio,
    ])
