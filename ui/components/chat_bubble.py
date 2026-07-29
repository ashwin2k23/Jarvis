from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
import datetime

class ChatBubble(QFrame):
    """Linear & Raycast Inspired Message Bubble Component."""

    def __init__(self, sender: str, content: str, agent_name: str = "Jarvis", timestamp: str = None):
        super().__init__()
        self.sender = sender
        self.content = content
        self.agent_name = agent_name
        self.timestamp = timestamp or datetime.datetime.now().strftime("%I:%M %p")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        # Header (Sender Tag + Timestamp)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        sender_label = QLabel(self.sender)
        sender_label.setStyleSheet("font-weight: 600; font-size: 12px; color: #7c8cff;" if self.sender != "User" else "font-weight: 600; font-size: 12px; color: #a1a1aa;")

        badge_str = ""
        if self.sender != "User" and self.agent_name and self.agent_name not in ["Jarvis", "AutomationAgent", "ResearcherAgent", "CoderAgent", "CoreAssistant"]:
            badge_str = f"[{self.agent_name}]"

        badge_label = QLabel(badge_str)
        badge_label.setStyleSheet("color: #71717a; font-size: 11px; font-weight: 500;")

        time_label = QLabel(self.timestamp)
        time_label.setStyleSheet("color: #71717a; font-size: 11px;")

        header_layout.addWidget(sender_label)
        if badge_str:
            header_layout.addWidget(badge_label)
        header_layout.addStretch()
        header_layout.addWidget(time_label)

        # Message Content (15px Linear Typography)
        content_label = QLabel()
        content_label.setWordWrap(True)
        content_label.setTextFormat(Qt.MarkdownText)
        content_label.setText(self.content)
        content_label.setStyleSheet("font-size: 15px; color: #fafafa; line-height: 1.4;")
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addLayout(header_layout)
        layout.addWidget(content_label)

        if self.sender == "User":
            self.setProperty("class", "user-bubble")
        elif self.sender == "System":
            self.setProperty("class", "system-bubble")
        else:
            self.setProperty("class", "jarvis-bubble")
