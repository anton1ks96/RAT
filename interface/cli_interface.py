from models.rag_engine import RAGEngine
from data.catalog_loader import load_catalog, format_catalog
from prompts.system_prompt import SYSTEM_PROMPT


def run_cli():
    catalog = load_catalog()
    catalog_info = format_catalog(catalog)
    system_prompt = SYSTEM_PROMPT.format(catalog_info=catalog_info)
    engine = RAGEngine(system_prompt)

    print("exit/quit для выхода.")
    while True:
        user_input = input("Ввод запроса: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        response = engine.query(user_input)
        print("Ответ:")
        print(response)
