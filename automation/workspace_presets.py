import os
import subprocess
import psutil
from typing import Dict, Any

class WorkspacePresetManager:
    """Manages system presets (Work Mode, Gaming Mode, Dev Mode, Focus Mode)."""

    PRESETS: Dict[str, Dict[str, Any]] = {
        "work": {
            "name": "Work Mode",
            "launch_apps": ["code", "chrome"],
            "volume": 30,
            "brightness": 80,
            "night_light": False,
            "description": "Launches VS Code & Chrome, sets comfortable volume and brightness."
        },
        "gaming": {
            "name": "Gaming Mode",
            "launch_apps": ["discord", "steam"],
            "close_apps": ["code", "slack", "postman"],
            "volume": 70,
            "brightness": 90,
            "description": "Launches Gaming apps, closes dev tools, increases volume."
        },
        "dev": {
            "name": "Dev Mode",
            "launch_apps": ["code", "wt.exe"],
            "volume": 20,
            "brightness": 85,
            "description": "Opens VS Code & Windows Terminal, sets quiet volume."
        },
        "focus": {
            "name": "Focus Mode",
            "close_apps": ["discord", "spotify", "chrome"],
            "volume": 0,
            "brightness": 65,
            "night_light": True,
            "description": "Mutes audio, turns on Night Light, closes distracting apps."
        }
    }

    def __init__(self, computer_automation=None):
        self.automation = computer_automation

    def apply_preset(self, preset_key: str) -> str:
        key = preset_key.lower().strip()
        if key not in self.PRESETS:
            available = ", ".join(self.PRESETS.keys())
            return f"⚠️ Unknown preset '{preset_key}'. Available presets: {available}"

        preset = self.PRESETS[key]
        logs = [f"🚀 Applying **{preset['name']}**..."]

        if self.automation:
            # 1. Close apps if specified
            if "close_apps" in preset:
                for app in preset["close_apps"]:
                    res = self.automation.close_app(app)
                    logs.append(f"  • {res}")

            # 2. Launch apps if specified
            if "launch_apps" in preset:
                for app in preset["launch_apps"]:
                    res = self.automation.launch_app(app)
                    logs.append(f"  • {res}")

            # 3. Set volume if specified
            if "volume" in preset:
                res = self.automation.set_volume(preset["volume"])
                logs.append(f"  • {res}")

            # 4. Set brightness if specified
            if "brightness" in preset:
                res = self.automation.set_brightness(preset["brightness"])
                logs.append(f"  • {res}")

            # 5. Night light toggle
            if preset.get("night_light"):
                res = self.automation.toggle_night_light()
                logs.append(f"  • {res}")

        return "\n".join(logs)
