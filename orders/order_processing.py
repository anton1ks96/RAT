from interface.context_manager import ContextManager

QUESTIONS = [
    "Укажите ваше имя или наименование организации:",
    "Под какие задачи планируется приобретение? (Продажа / Использование в личных целях):",
    "В каком городе вы находитесь?:",
    "Пожалуйста, укажите ваши контактные данные:",
    "Какой планируемый чек закупки (если организация) или какой товар вас интересует (если частное лицо):",
    "Какая периодичность закупок? (только для бизнеса, напишите '-' если неактуально):"
]

class OrderProcessing:
    def __init__(self, user_id: int, context_manager: ContextManager):
        self.user_id = user_id
        self.context_manager = context_manager
        self.answers = [None] * len(QUESTIONS)
        self.current_question_index = 0

    def get_next_question(self) -> str | None:
        while self.current_question_index < len(QUESTIONS):
            if self.answers[self.current_question_index] is None:
                return QUESTIONS[self.current_question_index]
            self.current_question_index += 1
        return None

    def record_answer(self, answer: str) -> None:
        if self.current_question_index < len(QUESTIONS):
            self.answers[self.current_question_index] = answer
            self.current_question_index += 1

    def set_predefined_answer(self, question: str, answer: str) -> None:
        keys = [
            "Имя/Организация",
            "Задача покупки",
            "Город",
            "Контакты",
            "Чек/Товар",
            "Периодичность закупок"
        ]
        if question in keys:
            index = keys.index(question)
            self.answers[index] = answer
            if index == self.current_question_index:
                self.current_question_index += 1

    def is_complete(self) -> bool:
        return all(answer is not None for answer in self.answers)

    def summarize_data(self) -> dict:
        keys = [
            "Имя/Организация",
            "Задача покупки",
            "Город",
            "Контакты",
            "Чек/Товар",
            "Периодичность закупок"
        ]
        return dict(zip(keys, self.answers))