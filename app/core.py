"""
app/core.py — JarvisCoreController
Central orchestrator binding all Jarvis subsystems:
UI, AI Providers, Memory, Vision, RAG, Skills, Tools, Automation, Speech, Proactive.
"""
from app.config_manager import ConfigManager
from memory.db import DatabaseMemory
from memory.memory_manager import MemoryManager
from security.audit import SecurityAuditLogger
from automation.os_control import ComputerAutomation
from search.web_search import WebSearchEngine
from speech.tts import TextToSpeechEngine
from speech.stt import SpeechToTextListener
from ai.provider_interface import AIProviderInterface
from ai.gemini_provider import GeminiProvider
from ai.openai_provider import OpenAIProvider
from ai.ollama_provider import OllamaProvider
from ai.mock_provider import MockProvider
from tools.registry import ToolRegistry
from agents.planner import AgentPlanner
from agents.task_executor import TaskExecutor
from vision.camera import CameraVision
from vision.screen_vision import ScreenVision
from rag.indexer import LocalKnowledgeIndexer
from rag.retriever import RAGRetriever
from skills.skill_registry import SkillRegistry


class JarvisCoreController:
    """Central Orchestrator binding UI, AI Providers, Memory, Vision, RAG, Skills, Tools, and Automation."""

    def __init__(self):
        self.config = ConfigManager()
        self.security = SecurityAuditLogger()
        self.db = DatabaseMemory()
        self.memory_manager = MemoryManager(self.db)
        self.automation = ComputerAutomation(self.security)
        self.search = WebSearchEngine()
        self.tts = TextToSpeechEngine(
            rate=self.config.get("tts_voice_rate", 180),
            volume=self.config.get("tts_volume", 1.0),
            voice_id=self.config.get("tts_voice_id", "")
        )
        self.tools = ToolRegistry()
        self.skills = SkillRegistry()

        # AI provider (must be before vision/coder which need it)
        self.ai_provider = self._init_ai_provider()

        # Vision
        self.camera_vision = CameraVision(self.ai_provider)
        self.screen_vision = ScreenVision(self.ai_provider)

        # RAG
        self.rag_indexer = LocalKnowledgeIndexer(self.db)
        self.rag_retriever = RAGRetriever(self.db)

        # Agent planner with all subsystem references
        self.planner = AgentPlanner(self.search, self.automation)
        self.planner.skill_registry = self.skills
        self.planner.rag_retriever = self.rag_retriever
        self.planner.memory_manager = self.memory_manager
        self.planner.vision_camera = self.camera_vision
        self.planner.vision_screen = self.screen_vision

        # Coder agent needs AI provider
        self.planner.coder.set_provider(self.ai_provider)

        # Task executor (Phase 6)
        self.task_executor = TaskExecutor(self.ai_provider, self)
        self.planner.task_executor = self.task_executor

        # Proactive monitor (Phase 10)
        self._proactive_monitor = None
        if self.config.get("enable_proactive_monitor", True):
            self._start_proactive_monitor()

    # ──────────────────────────────────────────────────────────────────
    # AI Provider Init
    # ──────────────────────────────────────────────────────────────────

    def _init_ai_provider(self) -> AIProviderInterface:
        provider_type = self.config.get("ai_provider", "mock")
        if provider_type == "gemini":
            key = self.config.get("gemini_api_key", "")
            model = self.config.get("gemini_model", "gemini-2.5-flash")
            provider = GeminiProvider(api_key=key, model=model)
            if provider.is_available():
                return provider
            print("[JarvisCore] Gemini API unavailable/missing key. Falling back to MockProvider.")
        elif provider_type == "openai":
            key = self.config.get("openai_api_key", "")
            model = self.config.get("openai_model", "gpt-4o-mini")
            provider = OpenAIProvider(api_key=key, model=model)
            if provider.is_available():
                return provider
            print("[JarvisCore] OpenAI API unavailable/missing key. Falling back to MockProvider.")
        elif provider_type == "ollama":
            url = self.config.get("ollama_url", "http://localhost:11434")
            model = self.config.get("ollama_model", "llama3")
            provider = OllamaProvider(base_url=url, model=model)
            if provider.is_available():
                return provider
            print("[JarvisCore] Ollama server unavailable. Falling back to MockProvider.")
        return MockProvider()

    # ──────────────────────────────────────────────────────────────────
    # Config Updates
    # ──────────────────────────────────────────────────────────────────

    def update_tts_config(self, voice_id: str, voice_rate: int = 180):
        self.config.set("tts_voice_id", voice_id)
        self.config.set("tts_voice_rate", voice_rate)
        self.tts.set_voice(voice_id)
        self.tts.set_rate(voice_rate)

    def update_provider_config(self, provider_type: str, api_key: str = "", gemini_api_key: str = "",
                               gemini_model: str = "", ollama_url: str = "", model: str = ""):
        self.config.set("ai_provider", provider_type)
        if gemini_api_key:
            self.config.set("gemini_api_key", gemini_api_key)
        if gemini_model:
            self.config.set("gemini_model", gemini_model)
        if api_key:
            self.config.set("openai_api_key", api_key)
        if ollama_url:
            self.config.set("ollama_url", ollama_url)
        if model:
            key_map = {"gemini": "gemini_model", "openai": "openai_model", "ollama": "ollama_model"}
            if provider_type in key_map:
                self.config.set(key_map[provider_type], model)
        # Re-initialize AI provider and update dependent subsystems
        self.ai_provider = self._init_ai_provider()
        self.camera_vision.set_provider(self.ai_provider)
        self.screen_vision.set_provider(self.ai_provider)
        self.planner.coder.set_provider(self.ai_provider)
        self.task_executor.set_provider(self.ai_provider)

    # ──────────────────────────────────────────────────────────────────
    # Main Input Processing
    # ──────────────────────────────────────────────────────────────────

    def process_user_input(self, text: str, session_id: str = "default") -> dict:
        """Processes user input through all Jarvis subsystems and returns a response dict."""
        text = text.strip()
        if not text:
            return {"response": "", "agent": "None", "type": "empty"}

        # 1. Save user message
        self.db.add_message("User", text, session_id=session_id)

        # 2. Extract and store memory facts from every user message (Phase 1)
        self.memory_manager.extract_and_save(text)

        # 3. Handle explicit "remember that / forget / recall" commands
        from memory.memory_manager import MemoryManager
        if MemoryManager.is_memory_command(text):
            return self._handle_memory_command(text)

        tl = text.lower()

        # 3.5 Direct System Clock Trigger (exact live date & time)
        if any(p in tl for p in ["current date and time", "current time", "what time is it", "what's the time", "what date is it", "what's the date", "today's date", "what day is it", "current date", "time and date", "date and time"]):
            import datetime
            now = datetime.datetime.now()
            time_str = now.strftime("%A, %B %d, %Y at %I:%M %p")
            ans = f"The current date and time is **{time_str}**."
            self.db.add_message("Jarvis", ans, metadata={"agent": "SystemClock"})
            if self.config.get("auto_speak_responses", True):
                self.tts.speak(f"The current time is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}.")
            return {"response": ans, "agent": "SystemClock", "type": "clock"}

        # 4. Direct tool triggers & Dynamic Workspace Intents


        # Dynamic Workspace Intents
        workspace_mode = None
        if any(phrase in tl for phrase in ["happening around the world", "world news", "top headlines", "latest headlines"]):
            workspace_mode = "news"
        elif any(phrase in tl for phrase in ["what's trending", "what is trending", "trending on x", "trending topics"]):
            workspace_mode = "trends"
        elif any(phrase in tl for phrase in ["latest ai news", "tech news", "ai news", "technology updates"]):
            workspace_mode = "tech"
        elif any(phrase in tl for phrase in ["show me videos", "videos about", "video about", "youtube videos", "videos of", "video of", "videos on", "watch videos"]):
            workspace_mode = "videos"
        elif any(phrase in tl for phrase in ["morning brief", "newsletter", "daily briefing", "executive digest"]):
            workspace_mode = "brief"

        if workspace_mode:
            from search.dynamic_feed import DynamicFeedEngine
            engine = DynamicFeedEngine()
            user_name = self.config.get("user_name", "Ashwin")
            
            if workspace_mode == "news":
                data = engine.fetch_news_feed("world")
                summary = f"Good evening, {user_name}. Here are today's top global headlines: {data[0]['title']}, and {data[1]['title']}. I've opened the World News panel for you."
            elif workspace_mode == "trends":
                data = engine.fetch_trending_topics()
                summary = f"Here is what's trending today, {user_name}: {data[0]['topic']}, {data[1]['topic']}, and {data[2]['topic']}. Check out the Trending panel on the right."
            elif workspace_mode == "tech":
                data = engine.fetch_tech_ai_feed()
                summary = f"Here are the latest AI & Tech updates: {data[0]['company']} released {data[0]['title']}. I've populated the Tech panel."
            elif workspace_mode == "videos":
                import re
                clean_query = re.sub(
                    r'(?i)\b(show\s+me\s+videos?\s+(about|on|of|for)?|videos?\s+(about|on|of|for)?|youtube\s+videos?\s+(about|on|of|for)?|search\s+videos?\s+(about|on|of|for)?|play\s+videos?\s+(about|on|of|for)?|watch\s+videos?\s+(about|on|of|for)?)\b',
                    '',
                    text
                ).strip(" .,!?")
                query = clean_query if clean_query else "trending highlights"
                data = engine.fetch_video_feed(query)
                summary = f"I found video results for '{query}'. Click any card in the Video panel to stream it inside Jarvis."
            else: # brief
                data = engine.generate_newsletter_digest()
                summary = f"Good morning, {user_name}! Here is your executive morning briefing covering Markets, AI, Space, and Sports."


            self.db.add_message("Jarvis", summary, metadata={"agent": "DynamicWorkspace"})
            if self.config.get("auto_speak_responses", True):
                self.tts.speak(summary)

            return {
                "response": summary,
                "agent": "DynamicWorkspace",
                "type": "workspace",
                "workspace_mode": workspace_mode,
                "workspace_data": data
            }

        if tl.startswith("calc ") or tl.startswith("calculate "):
            expr = text.split(" ", 1)[1]
            result = self.tools.execute_tool("calculator", {"expression": expr})
            self.db.add_message("Jarvis", result, metadata={"agent": "CalculatorTool"})
            if self.config.get("auto_speak_responses", True):
                self.tts.speak(result)
            return {"response": result, "agent": "CalculatorTool", "type": "tool"}

        elif any(w in tl for w in ["system status", "cpu usage", "ram info", "hardware status"]):
            result = self.automation.get_system_info()
            self.db.add_message("Jarvis", result, metadata={"agent": "SystemMonitorTool"})
            if self.config.get("auto_speak_responses", True):
                self.tts.speak("Here is your system hardware status.")
            return {"response": result, "agent": "SystemMonitorTool", "type": "tool"}


        # 5. Multi-agent routing
        agent_name, agent_output = self.planner.route_request(text)

        # ── Agent Mode (Phase 6) ──
        if agent_name == "AgentMode":
            return self._handle_agent_mode(text)

        # ── Skills (Phase 7) ──
        if agent_name == "SkillAgent":
            result = self.skills.route_and_execute(text, core=self)
            if result:
                self.db.add_message("Jarvis", result, metadata={"agent": "SkillAgent"})
                if self.config.get("auto_speak_responses", True):
                    self.tts.speak(result[:300])
                return {"response": result, "agent": "SkillAgent", "type": "skill"}

        # ── Vision (Phase 3 & 4) ──
        if agent_name == "VisionAgent":
            return self._handle_vision_command(text)

        # ── RAG (Phase 5) ──
        if agent_name == "RAGAgent":
            result = self.rag_retriever.answer_from_knowledge_base(text, self.ai_provider)
            self.db.add_message("Jarvis", result, metadata={"agent": "RAGAgent"})
            if self.config.get("auto_speak_responses", True):
                self.tts.speak(result[:300])
            return {"response": result, "agent": "RAGAgent", "type": "rag"}

        # ── Memory Recall (Phase 1) ──
        if agent_name == "MemoryAgent":
            recall_result = self.memory_manager.recall_fact(text)
            if recall_result:
                # Supplement with LLM for natural answer
                memory_context = self.memory_manager.get_relevant_context(text)
                history = self.db.get_recent_messages(limit=6)
                system_prompt = self._build_system_prompt(memory_context)
                response_text = self.ai_provider.generate_response(history, system_prompt=system_prompt)
                self.db.add_message("Jarvis", response_text, metadata={"agent": "MemoryAgent"})
                if self.config.get("auto_speak_responses", True):
                    self.tts.speak(response_text)
                return {"response": response_text, "agent": "MemoryAgent", "type": "memory"}

        # ── Automation (Phase 2) ──
        if agent_name == "AutomationAgent":
            response_text = agent_output
            self.db.add_message("Jarvis", response_text, metadata={"agent": agent_name})
            if self.config.get("auto_speak_responses", True):
                self.tts.speak(response_text[:200])
            return {"response": response_text, "agent": agent_name, "type": "automation"}

        # ── Research ──
        elif agent_name == "ResearcherAgent":
            memory_context = self.memory_manager.get_relevant_context(text)
            prompt_with_context = [
                {"sender": "system", "content": f"Web search results:\n{agent_output}"},
                {"sender": "User", "content": text}
            ]
            system_prompt = self._build_system_prompt(memory_context) + " Synthesize web search results into a direct, helpful response."
            response_text = self.ai_provider.generate_response(prompt_with_context, system_prompt=system_prompt)
            self.db.add_message("Jarvis", response_text, metadata={"agent": agent_name})
            if self.config.get("auto_speak_responses", True):
                self.tts.speak(response_text[:300])
            return {"response": response_text, "agent": agent_name, "type": "research"}

        # ── Coder (Phase 8) ──
        elif agent_name == "CoderAgent":
            if agent_output and not agent_output.startswith("[CoderAgent]"):
                # Specialist already processed it via AI
                response_text = agent_output
            else:
                # Pass to LLM with coding context
                history = self.db.get_recent_messages(limit=8)
                system_prompt = (
                    f"You are {self.config.get('assistant_name', 'Jarvis')}, an expert software engineer and coding assistant. "
                    "Help with code, debugging, architecture, git, and technical questions. "
                    "Use markdown code blocks. Be precise and practical."
                )
                response_text = self.ai_provider.generate_response(history, system_prompt=system_prompt)
            self.db.add_message("Jarvis", response_text, metadata={"agent": agent_name})
            if self.config.get("auto_speak_responses", True):
                self.tts.speak(response_text[:200])
            return {"response": response_text, "agent": agent_name, "type": "coding"}

        # ── General Conversation (default) ──
        else:
            memory_context = self.memory_manager.get_relevant_context(text)
            history = self.db.get_recent_messages(limit=12)
            system_prompt = self._build_system_prompt(memory_context)
            response_text = self.ai_provider.generate_response(history, system_prompt=system_prompt)
            self.db.add_message("Jarvis", response_text, metadata={"agent": "CoreAssistant"})
            if self.config.get("auto_speak_responses", True):
                self.tts.speak(response_text)
            return {"response": response_text, "agent": "CoreAssistant", "type": "chat"}

    # ──────────────────────────────────────────────────────────────────
    # Specialized Handlers
    # ──────────────────────────────────────────────────────────────────

    def _build_system_prompt(self, memory_context: str = "") -> str:
        """Builds the LLM system prompt with optional memory context injection and live clock."""
        import datetime
        name = self.config.get("assistant_name", "Jarvis")
        user = self.config.get("user_name", "Ashwin")
        now = datetime.datetime.now()
        now_str = now.strftime("%A, %B %d, %Y at %I:%M %p")
        base = (
            f"You are {name}, a warm, highly intelligent personal AI assistant engaged in a "
            f"1-on-1 conversation with {user}. The CURRENT REAL-TIME LIVE DATE AND TIME is {now_str}. "
            f"Always use this current date for relative time references, sports results, and current news questions. "
            f"Respond naturally, helpfully, and like a real assistant. Keep responses clear, concise, and engaging."
        )
        if memory_context:
            base += f"\n\n{memory_context}"
        return base


    def _handle_memory_command(self, text: str) -> dict:
        """Handles explicit memory save/recall/forget commands (Phase 1)."""
        tl = text.lower()

        if any(p in tl for p in ["forget", "don't remember", "delete"]):
            # Extract what to forget
            import re
            match = re.search(r'forget\s+(?:that\s+)?(?:my\s+)?(.+)', tl)
            if match:
                key = match.group(1).strip()
                self.memory_manager.forget_fact(key)
                response = f"✅ I've forgotten: **{key}**"
            else:
                response = "What should I forget? Please be more specific."
        elif any(p in tl for p in ["remember that", "make a note", "keep in mind", "don't forget", "save this"]):
            # Extract the fact
            import re
            match = re.search(r'(?:remember that|make a note that|keep in mind that|don\'t forget that)\s+(.+)', tl)
            if match:
                fact = match.group(1).strip()
                self.memory_manager.save_explicit_fact("reminders", f"note_{fact[:20].replace(' ', '_')}", fact)
                response = f"✅ Got it! I'll remember: **{fact}**"
            else:
                response = "What should I remember? Please provide the information after 'remember that'."
        else:
            # General memory query — let AI answer with memory context
            memory_context = self.memory_manager.get_full_context_for_prompt()
            history = self.db.get_recent_messages(limit=8)
            system_prompt = self._build_system_prompt(memory_context)
            response = self.ai_provider.generate_response(history, system_prompt=system_prompt)

        self.db.add_message("Jarvis", response, metadata={"agent": "MemoryManager"})
        if self.config.get("auto_speak_responses", True):
            self.tts.speak(response[:200])
        return {"response": response, "agent": "MemoryManager", "type": "memory"}

    def _handle_vision_command(self, text: str) -> dict:
        """Routes vision commands to camera or screen vision (Phase 3 & 4)."""
        tl = text.lower()
        result = ""

        if any(p in tl for p in ["what do you see", "what can you see", "describe what you see", "camera"]):
            result = self.camera_vision.describe_what_i_see()
        elif any(p in tl for p in ["read this document", "read document", "read this paper"]):
            result = self.camera_vision.read_document()
        elif any(p in tl for p in ["analyze screen", "analyze my screen", "what's on my screen", "what's on screen", "look at my screen"]):
            result = self.screen_vision.analyze_screen()
        elif any(p in tl for p in ["explain this error", "explain the error", "error on screen"]):
            result = self.screen_vision.explain_error_on_screen()
        elif any(p in tl for p in ["read code on screen", "read code", "code on screen"]):
            result = self.screen_vision.read_code_on_screen()
        elif any(p in tl for p in ["detect ui bugs", "ui bugs", "ui issues"]):
            result = self.screen_vision.detect_ui_bugs()
        elif "pdf" in tl:
            import re
            path_match = re.search(r'["\']?([A-Za-z]:\\[^"\']+\.pdf|[^"\']+\.pdf)["\']?', text, re.IGNORECASE)
            if path_match:
                result = self.screen_vision.summarize_pdf(path_match.group(1))
            else:
                result = "Please provide the PDF file path. Example: 'summarize PDF C:\\Documents\\file.pdf'"
        else:
            result = self.screen_vision.analyze_screen(custom_prompt=text)

        self.db.add_message("Jarvis", result, metadata={"agent": "VisionAgent"})
        if self.config.get("auto_speak_responses", True):
            self.tts.speak(result[:300])
        return {"response": result, "agent": "VisionAgent", "type": "vision"}

    def _handle_agent_mode(self, text: str) -> dict:
        """Executes multi-step task planning (Phase 6)."""
        steps = self.task_executor.parse_plan(text)
        intro = f"🤖 **Agent Mode** — Planning {len(steps)} steps...\n\n"
        result = self.task_executor.execute_plan(steps)
        full_response = intro + result
        self.db.add_message("Jarvis", full_response, metadata={"agent": "AgentMode"})
        if self.config.get("auto_speak_responses", True):
            self.tts.speak(f"Executing {len(steps)} step plan.")
        return {"response": full_response, "agent": "AgentMode", "type": "agent_mode"}

    # ──────────────────────────────────────────────────────────────────
    # Proactive Monitor (Phase 10)
    # ──────────────────────────────────────────────────────────────────

    def _start_proactive_monitor(self):
        """Starts the background proactive intelligence monitor."""
        try:
            from proactive.monitor import ProactiveMonitor
            self._proactive_monitor = ProactiveMonitor()
            self._proactive_monitor.set_core(self)
            self._proactive_monitor.start()
        except Exception as e:
            print(f"[JarvisCore] Proactive monitor failed to start: {e}")

    def get_proactive_monitor(self):
        """Returns the ProactiveMonitor instance for connecting UI signals."""
        return self._proactive_monitor

    def stop_proactive_monitor(self):
        """Cleanly stops the proactive monitor thread."""
        if self._proactive_monitor and self._proactive_monitor.isRunning():
            self._proactive_monitor.stop()
            self._proactive_monitor.wait(2000)

    # ──────────────────────────────────────────────────────────────────
    # RAG Convenience (Phase 5)
    # ──────────────────────────────────────────────────────────────────

    def index_knowledge_folder(self, folder_path: str) -> dict:
        """Indexes a folder into the RAG knowledge base."""
        return self.rag_indexer.index_folder(folder_path)

    def index_knowledge_file(self, file_path: str) -> dict:
        """Indexes a single file into the RAG knowledge base."""
        return self.rag_indexer.index_file(file_path)
