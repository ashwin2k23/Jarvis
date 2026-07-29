"""
agents/planner.py — Multi-Agent Orchestrator
Routes user requests to the appropriate specialist agent or subsystem.
Phases 2, 5, 6, 7, 8, 9 routing added.
"""
from typing import Dict, Any, Tuple
from agents.specialists import ResearcherSpecialist, AutomationSpecialist, CoderSpecialist


class AgentPlanner:
    """Multi-Agent Orchestrator (User → Planner → Specialist Agent → LLM Synthesis → Response)."""

    def __init__(self, search_engine, os_control):
        self.researcher = ResearcherSpecialist(search_engine)
        self.automation = AutomationSpecialist(os_control)
        self.coder = CoderSpecialist()
        # Extended subsystems set externally by core
        self.skill_registry = None
        self.rag_retriever = None
        self.task_executor = None
        self.vision_camera = None
        self.vision_screen = None
        self.memory_manager = None

    def route_request(self, user_input: str) -> Tuple[str, str]:
        """
        Analyzes user intent and returns (agent_name, agent_output_or_context).
        Routing priority: Skills > Vision > RAG > Automation > Research > Coding > Memory > General
        Supports full typo tolerance across all triggers and commands.
        """
        from utils.fuzzy_match import matches_any_fuzzy
        il = user_input.lower()

        # ── Priority 0: Multi-step Agent Mode (Phase 6) ──
        from agents.task_executor import TaskExecutor
        if TaskExecutor.is_multi_step_request(user_input):
            return ("AgentMode", user_input)

        # ── Priority 1: Skills (Phase 7) ──
        if self.skill_registry:
            skill_triggers = [
                "weather", "wether", "temperature", "forecast", "rain",
                "spotify", "spotfy", "play music", "pause music", "skip song", "next song", "previous song",
                "github", "githb", "my repos", "pull requests", "open prs", "github issues", "github notifications",
            ]
            if matches_any_fuzzy(il, skill_triggers):
                return ("SkillAgent", user_input)

        # ── Priority 2: Vision Commands (Phase 3 & 4) ──
        vision_keywords = [
            "what do you see", "what can you see", "describe what you see",
            "read this document", "read this", "describe this image",
            "explain this error", "explain the error on screen",
            "analyze screen", "analyze my screen", "what's on my screen",
            "read code on screen", "detect ui bugs", "what's on screen",
            "look at my screen", "screen analysis",
        ]
        if matches_any_fuzzy(il, vision_keywords):
            return ("VisionAgent", user_input)

        # ── Priority 3: RAG / Local Knowledge (Phase 5) ──
        rag_keywords = [
            "search my files", "search my project", "find in my", "in my codebase",
            "look in my", "search my notes", "search my docs", "where is the",
            "find the function", "where is defined", "in my project",
            "search local", "from my files", "my knowledge base",
            "summarize my pdf", "summarize pdf", "summarize my uploaded pdf",
            "uploaded pdf", "my pdf", "pdf summary", "read my pdf",
            "indexed pdf", "indexed file", "uploaded file", "my uploaded file"
        ]
        if self.rag_retriever and matches_any_fuzzy(il, rag_keywords):
            return ("RAGAgent", user_input)

        # ── Priority 4: Computer Control & Browser Automation (Phase 2) ──
        automation_keywords = [
            "open", "opn", "launch", "lnch", "close", "clse", "kill", "kll", "screenshot", "screnshot",
            "clipboard", "run command", "terminal", "go to", "goto", "navigate", "search youtube",
            "search google", "open browser", "open website", "volume", "mute",
            "unmute", "sound", "louder", "quieter", "turn up", "turn down",
            # Power & Settings (with typo variants)
            "shutdown", "shut down", "shwtdwn", "stdwn", "restart", "reboot", "restrt", "lock screen", "lock pc",
            "sleep mode", "hibernate", "empty recycle", "recycle bin", "downloads",
            "brightness", "brightnes", "night light", "wifi", "wi-fi", "bluetooth", "blutooth",
            "switch monitor", "change display", "record screen", "screen record",
            "system info", "system status", "hardware status", "open folder",
        ]
        if matches_any_fuzzy(il, automation_keywords):
            res = self.automation.process_task(user_input)
            return ("AutomationAgent", res)

        # ── Priority 5: Memory Recall (Phase 1) ──
        if self.memory_manager:
            from memory.memory_manager import MemoryManager
            if MemoryManager.is_recall_query(user_input):
                return ("MemoryAgent", user_input)

        # ── Priority 6: Knowledge Research ──
        research_keywords = [
            "search for", "lookup", "who is", "what is the latest", "news on",
            "find information about", "explain how", "how to", "tell me about",
            "what happened", "current news"
        ]
        if matches_any_fuzzy(il, research_keywords):
            res = self.researcher.process_task(user_input)
            return ("ResearcherAgent", res)

        # ── Priority 7: Coding Tasks (Phase 8) ──
        coding_keywords = [
            "write code", "create function", "debug", "python script", "fix bug",
            "html", "javascript", "git", "commit", "refactor", "unit test",
            "write test", "generate file", "explain code", "fix error",
            "create file", "make a file", "generate docs", "docstring",
            "typescript", "react", "fastapi", "flask", "node", "npm",
        ]
        if matches_any_fuzzy(il, coding_keywords):
            res = self.coder.process_task(user_input)
            return ("CoderAgent", res)

        # ── Default: General Conversation / LLM ──
        return ("CoreAssistant", "")
