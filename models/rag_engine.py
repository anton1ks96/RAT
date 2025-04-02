import openai
import subprocess
from config import MODEL_PROVIDER, OPENAI_API_KEY, OLLAMA_MODEL

class RAGEngine:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        if MODEL_PROVIDER == 'openAI':
            openai.api_key = OPENAI_API_KEY

    def query(self, user_input):
        prompt = self.system_prompt + "\n" + user_input
        if MODEL_PROVIDER == 'openAI':
            return self.query_openai(prompt)
        elif MODEL_PROVIDER == 'ollama':
            return self.query_ollama(prompt)
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
        command = ['ollama', 'run', OLLAMA_MODEL, prompt]
        try:
            result = subprocess.run(command,
                                    capture_output=True,
                                    text=True,
                                    check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return (
                f"Ошибка при вызове ollama:\n"
                f"Команда: {command}\n"
                f"Вывод: {e.output}\n"
                f"Ошибка: {e.stderr}"
            )
