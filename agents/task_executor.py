"""
agents/task_executor.py — Phase 6: Multi-Step Agent Mode
Breaks complex multi-step user requests into a plan and executes each step
sequentially, returning real-time progress updates.
"""
import re
import json
from typing import List, Dict, Callable, Optional


class TaskExecutor:
    """
    Handles multi-step task planning and execution (Agent Mode).

    Flow:
        1. LLM generates a step-by-step JSON plan from the user's request
        2. Each step is dispatched to the appropriate Jarvis subsystem
        3. Results are collected and returned with a progress log
    """

    STEP_TYPES = {
        "launch": "automation",
        "open": "automation",
        "close": "automation",
        "run_command": "terminal",
        "search": "research",
        "web": "browser",
        "create_file": "filesystem",
        "write_file": "filesystem",
        "git": "terminal",
        "remember": "memory",
        "speak": "tts",
        "wait": "delay",
        "ai": "llm",
    }

    PLAN_PROMPT = """You are a task planning AI. The user wants to accomplish a multi-step task.
Break this into a JSON array of steps. Each step has:
  - "step": short name
  - "type": one of [launch, open, close, run_command, search, web, create_file, git, remember, speak, ai]
  - "params": dict of parameters
  - "description": human-readable description of what this step does

Respond ONLY with valid JSON array. No markdown, no extra text.

User request: {user_request}

Example output format:
[
  {{"step": "open_vscode", "type": "launch", "params": {{"app": "code"}}, "description": "Open VS Code"}},
  {{"step": "run_npm", "type": "run_command", "params": {{"command": "npm install"}}, "description": "Install dependencies"}}
]"""

    def __init__(self, ai_provider=None, core=None):
        self.ai_provider = ai_provider
        self.core = core

    def set_provider(self, ai_provider):
        self.ai_provider = ai_provider

    def set_core(self, core):
        self.core = core

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------

    def parse_plan(self, user_request: str) -> List[Dict]:
        """
        Asks the LLM to create an executable step-by-step plan.
        Returns a list of step dicts, or a fallback single-step plan on error.
        """
        if not self.ai_provider:
            return self._fallback_plan(user_request)

        prompt = self.PLAN_PROMPT.format(user_request=user_request)
        try:
            raw = self.ai_provider.generate_response(
                messages=[{"sender": "User", "content": prompt}],
                system_prompt="You are a task planning assistant. Respond ONLY with valid JSON arrays. No markdown."
            )
            # Strip markdown code fences if present
            raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
            raw = re.sub(r'\s*```$', '', raw.strip())
            steps = json.loads(raw)
            if isinstance(steps, list):
                return steps
        except (json.JSONDecodeError, Exception):
            pass
        return self._fallback_plan(user_request)

    def _fallback_plan(self, user_request: str) -> List[Dict]:
        """Returns a single-step plan that just passes the request to AI."""
        return [{
            "step": "ai_response",
            "type": "ai",
            "params": {"prompt": user_request},
            "description": f"Process: {user_request[:60]}"
        }]

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute_plan(self, steps: List[Dict], progress_callback: Callable = None) -> str:
        """
        Executes all steps in sequence.

        Args:
            steps: List of step dicts from parse_plan()
            progress_callback: Optional callable(step_num, total, description, result)

        Returns:
            Formatted execution summary.
        """
        if not steps:
            return "No steps to execute."

        total = len(steps)
        results = []

        for i, step in enumerate(steps, 1):
            desc = step.get("description", step.get("step", f"Step {i}"))
            step_type = step.get("type", "ai")
            params = step.get("params", {})

            if progress_callback:
                progress_callback(i, total, desc, None)

            try:
                result = self._execute_step(step_type, params, step)
            except Exception as e:
                result = f"❌ Error: {e}"

            if progress_callback:
                progress_callback(i, total, desc, result)

            results.append(f"**Step {i}/{total}** — {desc}\n→ {result}")

        return "\n\n".join(results)

    def _execute_step(self, step_type: str, params: Dict, step: Dict) -> str:
        """Dispatches a single step to the right subsystem."""
        if not self.core:
            return f"[Simulated] Would execute: {step_type} with {params}"

        if step_type in ("launch", "open"):
            app = params.get("app") or params.get("target", "")
            return self.core.automation.launch_app(app) if app else "No app specified."

        elif step_type == "close":
            app = params.get("app") or params.get("target", "")
            return self.core.automation.close_app(app) if app else "No app specified."

        elif step_type == "run_command":
            cmd = params.get("command", "")
            if not cmd:
                return "No command specified."
            return self.core.automation.execute_terminal_command(cmd)

        elif step_type == "search":
            query = params.get("query", "")
            if not query:
                return "No search query specified."
            results = self.core.search.search(query)
            return self.core.search.format_search_results_for_llm(query, results)[:300]

        elif step_type == "web":
            url = params.get("url", params.get("site", ""))
            return self.core.automation.open_website(url) if url else "No URL specified."

        elif step_type in ("create_file", "write_file"):
            path = params.get("path", params.get("filename", ""))
            content = params.get("content", "")
            if not path:
                return "No file path specified."
            try:
                from pathlib import Path
                fpath = Path(path)
                fpath.parent.mkdir(parents=True, exist_ok=True)
                fpath.write_text(content, encoding="utf-8")
                return f"✅ File created: {path}"
            except Exception as e:
                return f"File creation error: {e}"

        elif step_type == "git":
            cmd = params.get("command", "")
            full_cmd = f"git {cmd}" if not cmd.startswith("git") else cmd
            return self.core.automation.execute_terminal_command(full_cmd)

        elif step_type == "remember":
            cat = params.get("category", "general")
            key = params.get("key", "note")
            value = params.get("value", "")
            if value and hasattr(self.core, "memory_manager"):
                self.core.memory_manager.save_explicit_fact(cat, key, value)
                return f"✅ Remembered: {key} = {value}"
            return "Memory save skipped (no value provided)."

        elif step_type == "speak":
            text = params.get("text", "")
            if text and hasattr(self.core, "tts"):
                self.core.tts.speak(text)
            return f"🔊 Spoke: {text}"

        elif step_type == "ai":
            prompt_text = params.get("prompt", step.get("description", ""))
            if not prompt_text:
                return "No AI prompt specified."
            return self.core.ai_provider.generate_response(
                messages=[{"sender": "User", "content": prompt_text}],
                system_prompt="You are Jarvis. Complete this task step concisely."
            )

        elif step_type == "delay":
            import time
            seconds = int(params.get("seconds", 1))
            time.sleep(min(seconds, 10))  # Cap at 10s
            return f"⏳ Waited {seconds} second(s)."

        return f"Unknown step type: {step_type}"

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    @staticmethod
    def is_multi_step_request(text: str) -> bool:
        """
        Returns True if the user input looks like a multi-step task request.
        """
        multi_step_keywords = [
            " then ", " after that", " and then", " and also", " next ",
            "step by step", "step-by-step", "one by one",
            "first ", "second ", "third ",
            "initialize", "set up", "and open", "and install", "and create",
            "after installing", "once done", "following that"
        ]
        text_lower = text.lower()
        keyword_count = sum(1 for kw in multi_step_keywords if kw in text_lower)
        return keyword_count >= 1 and len(text) > 30
