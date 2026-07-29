from typing import List, Dict
from ai.provider_interface import AIProviderInterface

class OpenAIProvider(AIProviderInterface):
    """OpenAI API provider integration."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        if not self.is_available():
            return "Error: OpenAI API Key is missing. Please set your API key in Jarvis Settings."
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            formatted_messages = []
            if system_prompt:
                formatted_messages.append({"role": "system", "content": system_prompt})
            
            for msg in messages:
                role = "assistant" if msg.get("sender") == "Jarvis" else "user"
                formatted_messages.append({"role": role, "content": msg.get("content", "")})

            response = client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[OpenAI Error]: {str(e)}"
