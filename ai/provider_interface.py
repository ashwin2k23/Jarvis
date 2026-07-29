from abc import ABC, abstractmethod
from typing import List, Dict

class AIProviderInterface(ABC):
    """Abstract interface that all LLM providers must implement."""

    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        """Generates a text response from the LLM based on conversation messages."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider is properly configured and reachable."""
        pass
