"""
ai/gemini_provider.py — Gemini AI Provider
Uses the official modern `google-genai` SDK (google.genai).
"""
from typing import List, Dict
from ai.provider_interface import AIProviderInterface


class GeminiProvider(AIProviderInterface):
    """Google Gemini API Provider integration using the modern official google-genai SDK."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key.strip() if api_key else ""
        self.model = model if model and "gemini-2.5" not in model else "gemini-2.0-flash"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        if not self.is_available():
            return "Error: Gemini API Key is missing. Please set your Gemini API key in Jarvis Settings."
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            contents = []
            for msg in messages:
                role = "model" if msg.get("sender") == "Jarvis" else "user"
                content_text = msg.get("content", "")
                if content_text:
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=content_text)]
                        )
                    )

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                temperature=0.7
            )

            models_to_try = [self.model, "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-flash-latest"]
            # Deduplicate while preserving order
            seen = set()
            models_to_try = [m for m in models_to_try if m and not (m in seen or seen.add(m))]

            last_err = None
            for target_model in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=target_model,
                        contents=contents if contents else "Hello",
                        config=config
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as m_err:
                    last_err = m_err
                    continue

            return f"⚠️ Gemini API notice: Could not reach model endpoint. ({last_err})"
        except Exception as e:
            return f"[Gemini API Error]: {str(e)}"


    def generate_response_with_image(self, messages: List[Dict[str, str]], image_bytes: bytes, system_prompt: str = "") -> str:
        """Generates a multimodal response using text + image (vision capability)."""
        if not self.is_available():
            return "Error: Gemini API Key is missing. Vision requires a valid Gemini API key."
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

            text_content = "\n".join(
                msg.get("content", "") for msg in messages if msg.get("content")
            )
            text_part = types.Part.from_text(text=text_content)

            contents = [types.Content(role="user", parts=[image_part, text_part])]

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                temperature=0.5
            )

            for target_model in [self.model, "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-flash-latest"]:
                try:
                    response = client.models.generate_content(
                        model=target_model,
                        contents=contents,
                        config=config
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception:
                    continue

            if response and response.text:
                return response.text.strip()
            return "No vision response returned from Gemini API."
        except Exception as e:
            return f"[Gemini Vision Error]: {str(e)}"
