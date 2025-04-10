import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from models.rag_engine import RAGEngine
from data.catalog_loader import load_catalog, format_catalog
from prompts.system_prompt import SYSTEM_PROMPT
from config import TELEGRAM_BOT_TOKEN
from interface.context_manager import ContextManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

context_manager = ContextManager(max_messages=5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправьте ваш запрос.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    catalog = load_catalog()
    catalog_info = format_catalog(catalog)
    system_prompt = SYSTEM_PROMPT.format(catalog_info=catalog_info)

    user_id = update.effective_user.id
    user_input = update.message.text

    context_manager.append_message(user_id, "user", user_input)
    messages = context_manager.get_context(user_id, system_prompt)

    engine = RAGEngine(system_prompt)
    response = engine.query_with_messages(messages)

    context_manager.append_message(user_id, "assistant", response)
    context_manager.clear_expired_contexts()

    await update.message.reply_text(response)

def run_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
