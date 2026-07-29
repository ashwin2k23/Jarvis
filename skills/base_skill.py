"""
skills/base_skill.py — Phase 7: Plugin Architecture Base Class
All Jarvis skills/plugins must inherit from BaseSkill.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseSkill(ABC):
    """Abstract base class for all Jarvis skills/plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique skill identifier (lowercase, no spaces)."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description shown in the Tools UI."""
        ...

    @property
    @abstractmethod
    def triggers(self) -> List[str]:
        """Keywords that activate this skill (lowercase)."""
        ...

    @abstractmethod
    def execute(self, user_input: str, core=None) -> str:
        """
        Execute the skill with the given user input.

        Args:
            user_input: The raw user message
            core: JarvisCoreController instance (optional, for access to db, ai, etc.)

        Returns:
            Response string to show to user
        """
        ...

    def matches(self, text: str) -> bool:
        """Returns True if any trigger keyword is found or fuzzy matched in the text."""
        from utils.fuzzy_match import matches_any_fuzzy
        return matches_any_fuzzy(text, self.triggers, threshold=0.70)
