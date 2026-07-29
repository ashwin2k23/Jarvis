import os
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "ai_provider": "mock",  # 'gemini', 'openai', 'ollama', or 'mock'
    "gemini_api_key": "",
    "gemini_model": "gemini-2.0-flash",
    "openai_api_key": "",
    "openai_model": "gpt-4o-mini",
    "ollama_url": "http://localhost:11434",
    "ollama_model": "llama3",
    "tts_enabled": True,
    "tts_voice_id": "en-US-ChristopherNeural",
    "tts_voice_rate": 180,
    "tts_volume": 1.0,
    "stt_enabled": True,
    "theme": "dark_glass",
    "user_name": "Ashwin",
    "preferred_name": "Ash",
    "assistant_name": "Jarvis",
    "github_token": "",
    "github_username": "ashwin2k23",
    "auto_speak_responses": True,
    "safe_command_execution": True,
    "web_search_enabled": True
}

class ConfigManager:
    """Manages persistent application settings stored in user's home directory or local data folder."""
    
    def __init__(self, config_filename="jarvis_config.json"):
        self.config_dir = Path(os.path.expanduser("~")) / ".jarvis_ai"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.config_dir / config_filename
        self.config = self.load_config()

    def load_config(self) -> dict:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge with default config to ensure new keys exist
                    merged = DEFAULT_CONFIG.copy()
                    merged.update(data)
                    return merged
            except Exception as e:
                print(f"[ConfigManager] Error loading config, using defaults: {e}")
                return DEFAULT_CONFIG.copy()
        else:
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

    def save_config(self, config_data: dict = None) -> bool:
        if config_data is not None:
            self.config = config_data
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"[ConfigManager] Failed to save config: {e}")
            return False

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
