import datetime
import random
from typing import List, Dict
from ai.provider_interface import AIProviderInterface

class MockProvider(AIProviderInterface):
    """Built-in offline intelligent fallback provider for zero-config out-of-the-box experience."""

    def is_available(self) -> bool:
        return True

    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        last_message = ""
        if messages:
            last_message = messages[-1].get("content", "").lower().strip()

        # Pattern matching for offline smart responses
        if any(w in last_message for w in ["hello", "hi", "hey", "greetings"]):
            return "Greetings! I am Jarvis, your personal AI assistant. How may I assist you today?"
        
        elif any(w in last_message for w in ["time", "clock", "date"]):
            now = datetime.datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
            return f"The current system time is {now}."
        
        elif "who are you" in last_message or "your name" in last_message:
            return "I am Jarvis — an advanced, extensible desktop AI assistant equipped with computer control, search, voice interaction, and automation tools."
        
        elif "weather" in last_message:
            return "To check live weather forecast, please enable the Internet Search module or enter a location query like 'search weather in London'."
        
        elif "help" in last_message or "command" in last_message:
            return (
                "Here are some capabilities you can try:\n"
                "• **Computer Control**: 'open notepad', 'take screenshot', 'mute volume'\n"
                "• **Internet Search**: 'search latest news on AI'\n"
                "• **Productivity**: 'add task Buy groceries', 'notes'\n"
                "• **Coding**: Ask me to generate Python code or debug snippets\n"
                "• **Settings**: Switch to OpenAI or local Ollama model in the Settings tab"
            )

        elif "code" in last_message or "python" in last_message or "function" in last_message:
            return (
                "Here is a Python example based on your prompt:\n\n"
                "```python\n"
                "def jarvis_helper(data):\n"
                "    \"\"\"Automated assistant utility function.\"\"\"\n"
                "    print(f'[Jarvis] Processing: {data}')\n"
                "    return True\n"
                "```\n\n"
                "You can execute code and system operations safely directly within Jarvis!"
            )
        
        else:
            responses = [
                f"I have received your message: '{last_message}'. As an AI assistant, I can help you automate tasks, search the web, manage notes, or control system functions.",
                f"Understood. I am standing by to assist with your request: '{last_message}'. Feel free to try my automation commands or search tools!",
                f"Processing '{last_message}'. All system modules are online and operating normally."
            ]
            return random.choice(responses)
