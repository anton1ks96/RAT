import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from models.rag_engine import RAGEngine
from data.catalog_loader import load_catalog, format_catalog
from prompts.system_prompt import SYSTEM_PROMPT
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Отправьте запрос.")


def handle_message(update: Update, context: CallbackContext):
    catalog = load_catalog()
    catalog_info = format_catalog(catalog)
    system_prompt = SYSTEM_PROMPT.format(catalog_info=catalog_info)
    engine = RAGEngine(system_prompt)

    user_input = update.message.text
    response = engine.query(user_input)
    update.message.reply_text(response)


def run_telegram_bot():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    updater.start_polling()
    updater.idle()
