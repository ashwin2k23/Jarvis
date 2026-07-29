import threading
from PySide6.QtCore import QThread, Signal

class VoiceListenerThread(QThread):
    """Background Qt thread for Speech-To-Text microphone listening."""
    text_recognized = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, timeout: int = 5, phrase_time_limit: int = 10):
        super().__init__()
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit

    def run(self):
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit
                )
                text = recognizer.recognize_google(audio)
                if text:
                    self.text_recognized.emit(text)
                else:
                    self.error_occurred.emit("No speech recognized.")
        except Exception as e:
            self.error_occurred.emit(str(e))


class SpeechToTextListener:
    """Synchronous / Callback-based SpeechToTextListener wrapper."""
    
    def __init__(self, callback_on_text=None, callback_on_error=None):
        self.callback_on_text = callback_on_text
        self.callback_on_error = callback_on_error
        self.is_listening = False

    def start_listening_once(self):
        if self.is_listening:
            return
        self.is_listening = True
        self.thread = VoiceListenerThread()
        if self.callback_on_text:
            self.thread.text_recognized.connect(self.callback_on_text)
        if self.callback_on_error:
            self.thread.error_occurred.connect(self.callback_on_error)
        self.thread.start()

    def stop(self):
        self.is_listening = False
