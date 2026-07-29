import threading
import queue
import asyncio
import tempfile
import os
import time
import re

def clean_text_for_speech(text: str) -> str:
    """
    Sanitizes response text into clean, natural spoken English.
    Strips raw URLs, query strings, markdown code blocks/formatting, emojis, and paths.
    """
    if not text or not text.strip():
        return ""

    # 1. Convert specific action URLs into natural spoken phrases
    # e.g., "Opened: https://www.google.com/search?q=the+mentalist" -> "Opened Google search for the mentalist"
    text = re.sub(
        r'https?://(?:www\.)?google\.com/search\?q=([^+&\s]+(?:\+[^+&\s]+)*)',
        lambda m: f"Google search for {m.group(1).replace('+', ' ')}",
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(
        r'https?://(?:www\.)?youtube\.com/results\?search_query=([^+&\s]+(?:\+[^+&\s]+)*)',
        lambda m: f"YouTube search for {m.group(1).replace('+', ' ')}",
        text,
        flags=re.IGNORECASE
    )

    # 2. Convert "Opened in [Browser]: https://..." -> "Opened search in [Browser]"
    text = re.sub(r'Opened\s+in\s+([A-Za-z]+):\s+https?://\S+', r'Opened search in \1', text, flags=re.IGNORECASE)
    text = re.sub(r'Opened:\s+https?://\S+', 'Opened website', text, flags=re.IGNORECASE)

    # 3. Strip Markdown links [Label](url) -> Label
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # 4. Remove any remaining raw URLs (http://..., https://..., www....)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)

    # 5. Remove file system paths (e.g. C:\Users\... or /home/...)
    text = re.sub(r'[A-Za-z]:\\[^\s]+', 'file', text)

    # 6. Strip Markdown code blocks (```...```) and inline code (`...`)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)

    # 7. Strip Markdown symbols (*, _, #, ~, >, |, -, •)
    text = re.sub(r'[\*\_\#\~\>\|\-\•]', ' ', text)

    # 8. Remove Emojis & special non-printable symbols (keep alphanumeric, space, standard punctuation)
    text = re.sub(r'[^\w\s\.,\?!\'"]', '', text)

    # 9. Clean up excess whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # 10. Cap spoken text length (max 180 chars for snappy speech response)
    if len(text) > 180:
        cutoff = text[:180]
        last_space = cutoff.rfind(' ')
        if last_space > 40:
            text = cutoff[:last_space] + '...'
        else:
            text = cutoff + '...'

    return text


class TextToSpeechEngine:
    """Multi-engine Text-To-Speech engine supporting Microsoft Edge Neural AI voices and pyttsx3 SAPI5 voices."""

    EDGE_VOICES = [
        {"id": "en-US-ChristopherNeural", "name": "[Edge Neural] Christopher (US Male)", "type": "edge"},
        {"id": "en-US-GuyNeural", "name": "[Edge Neural] Guy (US Male)", "type": "edge"},
        {"id": "en-US-AvaNeural", "name": "[Edge Neural] Ava (US Female)", "type": "edge"},
        {"id": "en-US-JennyNeural", "name": "[Edge Neural] Jenny (US Female)", "type": "edge"},
        {"id": "en-US-AriaNeural", "name": "[Edge Neural] Aria (US Female)", "type": "edge"},
        {"id": "en-US-AndrewNeural", "name": "[Edge Neural] Andrew (US Male)", "type": "edge"},
        {"id": "en-GB-RyanNeural", "name": "[Edge Neural] Ryan (UK Male)", "type": "edge"},
        {"id": "en-GB-SoniaNeural", "name": "[Edge Neural] Sonia (UK Female)", "type": "edge"},
        {"id": "en-AU-WilliamMultilingualNeural", "name": "[Edge Neural] William (AU Male)", "type": "edge"},
        {"id": "en-IN-NeerjaNeural", "name": "[Edge Neural] Neerja (IN Female)", "type": "edge"},
        {"id": "en-IN-PrabhatNeural", "name": "[Edge Neural] Prabhat (IN Male)", "type": "edge"},
    ]

    def __init__(self, rate: int = 180, volume: float = 1.0, voice_id: str = "en-US-ChristopherNeural"):
        self.rate = rate
        self.volume = volume
        self.voice_id = voice_id if voice_id else "en-US-ChristopherNeural"
        self.queue = queue.Queue()
        self.is_running = True
        self.stop_requested = False
        self.pyttsx_engine = None
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    @classmethod
    def get_available_voices(cls) -> list:
        """Returns combined list of Edge Neural Voices and local System SAPI5 voices."""
        voices = list(cls.EDGE_VOICES)
        
        try:
            import pyttsx3
            eng = pyttsx3.init()
            sapi_voices = eng.getProperty('voices')
            for v in sapi_voices:
                voices.append({
                    "id": v.id,
                    "name": f"💻 System (Offline): {v.name}",
                    "type": "sapi5"
                })
        except Exception as e:
            print(f"[TTS] SAPI5 voice enumeration notice: {e}")

        return voices

    def set_voice(self, voice_id: str):
        if voice_id:
            self.voice_id = voice_id

    def set_rate(self, rate: int):
        self.rate = rate

    def _worker(self):
        # Pre-initialize pygame mixer to eliminate audio lag
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            pass

        while self.is_running:
            try:
                text = self.queue.get(timeout=0.5)
                if text is None:
                    break

                self.stop_requested = False
                self._process_speak_request(text)
                self.queue.task_done()
            except queue.Empty:
                continue

    def _process_speak_request(self, text: str):
        if self.stop_requested or not text:
            return

        is_sapi = "Offline" in self.voice_id or "HKEY_LOCAL_MACHINE" in self.voice_id
        is_edge = not is_sapi and ("Neural" in self.voice_id or self.voice_id.startswith("en-"))

        if is_edge:
            try:
                self._speak_edge_neural(text)
                return
            except Exception as e:
                print(f"[TTS] Edge Neural TTS failed ({e}). Falling back to local pyttsx3...")

        self._speak_pyttsx3(text)

    def _speak_edge_neural(self, text: str):
        import edge_tts
        import pygame

        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"jarvis_tts_{int(time.time()*1000)}.mp3")

        async def _generate():
            communicate = edge_tts.Communicate(text, self.voice_id)
            await communicate.save(temp_file)

        asyncio.run(_generate())

        if not os.path.exists(temp_file):
            raise RuntimeError("Failed to create temporary TTS audio file.")

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy() and self.is_running and not self.stop_requested:
                time.sleep(0.03)

            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

    def stop_audio(self):
        """Immediately stops active audio speech playback and clears speech queue."""
        self.stop_requested = True
        try:
            with self.queue.mutex:
                self.queue.queue.clear()
        except Exception:
            pass
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass
        try:
            if self.pyttsx_engine:
                self.pyttsx_engine.stop()
        except Exception:
            pass

    def _speak_pyttsx3(self, text: str):
        try:
            import pyttsx3
            if self.pyttsx_engine is None:
                self.pyttsx_engine = pyttsx3.init()
            
            self.pyttsx_engine.setProperty('rate', self.rate)
            self.pyttsx_engine.setProperty('volume', self.volume)
            
            sapi_voices = self.pyttsx_engine.getProperty('voices')
            if sapi_voices:
                for v in sapi_voices:
                    if v.id == self.voice_id or self.voice_id.lower() in v.name.lower():
                        self.pyttsx_engine.setProperty('voice', v.id)
                        break

            self.pyttsx_engine.say(text)
            self.pyttsx_engine.runAndWait()
        except Exception as e:
            print(f"[TTS pyttsx3 Error]: {e}")

    def speak(self, text: str):
        if text and text.strip():
            clean_text = clean_text_for_speech(text)
            if clean_text:
                self.queue.put(clean_text)

    def stop(self):
        self.is_running = False
        self.queue.put(None)
