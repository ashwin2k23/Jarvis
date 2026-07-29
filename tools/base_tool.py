from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """Abstract base class for all Jarvis tools and plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name for the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description explaining what the tool does."""
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> str:
        """Executes the tool logic with given parameters."""
        pass
