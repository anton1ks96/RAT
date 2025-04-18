import logging
import json
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatAction

from models.rag_engine import RAGEngine
from data.catalog_loader import load_catalog, format_catalog
from data.google_catalog_updater import update_catalog_from_google
from prompts.system_prompt import SYSTEM_PROMPT
from config import TELEGRAM_BOT_TOKEN
from interface.context_manager import ContextManager
from orders import OrderProcessing, save_to_google_sheets

STATUS_UPDATE_INTERVAL = 10
STATUS_MESSAGES = [
    "Запрос обрабатывается. Пожалуйста подождите...",
    "Ответ занимает больше времени, чем обычно. Мы продолжаем обработку.",
    "Ответ почти готов. Спасибо за ожидание."
]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

active_orders = {}
context_manager = ContextManager(max_messages=5, min_interval=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправьте ваш запрос.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text

    if context_manager.is_too_frequent(user_id):
        await update.message.reply_text("Слишком частые запросы. Пожалуйста подождите пару секунд и попробуйте снова.")
        return

    if user_id in active_orders:
        funnel = active_orders[user_id]
        funnel.record_answer(user_input)

        if funnel.is_complete():
            order_data = funnel.summarize_data()
            try:
                save_to_google_sheets(order_data)
                logging.info("Сохранение заявки в google sheets.")
                await update.message.reply_text("Ваша завявка была собрана и отправлена!")
            except Exception as e:
                logging.info(f"Ошибка при сохранении в google sheets: {e}")

            context_manager.clear_user_context(user_id)
            del active_orders[user_id]
        else:
            await update.message.reply_text(funnel.get_next_question())
        return

    status_index = 0
    status_updated = False
    status_message = await update.message.reply_text(STATUS_MESSAGES[status_index])

    async def update_status():
        nonlocal status_index, status_updated
        while status_index < len(STATUS_MESSAGES) - 1:
            await asyncio.sleep(STATUS_UPDATE_INTERVAL)
            status_index += 1
            try:
                await status_message.edit_text(STATUS_MESSAGES[status_index])
                status_updated = True
            except Exception:
                pass

    status_task = asyncio.create_task(update_status())
    await asyncio.sleep(0)

    catalog = load_catalog()
    catalog_info = format_catalog(catalog)
    system_prompt = SYSTEM_PROMPT.format(catalog_info=catalog_info)

    context_manager.append_message(user_id, "user", user_input)
    messages = context_manager.get_context(user_id, system_prompt)

    engine = RAGEngine(system_prompt)
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, engine.query_with_messages, messages)

    status_task.cancel()

    try:
        parsed = json.loads(response)
        print(parsed)
        if parsed.get("intent") == "confirm_purchase":
            product = parsed.get("product", {})
            product_name = product.get("name", "Не указано")
            volume = product.get("volume", "")
            price = product.get("price", "")

            funnel = OrderProcessing(user_id, context_manager)
            funnel.set_predefined_answer("Чек/Товар", f"{product_name} · {volume} · {price}")
            active_orders[user_id] = funnel

            question = funnel.get_next_question()
            try:
                await status_message.edit_text(f"Начинаем оформление вашей заявки.\n{question}")
            except Exception:
                await update.message.reply_text(f"Начинаем оформление вашей заявки.\n{question}")
            return
    except json.JSONDecodeError:
        pass

    try:
        await status_message.edit_text(response)
    except Exception:
        await update.message.reply_text(response)

    context_manager.append_message(user_id, "assistant", response)
    context_manager.clear_expired_contexts()

def run_telegram_bot():
    update_catalog_from_google()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
