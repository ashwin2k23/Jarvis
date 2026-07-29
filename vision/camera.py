"""
vision/camera.py — Phase 3: Camera & Image Vision
Uses OpenCV for webcam capture and Gemini Vision API for multimodal understanding.
"""
import base64
import os
from pathlib import Path
from typing import Optional


class CameraVision:
    """
    Manages webcam capture and vision-based AI analysis.
    Sends frames to Gemini Vision for natural language descriptions.
    """

    def __init__(self, ai_provider=None):
        self.ai_provider = ai_provider
        self._camera_index = 0

    def set_provider(self, ai_provider):
        self.ai_provider = ai_provider

    def capture_frame_bytes(self) -> Optional[bytes]:
        """Captures a single frame from the default webcam and returns it as JPEG bytes."""
        try:
            import cv2
            cap = cv2.VideoCapture(self._camera_index)
            if not cap.isOpened():
                return None
            ret, frame = cap.read()
            cap.release()
            if not ret or frame is None:
                return None
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()
        except ImportError:
            # Fallback: use PIL if opencv not installed
            try:
                from PIL import ImageGrab
                import io
                img = ImageGrab.grab()
                buf = io.BytesIO()
                img.save(buf, format='JPEG')
                return buf.getvalue()
            except Exception:
                return None
        except Exception:
            return None

    def describe_what_i_see(self) -> str:
        """Captures a webcam frame and asks the AI to describe what it sees."""
        if not self.ai_provider:
            return "No AI provider available for vision."
        image_bytes = self.capture_frame_bytes()
        if image_bytes is None:
            return "Could not capture image from camera. Please ensure a webcam is connected and accessible."
        try:
            response = self.ai_provider.generate_response_with_image(
                messages=[{"sender": "User", "content": "Describe in detail what you see in this image."}],
                image_bytes=image_bytes,
                system_prompt="You are Jarvis, a helpful AI assistant with vision capabilities. Describe what you see clearly and helpfully."
            )
            return response
        except AttributeError:
            return "Vision requires the Gemini AI provider. Please switch to Gemini in Settings."
        except Exception as e:
            return f"Vision analysis error: {e}"

    def read_document(self) -> str:
        """Captures a frame and performs OCR/text extraction on it."""
        if not self.ai_provider:
            return "No AI provider available."
        image_bytes = self.capture_frame_bytes()
        if image_bytes is None:
            return "Could not capture image from camera."
        try:
            response = self.ai_provider.generate_response_with_image(
                messages=[{"sender": "User", "content": "Extract and read all text visible in this image accurately. Present it in a clean, readable format."}],
                image_bytes=image_bytes,
                system_prompt="You are an OCR assistant. Extract all visible text from the provided image accurately."
            )
            return response
        except Exception as e:
            return f"Document reading error: {e}"

    def describe_image_file(self, filepath: str) -> str:
        """Describes any image file given a path."""
        if not self.ai_provider:
            return "No AI provider available."
        try:
            with open(filepath, "rb") as f:
                image_bytes = f.read()
            response = self.ai_provider.generate_response_with_image(
                messages=[{"sender": "User", "content": "Describe this image in detail."}],
                image_bytes=image_bytes,
                system_prompt="Describe the provided image comprehensively and helpfully."
            )
            return response
        except FileNotFoundError:
            return f"Image file not found: {filepath}"
        except Exception as e:
            return f"Image description error: {e}"

    def analyze_for_errors(self) -> str:
        """Captures screen via camera and looks for error messages or issues."""
        if not self.ai_provider:
            return "No AI provider available."
        image_bytes = self.capture_frame_bytes()
        if image_bytes is None:
            return "Could not capture image."
        try:
            response = self.ai_provider.generate_response_with_image(
                messages=[{"sender": "User", "content": "Look for any error messages, warnings, or problems visible in this image. Explain what they mean and suggest how to fix them."}],
                image_bytes=image_bytes,
                system_prompt="You are a technical debugging assistant. Identify and explain any errors or warnings visible in the image."
            )
            return response
        except Exception as e:
            return f"Error analysis failed: {e}"
