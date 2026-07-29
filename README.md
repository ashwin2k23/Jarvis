<![CDATA[<div align="center">

<img src="assets/jarvis_orb.gif" width="120" alt="Jarvis Orb"/>

# Jarvis AI Desktop Assistant

**A powerful, multi-modal, OS-level AI assistant built with Python & PySide6**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-Qt_6.5%2B-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PySide6/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![Platform](https://img.shields.io/badge/Windows-10%2F11-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

*Combines long-term memory · desktop automation · computer vision · local RAG · voice interaction · multi-agent planning · proactive monitoring — all in one native desktop app.*

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [AI Providers](#ai-providers)
- [Usage Examples](#usage-examples)
- [Agent Routing](#agent-routing)
- [Skills / Plugins](#skills--plugins)
- [Memory System](#memory-system)
- [Desktop Automation](#desktop-automation)
- [Vision Capabilities](#vision-capabilities)
- [RAG (Local Knowledge Base)](#rag-local-knowledge-base)
- [Proactive Intelligence](#proactive-intelligence)
- [Building an Executable](#building-an-executable)
- [Contributing](#contributing)

---

## Overview

Jarvis is a **feature-complete AI desktop assistant** designed to act as a genuine daily-use companion at the OS level. It goes well beyond a simple chatbot:

- **It remembers you** — extracts and stores facts from every conversation into a persistent SQLite memory database, and injects that context into every future LLM response.
- **It controls your PC** — launches apps, changes brightness, toggles Wi-Fi/Bluetooth, takes screenshots, manages the clipboard, and runs terminal commands.
- **It sees your screen** — captures your webcam or desktop in real time and describes, analyzes, or debugs what it sees using multimodal AI.
- **It knows your files** — indexes local folders (code, PDFs, markdown, text) and answers questions about them with TF-IDF retrieval, no ML dependencies required.
- **It works proactively** — monitors battery, CPU, reminders, and delivers a daily briefing at 9 AM — all in a background thread.
- **It speaks and listens** — full TTS (edge-tts / pyttsx3) and STT (SpeechRecognition), with optional offline wake word detection ("Hey Jarvis").

The UI is built with PySide6 and uses a custom **Invisible Intelligence** design language — dark glass aesthetic inspired by Raycast, Linear, Arc Browser, and Apple Intelligence.

---

## Features

### Phase 1 — Long-Term Memory
- Automatically extracts facts from every user message using regex pattern matching (name, age, location, employer, project, preferences, deadlines, reminders)
- Facts are stored in a persistent SQLite database and injected into every LLM system prompt as context
- Supports natural-language recall: *"What did I tell you about my project?"*
- Supports explicit commands: *"Remember that…"*, *"Forget my…"*, *"Delete memory of…"*
- Memory is searchable and deletable from the UI Settings → Memory tab

### Phase 2 — Desktop Automation (20+ commands)
- **App control**: Launch or close any installed app by name (resolves Start Menu shortcuts, UWP protocols, and common install paths dynamically)
- **Power management**: Shutdown, restart, sleep, hibernate, lock screen
- **Display**: Set brightness (WMI), toggle Night Light, switch monitor modes
- **Network**: Toggle Wi-Fi and Bluetooth
- **System**: Empty Recycle Bin, record screen, open Downloads/Documents/Desktop
- **Browser/web**: Open URLs, search Google, search YouTube
- **Volume**: Mute, unmute, set volume level
- **Terminal**: Run arbitrary shell commands safely

### Phase 3 — Camera Vision
- Captures webcam frames via OpenCV and sends them to Gemini Vision
- Supports: *"What do you see?"*, *"Read this document"*, *"Describe this image"*, *"Analyze for errors"*

### Phase 4 — Screen Understanding
- Takes real-time screenshots of the desktop and sends to Gemini Vision
- Supports: *"Analyze my screen"*, *"Explain this error"*, *"Read code on screen"*, *"Detect UI bugs"*, *"Summarize this PDF"*

### Phase 5 — Local Knowledge Base (RAG)
- Index local folders or individual files (PDF via pdfplumber, code, markdown, plain text)
- Pure-Python TF-IDF retrieval — zero ML/vector DB dependencies
- Queries: *"Search my project for the login function"*, *"What does my README say about X?"*

### Phase 6 — Agent Mode
- LLM-powered multi-step task planner; detects complex multi-part requests automatically
- Breaks goals into individual steps and executes them sequentially via `TaskExecutor`
- Example: *"Create a React project, install dependencies, open it in VS Code"*

### Phase 7 — Skills / Plugins
- Modular skill system with a `SkillRegistry` and `BaseSkill` interface — easily extensible
- **WeatherSkill**: Real-time weather via Open-Meteo (free, no API key required)
- **SpotifySkill**: Media key control + URI-based track/playlist playback
- **GitHubSkill**: Full REST API — list repos, open PRs, issues, commits, notifications, create issues

### Phase 8 — Coding Copilot
- Routed to `CoderSpecialist` with an expert software-engineer system prompt
- Explain code, fix bugs, refactor, generate unit tests, write documentation
- Git operations: commit, status, push, log — executed directly through the terminal tool

### Phase 9 — Wake Word
- Offline "Hey Jarvis" detection via `openwakeword` (optional install)
- Falls back to `SpeechRecognition`-based keyword detection automatically if openwakeword is unavailable

### Phase 10 — Proactive Intelligence
- `ProactiveMonitor` runs as a background `QThread`, checking every 60 seconds:
  - 🔋 Low battery warning (< 20%, discharging)
  - 🔥 High CPU usage alert (> 85% sustained)
  - ⏰ Due reminder notifications (from memory database)
  - 🌅 Daily 9 AM briefing (top news, weather, reminders)
  - 🔔 GitHub notification pings (if GitHub skill is configured)

---

## Architecture

```
User Input (Text / Voice / Wake Word)
         │
         ▼
JarvisCoreController  (app/core.py)
         │
         ├─── ConfigManager          → ~/.jarvis_ai/jarvis_config.json
         ├─── SecurityAuditLogger    → Audit log for dangerous commands
         ├─── DatabaseMemory         → SQLite (messages + memory facts)
         ├─── MemoryManager          → Fact extraction + context injection
         ├─── ComputerAutomation     → 20+ OS control commands
         ├─── WebSearchEngine        → DuckDuckGo (ddgs)
         ├─── TextToSpeechEngine     → edge-tts / pyttsx3
         ├─── SpeechToTextListener   → Google SpeechRecognition
         ├─── ToolRegistry           → Calculator, system info
         ├─── SkillRegistry          → Weather, Spotify, GitHub
         │
         ├─── AIProviderInterface ◄── GeminiProvider
         │                       ◄── OpenAIProvider
         │                       ◄── OllamaProvider
         │                       ◄── MockProvider (offline/testing)
         │
         ├─── CameraVision           → OpenCV + Gemini Vision
         ├─── ScreenVision           → PIL screenshot + Gemini Vision
         │
         ├─── LocalKnowledgeIndexer  → TF-IDF indexer (PDF, code, md, txt)
         ├─── RAGRetriever           → Context retrieval from SQLite index
         │
         ├─── AgentPlanner           → Intent router (priority-based)
         │         ├── ResearcherSpecialist   → DuckDuckGo synthesis
         │         ├── AutomationSpecialist   → OS command dispatcher
         │         └── CoderSpecialist        → Code generation / git
         │
         ├─── TaskExecutor           → Multi-step plan execution (Agent Mode)
         │
         └─── ProactiveMonitor       → Background QThread (60s intervals)
```

**Routing priority** (highest to lowest):
`AgentMode` → `SkillAgent` → `VisionAgent` → `RAGAgent` → `AutomationAgent` → `ResearcherAgent` → `CoderAgent` → `MemoryAgent` → `CoreAssistant`

---

## Project Structure

```
Jarvis/
├── agents/
│   ├── planner.py          # Multi-agent orchestrator & intent router
│   ├── specialists.py      # ResearcherSpecialist, AutomationSpecialist, CoderSpecialist
│   └── task_executor.py    # Multi-step plan parser & sequential executor
│
├── ai/
│   ├── provider_interface.py   # Abstract base class for all AI providers
│   ├── gemini_provider.py      # Google Gemini (google-genai SDK)
│   ├── openai_provider.py      # OpenAI-compatible (gpt-4o-mini etc.)
│   ├── ollama_provider.py      # Local Ollama (llama3 etc.)
│   └── mock_provider.py        # Offline mock for testing
│
├── app/
│   ├── core.py             # JarvisCoreController — central orchestrator
│   └── config_manager.py   # JSON config r/w → ~/.jarvis_ai/jarvis_config.json
│
├── assets/
│   ├── jarvis_icon.ico
│   ├── jarvis_icon.png
│   └── jarvis_orb.gif
│
├── automation/
│   ├── os_control.py           # ComputerAutomation — all OS commands
│   └── workspace_presets.py    # Predefined multi-app workspace layouts
│
├── memory/
│   ├── db.py               # DatabaseMemory — SQLite (messages + facts)
│   └── memory_manager.py   # Regex fact extraction, recall, context injection
│
├── proactive/
│   └── monitor.py          # ProactiveMonitor QThread — battery, CPU, reminders
│
├── rag/
│   ├── indexer.py          # LocalKnowledgeIndexer — TF-IDF over local files
│   └── retriever.py        # RAGRetriever — query → relevant chunks → LLM
│
├── search/
│   ├── web_search.py       # DuckDuckGo search engine wrapper
│   └── dynamic_feed.py     # News, trends, tech, video, briefing feeds
│
├── security/
│   └── audit.py            # SecurityAuditLogger — logs sensitive commands
│
├── skills/
│   ├── base_skill.py       # BaseSkill abstract class
│   ├── skill_registry.py   # SkillRegistry — auto-discovers & routes skills
│   ├── weather_skill.py    # Open-Meteo real-time weather (no API key)
│   ├── spotify_skill.py    # Spotify media keys + URI playback
│   └── github_skill.py     # GitHub REST API (repos, PRs, issues, commits)
│
├── speech/
│   ├── tts.py              # TextToSpeechEngine (edge-tts + pyttsx3 fallback)
│   ├── stt.py              # SpeechToTextListener (Google SpeechRecognition)
│   └── wake_word.py        # WakeWordListener (openwakeword + fallback)
│
├── tools/
│   ├── registry.py         # ToolRegistry — calculator, system info
│   ├── base_tool.py        # BaseTool abstract class
│   └── web_agent.py        # Playwright-based web interaction tool
│
├── ui/
│   ├── main_window.py      # MainWindow — chat, tabs, settings, memory panel
│   ├── styles.py           # DARK_GLASS_STYLESHEET (Raycast/Linear-inspired)
│   └── components/
│       ├── chat_bubble.py          # Markdown-rendered chat messages
│       ├── command_palette.py      # Spotlight-style command search
│       ├── dynamic_panel.py        # News/video/trends workspace panel
│       ├── floating_orb_window.py  # Always-on-top orb mode
│       ├── floating_widget.py      # Floating corner widget
│       ├── jarvis_orb_widget.py    # Animated GIF orb with pulse effects
│       └── screen_picker_dialog.py # Screen region selector for vision
│
├── utils/
│   └── fuzzy_match.py      # Typo-tolerant keyword matching for routing
│
├── vision/
│   ├── camera.py           # CameraVision — OpenCV webcam + Gemini Vision
│   └── screen_vision.py    # ScreenVision — PIL screenshot + Gemini Vision
│
├── run.py                  # Entry point
├── run.spec                # PyInstaller spec for building .exe
├── build_exe.bat           # One-click build script
└── requirements.txt
```

---

## Installation

### Prerequisites
- **Python 3.10+** — [Download](https://python.org/downloads/)
- **Windows 10 or 11** (some automation features are Windows-only)
- A microphone (for voice input) — optional but recommended

### 1. Clone the Repository

```bash
git clone https://github.com/ashwin2k23/Jarvis.git
cd Jarvis
```

### 2. Install Core Dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Enable Wake Word Detection

```bash
pip install openwakeword pyaudio
```

> If `pyaudio` fails to install, download the matching `.whl` from  
> [Unofficial Windows Binaries for Python](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install manually.

### 4. Run Jarvis

```bash
python run.py
```

---

## Configuration

Config is stored at `~/.jarvis_ai/jarvis_config.json` — created automatically on first run.

### Key Settings

| Key | Default | Description |
|-----|---------|-------------|
| `ai_provider` | `"mock"` | Active AI backend: `"gemini"`, `"openai"`, `"ollama"`, `"mock"` |
| `gemini_api_key` | `""` | Your Google Gemini API key |
| `gemini_model` | `"gemini-2.0-flash"` | Gemini model to use |
| `openai_api_key` | `""` | Your OpenAI API key |
| `openai_model` | `"gpt-4o-mini"` | OpenAI model to use |
| `ollama_url` | `"http://localhost:11434"` | Ollama server URL |
| `ollama_model` | `"llama3"` | Ollama model name |
| `tts_enabled` | `true` | Enable text-to-speech |
| `tts_voice_id` | `"en-US-ChristopherNeural"` | Voice for edge-tts |
| `tts_voice_rate` | `180` | Speech rate (words per minute) |
| `stt_enabled` | `true` | Enable speech-to-text input |
| `user_name` | `"User"` | Your name (used in responses) |
| `assistant_name` | `"Jarvis"` | Assistant's name |
| `github_token` | `""` | GitHub Personal Access Token |
| `github_username` | `""` | Your GitHub username |
| `auto_speak_responses` | `true` | Auto-speak every AI response |
| `safe_command_execution` | `true` | Confirm dangerous commands |
| `enable_proactive_monitor` | `true` | Run background monitor |

All settings are also editable live from the **Settings** tab inside the app.

---

## AI Providers

| Provider | Model | Setup | Notes |
|----------|-------|-------|-------|
| **Gemini** ⭐ | `gemini-2.0-flash` | [Get API key](https://aistudio.google.com/app/apikey) | Recommended — fast, multimodal, free tier |
| **OpenAI** | `gpt-4o-mini` | [Get API key](https://platform.openai.com/api-keys) | GPT-4o and gpt-4o-mini supported |
| **Ollama** | `llama3`, `mistral`, etc. | [Install Ollama](https://ollama.com) | Fully local, no internet required |
| **Mock** | — | None | Offline/testing mode; echoes prompts |

> **Fallback behavior**: If the configured provider is unavailable or the API key is missing, Jarvis automatically falls back to `MockProvider` and prints a warning.

---

## Usage Examples

### General Conversation
```
You: What's the capital of Japan?
You: Summarize the French Revolution in 5 bullet points
You: Write a professional email declining a meeting
```

### Memory
```
You: Remember that my project deadline is next Friday
You: My name is Alex and I'm a software engineer at Google
You: What do you know about my project?
You: Forget my deadline
```

### Desktop Automation
```
You: Open VS Code
You: Close Spotify
You: Take a screenshot
You: Set brightness to 60
You: Shutdown PC
You: Lock my computer
You: Open YouTube and search for Python tutorials
You: Empty the recycle bin
You: Toggle night light
```

### Vision
```
You: What do you see?              → webcam capture + description
You: Read this document            → webcam document OCR
You: Analyze my screen             → desktop screenshot analysis
You: Explain this error on screen  → error message explanation
You: Read code on screen           → code reading + explanation
You: Detect UI bugs                → UI issue detection
```

### Local Knowledge Base (RAG)
```
You: Search my project for the authentication function
You: What does my README say about installation?
You: Find the database schema in my files
You: Summarize my PDF report
```
*(First, index a folder in Settings → Knowledge Base tab)*

### Agent Mode (Multi-step)
```
You: Create a React app, install dependencies, and open it in VS Code
You: Search for Python best practices, summarize them, and save to a file
You: Check my GitHub notifications then open my browser
```

### Skills
```
You: What's the weather in Paris?
You: What's the temperature tomorrow in London?
You: Play Blinding Lights on Spotify
You: Pause music
You: Skip to the next song
You: Show my GitHub notifications
You: List my repositories
You: Show open pull requests in my-project
You: Create an issue fix login bug in my-repo
You: Show recent commits in jarvis
```

### Coding
```
You: Explain this Python code: [paste code]
You: Write unit tests for this function
You: What's wrong with this SQL query?
You: Refactor this into async/await
You: Generate documentation for this class
```

### System Tools
```
You: What's my CPU and RAM usage?
You: System status
You: Calc 15 * 8 + 22 / 2
You: Calculate sqrt(144)
```

---

## Agent Routing

Jarvis uses a **priority-based intent router** (`AgentPlanner`) with fuzzy/typo-tolerant matching:

```
Priority 0  AgentMode       → Detected multi-step / complex requests
Priority 1  SkillAgent      → "weather", "spotify", "github", etc.
Priority 2  VisionAgent     → "analyze screen", "what do you see", etc.
Priority 3  RAGAgent        → "search my files", "in my project", etc.
Priority 4  AutomationAgent → "open", "close", "shutdown", "brightness", etc.
Priority 5  ResearcherAgent → Web questions → DuckDuckGo → LLM synthesis
Priority 6  CoderAgent      → Code, git, debugging, architecture questions
Priority 7  MemoryAgent     → "do you remember", "what did I tell you", etc.
Priority 8  CoreAssistant   → General conversation (default fallback)
```

All routing keywords use **fuzzy matching** (`utils/fuzzy_match.py`) to handle typos — e.g., `"opn vs code"`, `"githb notifications"`, `"wether in tokyo"` all route correctly.

---

## Skills / Plugins

### Adding a Custom Skill

1. Create a new file in `skills/` inheriting from `BaseSkill`:

```python
from skills.base_skill import BaseSkill
from typing import List

class MyCustomSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "my_skill"

    @property
    def description(self) -> str:
        return "Does something useful."

    @property
    def triggers(self) -> List[str]:
        return ["my keyword", "another trigger"]

    def execute(self, user_input: str, core=None) -> str:
        return "Hello from my custom skill!"
```

2. Register it in `skills/skill_registry.py`:

```python
from skills.my_custom_skill import MyCustomSkill
# In SkillRegistry.__init__:
self.register(MyCustomSkill())
```

---

## Memory System

Jarvis automatically extracts these fact types from natural language:

| Category | Examples |
|----------|---------|
| **Personal** | Name, age, location |
| **Work** | Employer, role, internship, deadlines |
| **Projects** | Current project, tech stack, programming language |
| **Preferences** | Likes, dislikes, favorite tools |
| **Reminders** | Remind me to…, Remember that… |
| **Events** | Meeting on Monday, exam starts next week |

All facts are stored in SQLite (`~/.jarvis_ai/jarvis_memory.db`) and injected into every LLM system prompt as context, so Jarvis always "remembers" what you've told it — across sessions.

---

## Desktop Automation

Full list of supported OS commands:

| Category | Commands |
|----------|---------|
| **Apps** | Open/close any installed app by name |
| **Browser** | Open URL, search Google, search YouTube |
| **Power** | Shutdown, restart, sleep, hibernate, lock |
| **Display** | Set brightness (0–100), toggle Night Light, switch monitor mode |
| **Network** | Toggle Wi-Fi, toggle Bluetooth |
| **Audio** | Set volume, mute, unmute, volume up/down |
| **Files** | Open Downloads, Documents, Desktop, Recycle Bin |
| **System** | Screenshot, record screen, empty Recycle Bin, system info |
| **Terminal** | Run any shell command |
| **Clipboard** | Read/write clipboard contents |

App resolution order: Windows Protocol URIs → Start Menu shortcuts → Common install paths → Direct `.exe` name

---

## Vision Capabilities

### Camera Vision (`CameraVision`)
Uses OpenCV to capture webcam frames, then sends to Gemini Vision API.

| Command | What Jarvis Does |
|---------|-----------------|
| `"What do you see?"` | Describes everything in the webcam frame |
| `"Read this document"` | OCR-style reading of a document held up to camera |
| `"Describe this image"` | General image description |
| `"Analyze for errors"` | Looks for visual bugs, defects, or issues |

### Screen Vision (`ScreenVision`)
Uses PIL `ImageGrab` to capture the desktop, then sends to Gemini Vision API.

| Command | What Jarvis Does |
|---------|-----------------|
| `"Analyze my screen"` | Full desktop analysis |
| `"Explain this error"` | Explains visible error dialogs or stack traces |
| `"Read code on screen"` | Reads and explains visible source code |
| `"Detect UI bugs"` | Identifies visual UI issues in the app on screen |
| `"Summarize PDF [path]"` | Extracts and summarizes PDF via pdfplumber |

---

## RAG (Local Knowledge Base)

### How to Index Files

**From the UI**: Settings → Knowledge Base → Select folder or file → Index

**From Python**:
```python
# Index a whole folder
core.index_knowledge_folder("C:/Users/you/Documents/MyProject")

# Index a single file
core.index_knowledge_file("C:/reports/annual_report.pdf")
```

### Supported File Types
| Type | Extension | Parser |
|------|-----------|--------|
| Python | `.py` | Plain text |
| Markdown | `.md` | Plain text |
| Plain text | `.txt` | Plain text |
| PDF | `.pdf` | pdfplumber |

### How it Works
1. Files are chunked into passages (~500 chars with overlap)
2. TF-IDF vectors are computed and stored in SQLite
3. At query time, the top-K most relevant chunks are retrieved
4. Chunks are sent to the LLM as context for a grounded answer

---

## Proactive Intelligence

`ProactiveMonitor` runs every 60 seconds in the background:

| Check | Trigger | Alert |
|-------|---------|-------|
| **Battery** | < 20% and discharging | `"⚡ Low Battery: X% remaining"` |
| **CPU** | > 85% for 2+ consecutive checks | `"🔥 High CPU: X% — consider closing heavy apps"` |
| **Reminders** | Reminder due today (from memory DB) | `"⏰ Reminder: [your note]"` |
| **Daily briefing** | 9:00 AM, once per day | Top news + weather + reminders summary |
| **GitHub** | Unread notifications | `"🔔 You have N unread GitHub notifications"` |

All alerts appear as native desktop notifications and are also shown in the Jarvis chat panel.

---

## Building an Executable

Build a standalone Windows `.exe` using PyInstaller:

```bash
pip install pyinstaller
pyinstaller run.spec
```

Or use the included batch script:
```bash
build_exe.bat
```

Output: `dist/JarvisAI/JarvisAI.exe`

The spec file (`run.spec`) includes all required hidden imports and bundles the `assets/` folder automatically.

---

## Contributing

Contributions are welcome! Here are some good starting points:

- Add new **Skills** (see [Adding a Custom Skill](#adding-a-custom-skill))
- Add support for new **AI providers** (implement `AIProviderInterface`)
- Improve **intent routing** in `agents/planner.py`
- Add **Linux/macOS** support to `automation/os_control.py`
- Expand **RAG** to support more file types (`.docx`, `.xlsx`, `.html`)
- Add new **fact extraction patterns** to `memory/memory_manager.py`

### Steps
1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## Requirements

See [`requirements.txt`](requirements.txt) for the full list. Core dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| `PySide6` | ≥ 6.5.0 | Desktop UI framework |
| `google-genai` | ≥ 2.0.0 | Gemini AI provider |
| `openai` | ≥ 1.0.0 | OpenAI provider |
| `requests` | ≥ 2.28.0 | HTTP for GitHub/weather APIs |
| `SpeechRecognition` | ≥ 3.10.0 | Voice input |
| `pyttsx3` | ≥ 2.90 | Offline TTS fallback |
| `ddgs` | ≥ 9.0.0 | DuckDuckGo web search |
| `psutil` | ≥ 5.9.0 | System monitoring |
| `opencv-python` | ≥ 4.8.0 | Camera vision |
| `Pillow` | ≥ 9.5.0 | Screenshot capture |
| `pdfplumber` | ≥ 0.10.0 | PDF text extraction |

**Optional:**
| Package | Purpose |
|---------|---------|
| `openwakeword` | Offline "Hey Jarvis" wake word |
| `pyaudio` | Microphone input for wake word |

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ❤️ using Python · PySide6 · Gemini · SQLite

</div>
]]>
