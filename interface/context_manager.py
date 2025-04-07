import time

class ContextManager:
    def __init__(self, ttl_seconds=120):
        self.user_contexts = {}
        self.ttl = ttl_seconds

    def append_message(self, user_id, role, content):
        now = time.time()
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {'messages': [], 'last_active': now}
        self.user_contexts[user_id]['messages'].append({"role": role, "content": content})
        self.user_contexts[user_id]['last_active'] = now

    def get_context(self, user_id, system_prompt):
        now = time.time()
        context = self.user_contexts.get(user_id)
        if not context or now - context['last_active'] > self.ttl:
            self.user_contexts[user_id] = {'messages': [], 'last_active': now}
            return [{"role": "system", "content": system_prompt}]
        return [{"role": "system", "content": system_prompt}] + context["messages"]

    def clear_expired_contexts(self):
        now = time.time()
        self.user_contexts = {
            user_id: ctx for user_id, ctx in self.user_contexts.items()
            if now - ctx['last_active'] <= self.ttl
        }
