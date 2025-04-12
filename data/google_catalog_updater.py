import json
import gspread
import os
from config import CREDS_FILE, CATALOG_SPREADSHEET_ID
from oauth2client.service_account import ServiceAccountCredentials

CREDS_FILE = os.path.join(os.path.dirname(__file__), "..", CREDS_FILE)

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "..", "catalog.json")

def fetch_catalog_from_gsheet(spreadsheet_id=CATALOG_SPREADSHEET_ID, credentials_path=CREDS_FILE):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets']
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(spreadsheet_id).get_worksheet(0)
    rows = sheet.get_all_values()

    structured = []
    for row in rows:
        if len(row) < 3:
            continue

        item = {
            "name": row[0].strip(),
            "volume": row[1].strip() if len(row) > 1 else "",
            "price": row[2].strip() if len(row) > 2 else "",
            "description": row[3].strip() if len(row) > 3 else ""
        }
        structured.append(item)

    return structured

def save_catalog_to_json(catalog, catalog_path=CATALOG_PATH):
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=4)

def update_catalog_from_google(spreadsheet_id=CATALOG_SPREADSHEET_ID, json_path=CATALOG_PATH, credentials_path=CREDS_FILE):
    catalog_data = fetch_catalog_from_gsheet(spreadsheet_id, credentials_path)
    save_catalog_to_json(catalog_data, json_path)
