"""
agents/specialists.py — Multi-Agent Specialist Implementations
Handles automation routing, research queries, and coding assistance.
Phases 2, 4, 6, 8 enhancements included.
"""
from typing import Dict, Any
import re


class BaseSpecialistAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def process_task(self, prompt: str, context: Dict[str, Any] = None) -> str:
        raise NotImplementedError


class ResearcherSpecialist(BaseSpecialistAgent):
    def __init__(self, search_engine):
        super().__init__("ResearcherAgent", "Internet Intelligence & Web Information Gathering")
        self.search_engine = search_engine

    def process_task(self, prompt: str, context: Dict[str, Any] = None) -> str:
        query = prompt.replace("search", "").replace("find", "").replace("research", "").strip()
        results = self.search_engine.search(query if query else prompt)
        return self.search_engine.format_search_results_for_llm(query, results)


class AutomationSpecialist(BaseSpecialistAgent):
    """Routes all OS-level and automation commands to ComputerAutomation methods."""

    def __init__(self, os_control):
        super().__init__("AutomationAgent", "Computer Control & System Operations")
        self.os_control = os_control
        self.web_map = {
            "instagram": "https://www.instagram.com",
            "facebook": "https://www.facebook.com",
            "linkedin": "https://www.linkedin.com",
            "tiktok": "https://www.tiktok.com",
            "whatsapp": "https://web.whatsapp.com",
            "pinterest": "https://www.pinterest.com",
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "wikipedia": "https://www.wikipedia.org",
            "github": "https://github.com",
            "reddit": "https://www.reddit.com",
            "amazon": "https://www.amazon.com",
            "twitter": "https://x.com",
            "x": "https://x.com",
            "gmail": "https://mail.google.com",
            "stackoverflow": "https://stackoverflow.com",
            "chatgpt": "https://chat.openai.com",
            "claude": "https://claude.ai",
            "netflix": "https://www.netflix.com",
            "spotify": "https://open.spotify.com",
            "notion": "https://www.notion.so",
            "figma": "https://www.figma.com",
            "vercel": "https://vercel.com",
        }

    def _extract_target(self, prompt: str, action_words: list) -> str:
        text = prompt.lower()
        for word in action_words:
            text = text.replace(word, " ")
        fillers = [
            "can you", "could you", "please", "would you", "kindly",
            "for me", "for us", "the", "app", "application", "program",
            "website", "site", "up", "browser", "then", "now"
        ]
        for filler in fillers:
            text = text.replace(filler, " ")
        return text.strip(" .,!?:;")

    def process_task(self, prompt: str, context: Dict[str, Any] = None) -> str:
        from utils.fuzzy_match import is_fuzzy_match, matches_any_fuzzy, find_best_fuzzy_match
        p = prompt.lower().strip(" .,!?:;")

        # ── Phase 2: Power Controls with Typo Tolerance ──
        if matches_any_fuzzy(p, ["shutdown", "shut down", "turn off pc", "shwtdwn", "stdwn", "power off"]):
            return self.os_control.shutdown_pc()

        if matches_any_fuzzy(p, ["restart", "reboot", "restrt", "rboot"]):
            return self.os_control.restart_pc()

        if matches_any_fuzzy(p, ["lock screen", "lock pc", "lock computer", "lck screen"]):
            return self.os_control.lock_screen()

        if matches_any_fuzzy(p, ["sleep mode", "hibernate", "put to sleep", "slep"]):
            return self.os_control.sleep_pc()

        if matches_any_fuzzy(p, ["empty recycle", "clear recycle", "recycle bin"]):
            return self.os_control.empty_recycle_bin()

        if matches_any_fuzzy(p, ["open downloads", "show downloads", "downloads folder"]):
            return self.os_control.open_downloads()

        # ── Brightness ──
        if matches_any_fuzzy(p, ["brightness", "brightnes", "screen light"]):
            num = re.search(r'(\d+)', p)
            if num:
                return self.os_control.set_brightness(int(num.group(1)))
            elif matches_any_fuzzy(p, ["increase", "up", "higher", "raise"]):
                return self.os_control.set_brightness(80)
            elif matches_any_fuzzy(p, ["decrease", "down", "lower", "dim"]):
                return self.os_control.set_brightness(30)
            return self.os_control.set_brightness(60)

        # ── Night Light ──
        if matches_any_fuzzy(p, ["night light", "night mode", "blue light", "warm screen"]):
            return self.os_control.toggle_night_light()

        # ── Wi-Fi ──
        if matches_any_fuzzy(p, ["wifi", "wi-fi", "wireless"]):
            if matches_any_fuzzy(p, ["enable", "turn on", "on"]):
                return self.os_control.toggle_wifi(True)
            elif matches_any_fuzzy(p, ["disable", "turn off", "off"]):
                return self.os_control.toggle_wifi(False)
            return self.os_control.toggle_wifi(None)

        # ── Bluetooth ──
        if matches_any_fuzzy(p, ["bluetooth", "blutooth"]):
            if matches_any_fuzzy(p, ["enable", "turn on", "on"]):
                return self.os_control.toggle_bluetooth(True)
            elif matches_any_fuzzy(p, ["disable", "turn off", "off"]):
                return self.os_control.toggle_bluetooth(False)
            return self.os_control.toggle_bluetooth(None)

        # ── Monitor / Display ──
        if matches_any_fuzzy(p, ["switch monitor", "change display", "display mode", "second screen", "extend display"]):
            for mode in ["internal", "external", "extend", "clone", "duplicate", "mirror"]:
                if is_fuzzy_match(p, mode):
                    return self.os_control.switch_monitor_mode(mode)
            return self.os_control.switch_monitor_mode("extend")

        # ── Screen Recording ──
        if matches_any_fuzzy(p, ["record screen", "screen record", "start recording"]):
            num = re.search(r'(\d+)', p)
            duration = int(num.group(1)) if num else 30
            return self.os_control.record_screen(duration)

        # ── Screenshot ──
        if matches_any_fuzzy(p, ["screenshot", "screen shot", "screnshot", "capture screen"]):
            return self.os_control.take_screenshot()

        # ── System Info ──
        if matches_any_fuzzy(p, ["system info", "system status", "hardware status", "pc health"]):
            return self.os_control.get_system_info()

        # ── Local Video Playback (Play video from laptop / folder) ──
        if ("play" in p or "open" in p or "run" in p) and ("video" in p or "movie" in p or "mp4" in p or "mkv" in p) and any(w in p for w in ["lap", "laptop", "folder", "pc", "local", "downloads", "drive", "storage", "\\", "/"]):
            return self.os_control.play_local_video(prompt)


        # ── Detect browser preference if specified (fuzzy match) ──
        known_browsers = ["brave", "chrome", "firefox", "edge", "opera"]
        target_browser = None
        for word in p.split():
            match = find_best_fuzzy_match(word, known_browsers, threshold=0.72)
            if match:
                target_browser = match
                break

        # ── Compound web search (open/opn ... search/sarch ...) ──
        has_open = matches_any_fuzzy(p, ["open", "launch", "start", "run", "opn", "lnch"])
        has_search = matches_any_fuzzy(p, ["search for", "search", "find", "look for", "goto", "navigate", "sarch"])

        if has_open and has_search:
            match = re.search(r'(?:search for|search|find|lookup|look for|sarch|sarch for)\s+(.+)', p)
            if match:
                raw_query = match.group(1).strip()
                if target_browser:
                    raw_query = re.sub(rf'\b{target_browser}\b', '', raw_query, flags=re.IGNORECASE).strip()
                for site_key, site_url in self.web_map.items():
                    if is_fuzzy_match(raw_query, site_key):
                        return self.os_control.open_website(site_url, browser=target_browser)
                google_url = f"https://www.google.com/search?q={raw_query.replace(' ', '+')}"
                return self.os_control.open_website(google_url, browser=target_browser)

        # ── Platform-specific web search ──
        if is_fuzzy_match(p, "youtube") and (is_fuzzy_match(p, "search") or is_fuzzy_match(p, "find")):
            query = re.sub(r'.*search youtube for|.*search youtube|.*youtube search|.*youtube', '', p).strip()
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}" if query and query not in ["search", "for", "open"] else "https://www.youtube.com"
            return self.os_control.open_website(url, browser=target_browser)

        if is_fuzzy_match(p, "google") and (is_fuzzy_match(p, "search") or is_fuzzy_match(p, "find")):
            query = re.sub(r'.*search google for|.*search google|.*google search', '', p).strip()
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}" if query else "https://www.google.com"
            return self.os_control.open_website(url, browser=target_browser)

        # ── Check if command is opening/launching a browser application ──
        for b_name in known_browsers:
            if b_name in p and has_open:
                clean_p = p.replace("browser", "").replace("app", "").strip()
                if any(clean_p == f"{act} {b_name}" for act in ["open", "launch", "start", "run", "opn", "lnch"]) or clean_p == b_name:
                    return self.os_control.launch_app(b_name)

        # ── Direct website launch ──
        for site_key, site_url in self.web_map.items():
            if len(site_key) <= 2:
                # Require exact word match for 1 or 2 letter keys like "x"
                if re.search(rf'\b(open|launch|go\s+to)?\s*{site_key}\b', p) and not target_browser:
                    return self.os_control.open_website(site_url, browser=target_browser)
            else:
                if matches_any_fuzzy(p, [f"open {site_key}", f"launch {site_key}", f"go to {site_key}"]) or p == site_key:
                    return self.os_control.open_website(site_url, browser=target_browser)

        # ── App launch (open / launch / opn / lnch) ──
        if has_open:
            target = self._extract_target(prompt, ["open", "launch", "start", "run", "opn", "lnch"])
            for site_key, site_url in self.web_map.items():
                if len(site_key) > 2 and is_fuzzy_match(target, site_key):
                    return self.os_control.open_website(site_url, browser=target_browser)
            if "." in target or "http" in target or "www" in target:
                return self.os_control.open_website(target, browser=target_browser)
            return self.os_control.launch_app(target if target else prompt)


        # ── App close (close / kill / clse / kll) ──
        elif matches_any_fuzzy(p, ["close", "kill", "stop", "terminate", "exit", "quit", "clse", "kll"]):
            target = self._extract_target(prompt, ["close", "kill", "stop", "terminate", "exit", "quit", "clse", "kll"])
            return self.os_control.close_app(target if target else prompt)

        # ── Volume ──
        elif any(kw in p for kw in ["volume", "mute", "unmute", "sound", "louder", "quieter", "turn up", "turn down"]):
            num_match = re.search(r'(\d+)', p)
            number_val = int(num_match.group(1)) if num_match else None

            if "mute" in p and "unmute" not in p:
                return self.os_control.control_volume("mute")
            elif "unmute" in p:
                return self.os_control.control_volume("unmute")
            elif "set" in p or "to" in p:
                return self.os_control.control_volume("set", level=number_val) if number_val else self.os_control.control_volume("set", level=50)
            elif any(w in p for w in ["decrease", "down", "lower", "quieter", "turn down"]):
                return self.os_control.control_volume("decrease", level=number_val)
            elif any(w in p for w in ["increase", "up", "raise", "louder", "turn up"]):
                return self.os_control.control_volume("increase", level=number_val)
            elif number_val is not None:
                return self.os_control.control_volume("set", level=number_val)
            else:
                return self.os_control.control_volume("decrease")

        # ── Screenshot ──
        elif any(w in p for w in ["screenshot", "capture screen", "snap screen"]):
            return self.os_control.take_screenshot()

        # ── Clipboard ──
        elif "clipboard" in p:
            return f"📋 Clipboard: '{self.os_control.get_clipboard_text()}'"

        # ── Folder navigation ──
        elif any(w in p for w in ["open folder", "navigate to", "go to folder"]):
            match = re.search(r'(?:open folder|navigate to|go to folder)\s+(.+)', p)
            if match:
                return self.os_control.open_folder(match.group(1).strip())

        return self.os_control.execute_terminal_command(prompt)


class CoderSpecialist(BaseSpecialistAgent):
    """Phase 8: Enhanced Coding Copilot with git, file generation, test creation, etc."""

    def __init__(self, ai_provider=None):
        super().__init__("CoderAgent", "Code Generation, Debugging & Technical Problem Solving")
        self.ai_provider = ai_provider

    def set_provider(self, ai_provider):
        self.ai_provider = ai_provider

    def process_task(self, prompt: str, context: Dict[str, Any] = None) -> str:
        p = prompt.lower()
        ctx = context or {}

        # ── Git Operations ──
        if "git" in p:
            return self._handle_git(prompt, ctx)

        # ── Generate / Create File ──
        if any(w in p for w in ["create file", "generate file", "write file", "create a file", "make a file", "new file"]):
            return self._generate_file(prompt, ctx)

        # ── Unit Tests ──
        if any(w in p for w in ["write test", "create test", "unit test", "generate test", "pytest", "test for"]):
            return self._generate_tests(prompt, ctx)

        # ── Generate Documentation ──
        if any(w in p for w in ["document", "docstring", "add docs", "generate docs", "documentation for"]):
            return self._generate_docs(prompt, ctx)

        # ── Fix / Debug ──
        if any(w in p for w in ["fix", "debug", "bug", "error", "exception", "traceback"]):
            return self._fix_code(prompt, ctx)

        # ── Refactor ──
        if any(w in p for w in ["refactor", "rewrite", "improve", "optimize", "clean up"]):
            return self._refactor_code(prompt, ctx)

        # ── Explain Code ──
        if any(w in p for w in ["explain", "what does", "what is", "describe this code", "how does"]):
            return self._explain_code(prompt, ctx)

        # ── Default: pass to AI with coding system prompt ──
        return f"[CoderAgent] Processing: {prompt}"

    def _handle_git(self, prompt: str, ctx: dict) -> str:
        """Routes git commands or generates git help."""
        p = prompt.lower()
        # Direct git commands
        git_cmd_map = {
            "git status": "status",
            "git log": "log --oneline -10",
            "git pull": "pull",
            "git push": "push",
            "git branch": "branch",
            "git init": "init",
        }
        for phrase, git_sub in git_cmd_map.items():
            if phrase in p:
                from automation.os_control import ComputerAutomation
                auto = ComputerAutomation()
                return auto.execute_terminal_command(f"git {git_sub}")

        # Commit with message
        if "commit" in p:
            msg_match = re.search(r'commit[:\s]+["\']?(.+?)["\']?$', prompt, re.IGNORECASE)
            msg = msg_match.group(1).strip() if msg_match else "Update"
            from automation.os_control import ComputerAutomation
            auto = ComputerAutomation()
            stage = auto.execute_terminal_command("git add -A")
            commit_result = auto.execute_terminal_command(f'git commit -m "{msg}"')
            return f"Git staged all files.\n{commit_result}"

        return f"[GitAgent] Git command: {prompt}"

    def _generate_file(self, prompt: str, ctx: dict) -> str:
        """Generates file content via LLM and optionally saves it."""
        if not self.ai_provider:
            return "[CoderAgent] No AI provider for file generation."
        response = self.ai_provider.generate_response(
            messages=[{"sender": "User", "content": prompt}],
            system_prompt=(
                "You are an expert programmer. Generate the requested file with complete, working code. "
                "Include all necessary imports. Format the code cleanly. "
                "At the end, suggest a filename."
            )
        )
        return response

    def _generate_tests(self, prompt: str, ctx: dict) -> str:
        if not self.ai_provider:
            return "[CoderAgent] No AI provider for test generation."
        return self.ai_provider.generate_response(
            messages=[{"sender": "User", "content": prompt}],
            system_prompt=(
                "You are an expert Python developer specializing in testing. "
                "Generate comprehensive pytest unit tests for the described functionality. "
                "Include edge cases, happy paths, and error cases. Use pytest fixtures where appropriate."
            )
        )

    def _generate_docs(self, prompt: str, ctx: dict) -> str:
        if not self.ai_provider:
            return "[CoderAgent] No AI provider for documentation."
        return self.ai_provider.generate_response(
            messages=[{"sender": "User", "content": prompt}],
            system_prompt=(
                "You are a technical writer. Generate clear, comprehensive documentation. "
                "Use Google-style docstrings for Python. Include parameter descriptions, return types, "
                "and usage examples."
            )
        )

    def _fix_code(self, prompt: str, ctx: dict) -> str:
        if not self.ai_provider:
            return "[CoderAgent] No AI provider for bug fixing."
        return self.ai_provider.generate_response(
            messages=[{"sender": "User", "content": prompt}],
            system_prompt=(
                "You are an expert debugger. Analyze the provided error or code, identify the root cause, "
                "and provide a complete fix with explanation. Show the corrected code clearly."
            )
        )

    def _refactor_code(self, prompt: str, ctx: dict) -> str:
        if not self.ai_provider:
            return "[CoderAgent] No AI provider for refactoring."
        return self.ai_provider.generate_response(
            messages=[{"sender": "User", "content": prompt}],
            system_prompt=(
                "You are an expert software engineer. Refactor the provided code to improve readability, "
                "performance, and maintainability. Follow SOLID principles and best practices. "
                "Explain each significant change."
            )
        )

    def _explain_code(self, prompt: str, ctx: dict) -> str:
        if not self.ai_provider:
            return "[CoderAgent] No AI provider for code explanation."
        return self.ai_provider.generate_response(
            messages=[{"sender": "User", "content": prompt}],
            system_prompt=(
                "You are a patient programming teacher. Explain the provided code clearly and thoroughly. "
                "Break down complex concepts, use analogies where helpful, and highlight any important patterns "
                "or gotchas."
            )
        )
