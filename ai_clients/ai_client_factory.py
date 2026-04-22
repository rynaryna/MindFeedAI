from .ai_client_abc import AIClientABC
from .claude_client.claude_client import ClaudeClient
from config import ai_client_types


class AIClientFactory:
    _client_types: dict[ai_client_types, AIClientABC] = {
        'claude': ClaudeClient
    }

    @classmethod
    def get_ai_client(cls, client_type: ai_client_types, articles_per_call: int = 5) -> AIClientABC:
        if not (client := cls._client_types.get(client_type.lower())):
            raise ValueError()
        
        return client(articles_per_call=articles_per_call)
