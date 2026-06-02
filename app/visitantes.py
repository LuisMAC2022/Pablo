import gspread 
from google.oauth2.service_account import Credentials
from datetime import datetime
import os 
from dotenv import load_dotenv

load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheet_visitantes():
	creds = Credentials.from_service_account_file(
		"credentials.json",
		scopes=SCOPES
	)
	#client = gspread.Client(auth=creds)
	client = gspread.authorize(creds)
	spreadsheet = client.open_by_key(os.getenv("VISITANTES_SHEET_ID"))
	return spreadsheet.sheet1

def registrar_visitantes(cantidad: int):
	sheet = get_sheet_visitantes()
	ahora = datetime.now()
	sheet.append_row([
		ahora.strftime("%d/%m/%Y"),
		ahora.strftime("%H:00"),
		cantidad,
	])