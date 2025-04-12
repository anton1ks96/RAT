import os
from dotenv import load_dotenv

load_dotenv()

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openAI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDS_FILE = os.getenv("CREDS_FILE")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "default_model")
NOVITA_API_KEY = os.getenv("NOVITA_API_KEY")
NOVITA_MODEL = os.getenv("NOVITA_MODEL")
ALLOWED_THREAD_IDS= os.getenv("ALLOWED_THREAD_IDS")
CATALOG_SPREADSHEET_ID = os.getenv("CATALOG_SPREADSHEET_ID")