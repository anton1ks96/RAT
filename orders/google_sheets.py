import gspread
import os
from google.oauth2.service_account import Credentials

from config import SPREADSHEET_ID, CREDS_FILE

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDS_FILE = os.path.join(os.path.dirname(__file__), "..", CREDS_FILE)
SPREADSHEET_ID = SPREADSHEET_ID

def save_to_google_sheets(data: dict) -> None:
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1

    row = [
        data.get("Имя/Организация", ""),
        data.get("Задача покупки", ""),
        data.get("Город", ""),
        data.get("Контакты", ""),
        data.get("Периодичность закупок", "")
    ]

    if "Товар" in data or "Объём" in data or "Цена" in data:
        row.extend([
            data.get("Товар", ""),
            data.get("Объём", ""),
            data.get("Цена", "")
        ])
    else:
        row.append(data.get("Чек/Товар", ""))

    sheet.append_row(row)
