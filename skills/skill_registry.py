"""
skills/skill_registry.py — Phase 7: Plugin Registry
Manages all registered skills and routes user input to the appropriate skill.
"""
from typing import Dict, List, Optional
from skills.base_skill import BaseSkill
from skills.weather_skill import WeatherSkill
from skills.spotify_skill import SpotifySkill
from skills.github_skill import GitHubSkill


class SkillRegistry:
    """Central registry for all Jarvis skills/plugins."""

    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._load_default_skills()

    def _load_default_skills(self):
        """Registers all built-in skills."""
        default_skills = [
            WeatherSkill(),
            SpotifySkill(),
            GitHubSkill(),
        ]
        for skill in default_skills:
            self.register(skill)

    def register(self, skill: BaseSkill):
        """Registers a skill by its name."""
        self._skills[skill.name.lower()] = skill

    def unregister(self, skill_name: str):
        """Removes a skill from the registry."""
        self._skills.pop(skill_name.lower(), None)

    def get_skill(self, name: str) -> Optional[BaseSkill]:
        """Returns a skill by exact name."""
        return self._skills.get(name.lower())

    def find_matching_skill(self, user_input: str) -> Optional[BaseSkill]:
        """
        Finds the first skill whose triggers match the user input.
        Returns None if no skill matches.
        """
        for skill in self._skills.values():
            if skill.matches(user_input):
                return skill
        return None

    def list_skills(self) -> List[Dict[str, str]]:
        """Returns metadata for all registered skills."""
        return [
            {
                "name": s.name,
                "description": s.description,
                "triggers": ", ".join(s.triggers[:4])
            }
            for s in self._skills.values()
        ]

    def execute_skill(self, skill_name: str, user_input: str, core=None) -> str:
        """Executes a skill by name."""
        skill = self.get_skill(skill_name)
        if not skill:
            return f"Skill '{skill_name}' is not registered."
        return skill.execute(user_input, core)

    def route_and_execute(self, user_input: str, core=None) -> Optional[str]:
        """
        Automatically routes user input to a matching skill and executes it.
        Returns the skill response, or None if no skill matched.
        """
        skill = self.find_matching_skill(user_input)
        if skill:
            return skill.execute(user_input, core)
        return None
