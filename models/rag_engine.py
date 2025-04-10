import openai
import requests
from openai import OpenAI
from config import MODEL_PROVIDER, OPENAI_API_KEY, OLLAMA_MODEL, NOVITA_API_KEY, NOVITA_MODEL

NOVITA_BASE_URL = "https://api.novita.ai/v3/openai"

class RAGEngine:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        if MODEL_PROVIDER == 'openAI':
            openai.api_key = OPENAI_API_KEY
        elif MODEL_PROVIDER == 'novita':
            self.client = OpenAI(
                api_key=NOVITA_API_KEY,
                base_url=NOVITA_BASE_URL
            )

    def query(self, user_input):
        prompt = self.system_prompt + "\n" + user_input
        if MODEL_PROVIDER == 'openAI':
            return self.query_openai(prompt)
        elif MODEL_PROVIDER == 'ollama':
            return self.query_ollama(prompt)
        elif MODEL_PROVIDER == 'novita':
            return self.query_novita(prompt)
        else:
            raise ValueError("Unsupported model provider")

    def query_openai(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message['content']

    def query_ollama(self, prompt):
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.exceptions.RequestException as e:
            return f"Ошибка при обращении к Ollama API: {e}"

    def query_novita(self, prompt):
        response = self.client.chat.completions.create(
            model=NOVITA_MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=512
        )
        return response.choices[0].message.content

    def query_with_messages(self, messages):
        if MODEL_PROVIDER == 'openAI':
            return self.query_openai_with_messages(messages)
        elif MODEL_PROVIDER == 'ollama':
            return self.query_ollama_with_messages(messages)
        elif MODEL_PROVIDER == 'novita':
            return self.query_novita_with_messages(messages)
        else:
            raise ValueError("Unsupported model provider")

    def query_openai_with_messages(self, messages):
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message['content']

    def query_ollama_with_messages(self, messages):
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False
                },
                timeout=150
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.exceptions.RequestException as e:
            return f"Ошибка при обращении к Ollama API: {e}"

    def query_novita_with_messages(self, messages):
        response = self.client.chat.completions.create(
            model=NOVITA_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=512
        )
        return response.choices[0].message.content