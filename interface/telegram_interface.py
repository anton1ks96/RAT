import logging
import json
import asyncio
import re
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


def _extract_json_objects(text: str):
    
    objects = []
    brace_stack = []
    start = None
    for idx, ch in enumerate(text):
        if ch == '{':
            if not brace_stack:
                start = idx
            brace_stack.append(ch)
        elif ch == '}':
            if brace_stack:
                brace_stack.pop()
                if not brace_stack and start is not None:
                    snippet = text[start:idx + 1]
                    try:
                        obj = json.loads(snippet)
                        objects.append(obj)
                    except json.JSONDecodeError:
                        pass
    return objects


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

context_manager = ContextManager(max_messages=20, ttl_minutes=120)
active_orders = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я готов помочь вам сделать заказ.\nПросто напишите, что вам нужно.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text.strip()

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
                await update.message.reply_text("Ваша заявка была собрана и отправлена!")
            except Exception as e:
                logging.exception(e)
                await update.message.reply_text("Не удалось сохранить заявку. Попробуйте позже.")
            finally:
                active_orders.pop(user_id, None)
        else:
            await update.message.reply_text(funnel.get_next_question())
        return

    status_message = await update.message.reply_text(STATUS_MESSAGES[0])

    async def update_status():
        i = 1
        try:
            while True:
                await asyncio.sleep(STATUS_UPDATE_INTERVAL)
                await status_message.edit_text(STATUS_MESSAGES[i % len(STATUS_MESSAGES)])
                i += 1
        except asyncio.CancelledError:
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

    intents = _extract_json_objects(response)
    confirm_intents = [obj for obj in intents if isinstance(obj, dict) and obj.get("intent") == "confirm_purchase"]

    if len(confirm_intents) == 1 and len(intents) == 1:
        parsed = confirm_intents[0]
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

    if intents:
        response = re.sub(r'\{.*?\}', '', response, flags=re.DOTALL).strip()

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