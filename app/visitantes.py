import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

from app.config import get_settings


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_sheet_visitantes():
	settings = get_settings()
	creds = Credentials.from_service_account_file(
		str(settings.google_credentials_path),
		scopes=SCOPES
	)
	#client = gspread.Client(auth=creds)
	client = gspread.authorize(creds)
	spreadsheet = client.open_by_key(settings.visitantes_sheet_id)
	return spreadsheet.sheet1


def registrar_visitantes(cantidad: int):
	sheet = get_sheet_visitantes()
	ahora = datetime.now()
	sheet.append_row([
		ahora.strftime("%d/%m/%Y"),
		ahora.strftime("%H:00"),
		cantidad,
	])
