import pytest
import os
from dotenv import load_dotenv
from models.rag_engine import RAGEngine
import re

load_dotenv()

@pytest.fixture(scope='session', autouse=True)
def set_model_provider_novita():
    os.environ["MODEL_PROVIDER"] = "novita"
    os.environ["NOVITA_MODEL"] = "google/gemma-3-27b-it"

@pytest.fixture(scope='module')
def catalog():
    return [
        {"name": "Моющее средство для стекол", "volume": "5 л", "price": "178₽"},
        {"name": "Моющее средство для стекол", "volume": "0.5 л", "price": "86₽",
         "description": "Для стеклянных поверхностей и зеркал."},
        {"name": "Автошампунь", "volume": "1 л", "price": "340₽"}
    ]

@pytest.fixture(scope='module')
def rag_engine(catalog):
    from data.catalog_loader import format_catalog
    from prompts.system_prompt import SYSTEM_PROMPT

    catalog_info = format_catalog(catalog)
    system_prompt = SYSTEM_PROMPT.format(catalog_info=catalog_info)
    return RAGEngine(system_prompt)

def test_single_product_response(rag_engine):
    result = rag_engine.query("Автошампунь хочу купить")
    assert "Автошампунь · 1 л · 340₽" in result

def test_multiple_products_formats(rag_engine):
    result = rag_engine.query("Что есть для стекол?")
    assert "1. Моющее средство для стекол · 5 л · 178₽" in result
    assert "2. Моющее средство для стекол · 0.5 л · 86₽" in result

def test_no_unrequested_description_given(rag_engine):
    result = rag_engine.query("Хочу моющее средство для стекол 0.5 л")
    assert "Описание:" not in result

def test_json_response_for_confirmation(rag_engine):
    confirmation_text = "беру автошампунь"
    result = rag_engine.query(confirmation_text)
    json_clean = re.sub(r'```json\n|\n```', '', result).strip()
    assert '"intent": "confirm_purchase"' in json_clean
    assert '"name": "Автошампунь"' in json_clean
    assert '"volume": "1 л"' in json_clean
    assert '"price": "340₽"' in json_clean

def test_decline_unrelated_request(rag_engine):
    unrelated_text = "расскажи про курсы валют"
    result = rag_engine.query(unrelated_text).lower()
    assert "могу помочь только по подбору товаров" in result \
           or "не могу помочь" in result \
           or "не касается продукции" in result \
           or "только с подбором" in result

def test_env_variable_exists():
    assert os.getenv("NOVITA_API_KEY") is not None, "Переменная окружения NOVITA_API_KEY не задана"
