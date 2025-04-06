import pytest
from models.rag_engine import RAGEngine
from config import MODEL_PROVIDER, OPENAI_API_KEY

@pytest.fixture(scope='module')
def rag_engine():
    catalog = "Название: Моющее средство, Объем: 5л, Цена: 200₽"
    system_prompt = f"Ты ассистент компании. Данные каталога:\n{catalog}"
    return RAGEngine(system_prompt)

@pytest.mark.skipif(MODEL_PROVIDER != 'openAI', reason="MODEL_PROVIDER не OpenAI")
def test_real_openai_query(rag_engine):
    result = rag_engine.query("Расскажи кратко о моющем средстве из каталога.")

    assert isinstance(result, str)
    assert "моющее средство" in result.lower()
    assert "5 литров" in result.lower() or "5л" in result.lower()

@pytest.mark.skipif(MODEL_PROVIDER != 'openAI', reason="MODEL_PROVIDER не OpenAI")
def test_openai_real_response_quality(rag_engine):
    question = "Сколько стоит моющее средство из каталога?"
    result = rag_engine.query(question)

    assert isinstance(result, str)
    assert "200₽" in result
