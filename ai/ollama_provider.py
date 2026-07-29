import requests
from typing import List, Dict
from ai.provider_interface import AIProviderInterface

class OllamaProvider(AIProviderInterface):
    """Local Ollama model provider integration."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        if not self.is_available():
            return f"Error: Cannot connect to local Ollama server at {self.base_url}. Make sure Ollama is running."
        try:
            formatted_messages = []
            if system_prompt:
                formatted_messages.append({"role": "system", "content": system_prompt})
            for msg in messages:
                role = "assistant" if msg.get("sender") == "Jarvis" else "user"
                formatted_messages.append({"role": role, "content": msg.get("content", "")})

            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "stream": False
            }
            r = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=60)
            if r.status_code == 200:
                data = r.json()
                return data.get("message", {}).get("content", "").strip()
            else:
                return f"[Ollama Error {r.status_code}]: {r.text}"
        except Exception as e:
            return f"[Ollama Connection Error]: {str(e)}"
