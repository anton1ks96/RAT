import time

class ContextManager:
    def __init__(self, max_messages=5, min_interval=2):
        self.user_contexts = {}
        self.last_message_times = {}
        self.max_messages = max_messages
        self.min_interval = min_interval

    def append_message(self, user_id, role, content):
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = []
        self.user_contexts[user_id].append({"role": role, "content": content})
        self.user_contexts[user_id] = self.user_contexts[user_id][-self.max_messages:]
        self.last_message_times[user_id] = time.time()

    def get_context(self, user_id, system_prompt):
        messages = self.user_contexts.get(user_id, [])
        return [{"role": "system", "content": system_prompt}] + messages

    def is_too_frequent(self, user_id):
        last_time = self.last_message_times.get(user_id, 0)
        return time.time() - last_time < self.min_interval

    def clear_expired_contexts(self):
        pass

    def clear_user_context(self, user_id):
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]
        if user_id in self.last_message_times:
            del self.last_message_times[user_id]
