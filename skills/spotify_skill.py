"""
skills/spotify_skill.py — Phase 7: Spotify Control Skill
Controls Spotify desktop app via keyboard media keys and Windows automation.
No API key required — works with the Spotify desktop app.
"""
import subprocess
import re
from typing import List
from skills.base_skill import BaseSkill


class SpotifySkill(BaseSkill):
    """Controls Spotify desktop app using keyboard hotkeys and subprocess."""

    @property
    def name(self) -> str:
        return "spotify"

    @property
    def description(self) -> str:
        return "Controls Spotify: play, pause, skip, previous, volume. Works with the Spotify desktop app."

    @property
    def triggers(self) -> List[str]:
        return [
            "spotify", "play music", "pause music", "skip song", "next song",
            "previous song", "stop music", "resume music", "play song",
            "music volume", "play track"
        ]

    def execute(self, user_input: str, core=None) -> str:
        text_lower = user_input.lower()

        # Open Spotify first if not running
        if "open spotify" in text_lower:
            return self._launch_spotify()

        elif any(w in text_lower for w in ["pause", "stop music"]):
            return self._media_key("pause")

        elif any(w in text_lower for w in ["play", "resume"]):
            # Check if there's a specific song/artist mentioned
            track = self._extract_track(user_input)
            if track:
                return self._search_and_play(track)
            return self._media_key("play")

        elif any(w in text_lower for w in ["next", "skip"]):
            return self._media_key("next")

        elif any(w in text_lower for w in ["previous", "prev", "back", "last"]):
            return self._media_key("previous")

        elif "shuffle" in text_lower:
            return self._spotify_action("shuffle")

        elif any(w in text_lower for w in ["volume up", "louder"]):
            return self._spotify_volume("up")

        elif any(w in text_lower for w in ["volume down", "quieter"]):
            return self._spotify_volume("down")

        return "Spotify: try 'play music', 'pause', 'skip song', 'previous song', or 'open spotify'."

    def _launch_spotify(self) -> str:
        """Launches the Spotify desktop app."""
        try:
            subprocess.Popen(["spotify.exe"], shell=True)
            return "🎵 Opening Spotify..."
        except Exception:
            import os
            os.system('start spotify')
            return "🎵 Opening Spotify..."

    def _media_key(self, action: str) -> str:
        """Sends media keys via PowerShell."""
        key_map = {
            "play":     173,  # VK_MEDIA_PLAY_PAUSE (toggle)
            "pause":    173,
            "next":     176,  # VK_MEDIA_NEXT_TRACK
            "previous": 177,  # VK_MEDIA_PREV_TRACK
        }
        vk = key_map.get(action, 173)
        try:
            cmd = f"(New-Object -ComObject WScript.Shell).SendKeys([char]{vk})"
            subprocess.run(['powershell', '-Command', cmd], capture_output=True, timeout=3)
            labels = {"play": "▶️ Playing", "pause": "⏸️ Paused", "next": "⏭️ Skipped to next track", "previous": "⏮️ Went back to previous track"}
            return f"Spotify: {labels.get(action, action.title())}"
        except Exception as e:
            return f"Spotify key error: {e}"

    def _search_and_play(self, track: str) -> str:
        """Opens Spotify search URI for a track (launches Spotify app)."""
        try:
            import urllib.parse
            query = urllib.parse.quote(track)
            import webbrowser
            webbrowser.open(f"spotify:search:{query}")
            return f"🎵 Searching Spotify for: **{track}**"
        except Exception as e:
            return f"Spotify search error: {e}"

    def _spotify_action(self, action: str) -> str:
        """Generic Spotify URI action."""
        try:
            import webbrowser
            webbrowser.open(f"spotify:{action}")
            return f"Spotify: {action.title()} toggled."
        except Exception as e:
            return f"Spotify action error: {e}"

    def _spotify_volume(self, direction: str) -> str:
        """Adjusts system volume (which affects Spotify)."""
        try:
            steps = 5
            key = 175 if direction == "up" else 174  # VK_VOLUME_UP / VK_VOLUME_DOWN
            ps_cmd = f"1..{steps} | ForEach-Object {{ (New-Object -ComObject WScript.Shell).SendKeys([char]{key}) }}"
            subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True)
            return f"🎵 Spotify volume {'increased' if direction == 'up' else 'decreased'}."
        except Exception as e:
            return f"Volume error: {e}"

    def _extract_track(self, text: str) -> str:
        """Extracts a song/artist name from phrases like 'play Shape of You'."""
        patterns = [
            r'play\s+(?:song\s+)?(?:called\s+)?["\']?(.+?)["\']?\s*(?:by\s+.+)?$',
            r'play\s+(.+)\s+by\s+',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                track = m.group(1).strip()
                filler = ["music", "song", "track", "spotify", "the"]
                for f in filler:
                    track = re.sub(rf'\b{f}\b', '', track, flags=re.IGNORECASE).strip()
                if len(track) > 2:
                    return track
        return ""
