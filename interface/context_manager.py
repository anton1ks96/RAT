class ContextManager:
    def __init__(self, max_messages=5):
        self.user_contexts = {}
        self.max_messages = max_messages

    def append_message(self, user_id, role, content):
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = []
        self.user_contexts[user_id].append({"role": role, "content": content})
        self.user_contexts[user_id] = self.user_contexts[user_id][-self.max_messages:]

    def get_context(self, user_id, system_prompt):
        messages = self.user_contexts.get(user_id, [])
        return [{"role": "system", "content": system_prompt}] + messages

    def clear_expired_contexts(self):
        pass

    def clear_user_context(self, user_id):
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]
