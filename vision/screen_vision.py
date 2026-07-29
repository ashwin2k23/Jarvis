"""
vision/screen_vision.py — Phase 4: Screen Understanding
Captures the current screen and sends it to Gemini Vision for intelligent analysis.
"""
import io
import os
import datetime
from pathlib import Path
from typing import Optional


class ScreenVision:
    """
    Captures and analyzes the current desktop screen using Gemini Vision API.
    Can explain errors, read code, summarize PDFs, and detect UI bugs.
    """

    def __init__(self, ai_provider=None):
        self.ai_provider = ai_provider

    def set_provider(self, ai_provider):
        self.ai_provider = ai_provider

    @staticmethod
    def get_open_windows() -> list:
        """Enumerates visible top-level application windows and browser tabs."""
        windows = [{"title": "🖥️ Entire Desktop Screen (All Monitors)", "hwnd": None}]
        try:
            import win32gui
            def enum_cb(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd).strip()
                    if title and title not in ("Program Manager", "Settings", "Jarvis Desktop AI Assistant", "Jarvis"):
                        rect = win32gui.GetWindowRect(hwnd)
                        w = rect[2] - rect[0]
                        h = rect[3] - rect[1]
                        if w > 150 and h > 150:
                            tl = title.lower()
                            if any(b in tl for b in ["chrome", "brave", "edge", "firefox", "opera", "safari"]):
                                icon = "🌐 "
                            elif any(c in tl for c in ["code", "visual studio", "pycharm", "sublime", "git"]):
                                icon = "💻 "
                            elif any(m in tl for m in ["discord", "telegram", "whatsapp", "slack", "spotify"]):
                                icon = "💬 "
                            else:
                                icon = "📄 "
                            windows.append({"title": f"{icon}{title}", "hwnd": hwnd, "raw_title": title})
            win32gui.EnumWindows(enum_cb, None)
        except Exception as e:
            print(f"[ScreenVision] Window enum notice: {e}")
        return windows

    def capture_screen_bytes(self, hwnd=None) -> Optional[bytes]:
        """Takes a screenshot of full screen or a specific selected window/tab."""
        try:
            from PIL import ImageGrab
            if hwnd:
                import win32gui
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, 9)
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except Exception:
                    pass
                import time
                time.sleep(0.15)
                rect = win32gui.GetWindowRect(hwnd)
                if rect[2] > rect[0] and rect[3] > rect[1]:
                    img = ImageGrab.grab(bbox=rect)
                else:
                    img = ImageGrab.grab()
            else:
                img = ImageGrab.grab()

            buf = io.BytesIO()
            img.convert("RGB").save(buf, format='JPEG', quality=85)
            return buf.getvalue()
        except Exception:
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab()
                buf = io.BytesIO()
                img.convert("RGB").save(buf, format='JPEG', quality=85)
                return buf.getvalue()
            except Exception:
                return None

    def save_screenshot(self, save_dir: str = None, hwnd=None) -> Optional[str]:
        """Takes and saves a screenshot, returning the file path."""
        try:
            from PIL import ImageGrab
            if save_dir is None:
                save_dir = Path(os.path.expanduser("~")) / "Pictures" / "Jarvis_Screenshots"
            else:
                save_dir = Path(save_dir)
            save_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = save_dir / f"screenshot_{timestamp}.png"
            if hwnd:
                import win32gui
                rect = win32gui.GetWindowRect(hwnd)
                img = ImageGrab.grab(bbox=rect)
            else:
                img = ImageGrab.grab()
            img.save(str(filepath))
            return str(filepath)
        except Exception:
            return None

    def analyze_screen(self, custom_prompt: str = None, hwnd=None) -> str:
        """Captures the target screen/window and asks AI to analyze it."""
        if not self.ai_provider:
            return "No AI provider configured for screen analysis."
        image_bytes = self.capture_screen_bytes(hwnd=hwnd)
        if image_bytes is None:
            return "Failed to capture screen. Ensure Pillow is installed."
        prompt = custom_prompt or "Analyze this screenshot. Describe what application is open, what content is visible, and any notable observations."
        try:
            response = self.ai_provider.generate_response_with_image(
                messages=[{"sender": "User", "content": prompt}],
                image_bytes=image_bytes,
                system_prompt="You are Jarvis, an AI assistant with screen reading capabilities. Analyze the provided screenshot and give a helpful, accurate response."
            )
            return response
        except AttributeError:
            return "Screen analysis requires Gemini AI provider. Please configure Gemini in Settings."
        except Exception as e:
            return f"Screen analysis error: {e}"


    def explain_error_on_screen(self) -> str:
        """Captures the screen and specifically looks for compiler/runtime errors to explain."""
        return self.analyze_screen(
            "Look carefully at this screen. Find any error messages, exception traces, compiler errors, or warning messages. "
            "Explain what each error means in plain English and provide specific actionable steps to fix them."
        )

    def read_code_on_screen(self) -> str:
        """Reads and explains any code visible on screen."""
        return self.analyze_screen(
            "Read all the code visible on this screen. Explain what it does, identify any bugs or issues, "
            "and suggest improvements. Format code sections using markdown code blocks."
        )

    def summarize_pdf(self, pdf_path: str) -> str:
        """Extracts and summarizes text from a PDF file."""
        if not self.ai_provider:
            return "No AI provider configured."
        try:
            import pdfplumber
            text_content = []
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages[:20]):  # Cap at 20 pages
                    text = page.extract_text()
                    if text:
                        text_content.append(f"[Page {i+1}]\n{text}")

            if not text_content:
                return "Could not extract text from PDF. The PDF may be image-based or protected."

            combined_text = "\n\n".join(text_content)
            if len(combined_text) > 8000:
                combined_text = combined_text[:8000] + "\n...[truncated for length]"

            response = self.ai_provider.generate_response(
                messages=[{"sender": "User", "content": f"Please summarize this PDF document:\n\n{combined_text}"}],
                system_prompt="You are a helpful assistant. Provide a clear, structured summary of the provided document content."
            )
            return response
        except ImportError:
            return "PDF summarization requires 'pdfplumber'. Install it with: pip install pdfplumber"
        except FileNotFoundError:
            return f"PDF file not found: {pdf_path}"
        except Exception as e:
            return f"PDF summarization error: {e}"

    def detect_ui_bugs(self) -> str:
        """Captures screen and analyzes the visible UI for bugs or design issues."""
        return self.analyze_screen(
            "Analyze this UI screenshot as a UX/UI expert. Identify any visual bugs, layout issues, "
            "accessibility problems, or design inconsistencies. Be specific and actionable."
        )

    def fill_form_assistance(self) -> str:
        """Analyzes any form visible on screen and provides guidance."""
        return self.analyze_screen(
            "I can see what appears to be a form or input fields on screen. "
            "Describe each field visible and suggest what information should be entered in each one."
        )
