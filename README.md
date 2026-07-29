<![CDATA[<div align="center">

# 🤖 Jarvis AI Desktop Assistant

**A powerful, extensible AI assistant for your desktop — built with Python & PySide6**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![PySide6](https://img.shields.io/badge/UI-PySide6%20%28Qt%29-green)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightblue)](https://www.microsoft.com/windows)

</div>

---

## Overview

Jarvis is a feature-rich, OS-level desktop AI assistant. It combines a sleek glassmorphism UI with a modular backend supporting multiple AI providers, long-term memory, voice interaction, screen understanding, local RAG, agent mode, and more.

---

## ✨ Features

| Phase | Feature | Description |
|-------|---------|-------------|
| 1 | **Long-Term Memory** | Extracts facts from conversations (names, dates, preferences, reminders). Injects context into every LLM response. |
| 2 | **Desktop Automation** | Launch/close apps, control brightness, toggle Night Light / Wi-Fi / Bluetooth, shutdown, sleep, record screen. |
| 3 | **Camera Vision** | Webcam capture → Gemini Vision. Describe objects, read documents, analyze images. |
| 4 | **Screen Understanding** | Real-time screenshot → Gemini Vision. Explain UI errors, read code, summarize visible content. |
| 5 | **Local Knowledge Base (RAG)** | Index local folders (PDFs, code, markdown). TF-IDF retrieval — zero ML dependencies. |
| 6 | **Agent Mode** | LLM-powered multi-step planning. Give a high-level goal; Jarvis breaks it into steps and executes each one. |
| 7 | **Skills / Plugins** | Modular skill system. Built-in: Weather (no API key), Spotify (media keys + URI), GitHub (full REST API). |
| 8 | **Coding Copilot** | Explain code, generate files, fix bugs, refactor, run git commands, generate unit tests and docs. |
| 9 | **Wake Word** | "Hey Jarvis" offline detection via `openwakeword`. Falls back to `SpeechRecognition` automatically. |
| 10 | **Proactive Intelligence** | Background monitor: low battery alerts, high CPU warnings, daily 9 AM briefing, reminder notifications. |

---

## 🏗️ Architecture

```
JarvisCoreController
├── DatabaseMemory          (SQLite)
├── MemoryManager           (fact extraction + context injection)
├── ComputerAutomation      (20+ OS commands)
├── WebSearchEngine         (DuckDuckGo)
├── GeminiProvider / OpenAIProvider / OllamaProvider / MockProvider
├── CameraVision            (OpenCV → Gemini Vision)
├── ScreenVision            (screenshot → Gemini Vision)
├── LocalKnowledgeIndexer + RAGRetriever
├── SkillRegistry
│   ├── WeatherSkill        (Open-Meteo, no API key)
│   ├── SpotifySkill        (media keys + URI playback)
│   └── GitHubSkill         (repos, PRs, issues, commits, notifications)
├── AgentPlanner
│   ├── ResearcherSpecialist
│   ├── AutomationSpecialist
│   └── CoderSpecialist
├── TaskExecutor            (multi-step agent execution)
├── ProactiveMonitor        (background QThread, 60s intervals)
└── TextToSpeechEngine + SpeechToTextListener + WakeWordListener
```

---

## 📁 Project Structure

```
Jarvis/
├── agents/         # Agent planner, specialists, task executor
├── ai/             # AI provider adapters (Gemini, OpenAI, Ollama, Mock)
├── app/            # Core controller & config manager
├── assets/         # Icons, images, animations
├── automation/     # OS automation & workspace presets
├── memory/         # SQLite memory DB & memory manager
├── proactive/      # Background monitor thread
├── rag/            # Local knowledge base indexer & retriever
├── search/         # Web search (DuckDuckGo) & dynamic feed
├── security/       # Audit logging
├── skills/         # Skill registry + built-in skills
├── speech/         # TTS, STT & wake word detection
├── tools/          # Tool registry & web agent
├── ui/             # PySide6 main window & components
├── utils/          # Fuzzy matching & helpers
├── vision/         # Camera & screen capture
├── run.py          # Entry point
└── requirements.txt
```

---

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/ashwin2k23/Jarvis.git
cd Jarvis
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Enable wake word detection

```bash
pip install openwakeword pyaudio
```

### 4. Run Jarvis

```bash
python run.py
```

### 5. Configure in Settings tab

- **AI Provider** — Choose Gemini (recommended), OpenAI, Ollama, or Mock
- **API Key** — Enter your Gemini / OpenAI API key
- **GitHub PAT** — Required for GitHub skill ([create one here](https://github.com/settings/tokens))
- **Voice** — Enable/disable TTS & STT
- **Wake Word** — Enable "Hey Jarvis" detection
- **Proactive Monitor** — Enable background intelligence

---

## 🤖 AI Providers

| Provider | Model | Notes |
|----------|-------|-------|
| **Gemini** | `gemini-2.0-flash` | Recommended — fast & multimodal |
| **OpenAI** | `gpt-4o-mini` | Requires API key |
| **Ollama** | `llama3` | Local inference, no internet needed |
| **Mock** | — | Offline testing / demo mode |

---

## 💬 Usage Examples

| You say... | Jarvis does... |
|-----------|----------------|
| "Remember my meeting is at 3 PM on Friday" | Saves to long-term memory, recalls on demand |
| "What's the weather in Tokyo?" | Fetches live weather — no API key needed |
| "Open VS Code" | Launches the application |
| "Shutdown PC" | Issues `shutdown /s /t 10` |
| "Set brightness to 70" | Adjusts display brightness via WMI |
| "What do you see?" | Captures webcam, describes via Gemini Vision |
| "Analyze my screen" | Screenshots desktop, returns AI analysis |
| "Search my project for the login function" | RAG-searches your indexed local files |
| "Build a React app, init git, open VS Code" | Agent Mode — executes all steps sequentially |
| "Play Blinding Lights on Spotify" | Spotify URI search + playback |
| "Show my GitHub notifications" | Lists unread GitHub notifications via API |
| "Write unit tests for this function" | Generates pytest test code |
| "Hey Jarvis" | Activates Jarvis hands-free |

---

## 🛠️ Building an Executable

```bash
pip install pyinstaller
pyinstaller run.spec
```

Output: `dist/JarvisAI/JarvisAI.exe`

---

## 📋 Requirements

- Python 3.10+
- Windows 10/11
- See [`requirements.txt`](requirements.txt) for full dependency list

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
]]>
