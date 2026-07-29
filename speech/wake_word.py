"""
speech/wake_word.py — Phase 9: Offline Wake Word Detection
Listens continuously for "Hey Jarvis" using openwakeword (MIT license, no API key).
Falls back to a simple energy + Google STT approach if openwakeword is not installed.
"""
from PySide6.QtCore import QThread, Signal


class WakeWordListener(QThread):
    """
    Continuously listens for a wake word ("Hey Jarvis") in the background.
    Emits wake_word_detected when the phrase is heard.
    Uses openwakeword for offline detection — low CPU, no API key required.
    """

    wake_word_detected = Signal()
    status_update = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, sensitivity: float = 0.5, parent=None):
        super().__init__(parent)
        self._running = False
        self.sensitivity = sensitivity
        self._use_oww = self._check_openwakeword()

    def _check_openwakeword(self) -> bool:
        """Returns True if openwakeword is available."""
        try:
            import openwakeword  # noqa
            return True
        except ImportError:
            return False

    def start_listening(self):
        """Starts the background wake word thread."""
        self._running = True
        self.start()

    def stop_listening(self):
        """Signals the thread to stop."""
        self._running = False
        self.quit()

    def run(self):
        """Main loop — runs in background thread."""
        if self._use_oww:
            self._run_openwakeword()
        else:
            self._run_fallback()

    # ------------------------------------------------------------------
    # Primary: openwakeword
    # ------------------------------------------------------------------

    def _run_openwakeword(self):
        """Uses openwakeword for offline wake word detection."""
        try:
            import pyaudio
            import numpy as np
            from openwakeword.model import Model

            self.status_update.emit("Wake word engine starting...")

            # Load the pre-trained model (downloads on first use ~10MB)
            model = Model(
                wakeword_models=["hey_jarvis"],  # Built-in model
                inference_framework="onnx"
            )

            audio = pyaudio.PyAudio()
            stream = audio.open(
                rate=16000,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=1280
            )

            self.status_update.emit("🎙️ Wake word listening active...")

            while self._running:
                try:
                    raw = stream.read(1280, exception_on_overflow=False)
                    audio_data = np.frombuffer(raw, dtype=np.int16)
                    predictions = model.predict(audio_data)

                    for model_name, score in predictions.items():
                        if score >= self.sensitivity:
                            model.reset()  # Reset after trigger
                            self.wake_word_detected.emit()
                            self.msleep(2000)  # Brief cooldown
                            break
                except Exception:
                    continue

            stream.stop_stream()
            stream.close()
            audio.terminate()

        except ImportError:
            self.error_occurred.emit(
                "openwakeword not installed. Run: pip install openwakeword pyaudio"
            )
        except Exception as e:
            # Fall back to STT-based detection
            self._run_fallback()

    # ------------------------------------------------------------------
    # Fallback: SpeechRecognition-based trigger detection
    # ------------------------------------------------------------------

    def _run_fallback(self):
        """
        Fallback wake word using SpeechRecognition library.
        Less efficient than openwakeword but works without extra dependencies.
        """
        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 0.5

            self.status_update.emit("🎙️ Wake word listening (fallback mode)...")

            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)

                while self._running:
                    try:
                        audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                        text = recognizer.recognize_google(audio).lower()
                        if any(phrase in text for phrase in [
                            "hey jarvis", "jarvis", "hi jarvis", "okay jarvis",
                            "jarvis wake up", "jarvis are you there"
                        ]):
                            self.wake_word_detected.emit()
                            self.msleep(1500)
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError:
                        # No internet for Google STT — wait and retry
                        self.msleep(5000)
                    except Exception:
                        continue

        except Exception as e:
            self.error_occurred.emit(f"Wake word fallback error: {e}")
