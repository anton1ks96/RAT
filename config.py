import os
from dotenv import load_dotenv

load_dotenv()

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openAI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "default_model")