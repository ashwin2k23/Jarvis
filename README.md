# Jarvis AI Desktop Assistant

Jarvis is an advanced, extensible desktop AI assistant built in Python and PySide6 (Qt). It implements a 10-phase feature set making it a genuine daily-use OS-level AI assistant.

---

## Feature Roadmap — All 10 Phases Implemented

- **Phase 1 — Long-Term Memory**: Automatic fact extraction from every conversation. Remembers names, dates, jobs, preferences, reminders. Context-injected into every LLM response. Search/delete memory from the UI.
- **Phase 2 — Desktop Automation**: Launch/close apps, open Downloads, shutdown/restart/lock/sleep PC, set brightness, toggle Night Light/Wi-Fi/Bluetooth, switch monitor modes, record screen, empty recycle bin.
- **Phase 3 — Vision (Camera)**: Webcam capture via OpenCV → Gemini Vision. "What do you see?" / "Read this document" / "Analyze for errors."
- **Phase 4 — Screen Understanding**: Real-time screen capture → Gemini Vision. Explain errors, read code, detect UI bugs, summarize PDFs.
- **Phase 5 — Local Knowledge Base (RAG)**: Index local folders/files (PDFs, code, markdown, text). Pure-Python TF-IDF retrieval — no ML dependencies. "Search my React project for the login function."
- **Phase 6 — Agent Mode**: LLM-powered multi-step task planning. "Build a React project, install deps, open VS Code." Executes each step sequentially.
- **Phase 7 — Skills / Plugins**: Modular skill system. Built-in: Weather (Open-Meteo, free, no API key), Spotify (media keys + URI), GitHub (full REST API — repos, PRs, issues, commits, notifications).
- **Phase 8 — Coding Copilot**: Explain code, generate files, fix bugs, refactor, git operations, commit, unit test generation, documentation generation.
- **Phase 9 — Wake Word**: "Hey Jarvis" offline detection via `openwakeword`. Falls back to SpeechRecognition-based detection automatically.
- **Phase 10 — Proactive Intelligence**: Background monitor (60s intervals) for low battery alerts, high CPU warnings, reminder notifications, daily 9 AM briefing.

---

## Architecture

```
JarvisCoreController
├── DatabaseMemory (SQLite)
├── MemoryManager (fact extraction + context injection)
├── ComputerAutomation (20+ OS commands)
├── WebSearchEngine (DuckDuckGo)
├── GeminiProvider / OpenAIProvider / OllamaProvider / MockProvider
├── CameraVision + ScreenVision (multimodal Gemini Vision)
├── LocalKnowledgeIndexer + RAGRetriever
├── SkillRegistry → WeatherSkill, SpotifySkill, GitHubSkill
├── AgentPlanner → ResearcherSpecialist, AutomationSpecialist, CoderSpecialist
├── TaskExecutor (multi-step agent mode)
├── ProactiveMonitor (background QThread)
└── TextToSpeechEngine + SpeechToTextListener + WakeWordListener
```

---

## Installation & Setup

1. **Install Core Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Optional — Wake Word**:
   ```bash
   pip install openwakeword pyaudio
   ```

3. **Run Jarvis**:
   ```bash
   python run.py
   ```

4. **Configure in Settings Tab**:
   - Choose AI Provider (Gemini recommended — set API key)
   - Set GitHub PAT for GitHub skill
   - Enable/disable Wake Word and Proactive Monitor

---

## Usage Examples

| You say... | Jarvis does... |
|------------|----------------|
| "Remember my internship starts next Monday" | Saves to memory, recalls on demand |
| "What's the weather in London?" | Fetches real-time weather (no API key) |
| "Open VS Code" | Launches VS Code |
| "Shutdown PC" | Issues `shutdown /s /t 10` |
| "Set brightness to 70" | Adjusts screen brightness via WMI |
| "What do you see?" | Captures webcam, describes via Gemini Vision |
| "Analyze my screen" | Screenshots desktop, analyzes via Gemini Vision |
| "Explain this error on screen" | Explains visible error messages |
| "Search my project for login function" | RAG searches indexed local files |
| "Build a React app, initialize git, open VS Code" | Agent Mode — executes all steps |
| "Play Blinding Lights on Spotify" | Spotify URI search + play |
| "Show my GitHub PRs" | Lists open pull requests via GitHub API |
| "Write unit tests for this function" | Generates pytest test code |
| "Hey Jarvis" | Wakes Jarvis without pressing any button |
