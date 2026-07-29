import sys
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QLabel, 
                             QListWidget, QListWidgetItem, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui import QColor, QFont, QKeyEvent

class GlobalHotkeyListener(QThread):
    """Background listener for Alt+Space global shortcut using pynput."""
    hotkey_triggered = Signal()

    def __init__(self):
        super().__init__()
        self._stop_flag = False
        self.setDaemon(True)

    def stop(self):
        self._stop_flag = True

    def run(self):
        try:
            from pynput import keyboard

            current_keys = set()

            def on_press(key):
                try:
                    if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
                        current_keys.add("alt")
                    if key == keyboard.Key.space:
                        current_keys.add("space")

                    if "alt" in current_keys and "space" in current_keys:
                        self.hotkey_triggered.emit()
                except Exception:
                    pass

            def on_release(key):
                try:
                    if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
                        current_keys.discard("alt")
                    if key == keyboard.Key.space:
                        current_keys.discard("space")
                except Exception:
                    pass

            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                while not self._stop_flag:
                    listener.join(timeout=0.5)
                    if not listener.running:
                        break
        except Exception as e:
            print(f"[GlobalHotkeyListener Notice]: {e}")



class CommandPaletteDialog(QDialog):
    """Spotlight / Raycast style floating Alt+Space launcher dialog."""

    command_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(650, 360)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Container Widget with dark glass style
        self.container = QDialog(self)
        self.container.setStyleSheet("""
            QDialog {
                background-color: #121215;
                border: 1px solid #27272a;
                border-radius: 14px;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(10)

        # Header Title
        title_label = QLabel("⚡ Jarvis Command Palette")
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_label.setStyleSheet("color: #7c8cff;")
        container_layout.addWidget(title_label)

        # Search Bar Input
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command, ask Jarvis, or apply a preset (e.g. 'Start Work Mode')...")
        self.input_field.setFont(QFont("Segoe UI", 11))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #18181b;
                color: #f4f4f5;
                border: 1px solid #3f3f46;
                border-radius: 8px;
                padding: 10px 14px;
            }
            QLineEdit:focus {
                border: 1px solid #7c8cff;
            }
        """)
        self.input_field.returnPressed.connect(self._handle_submit)
        container_layout.addWidget(self.input_field)

        # Output / Results Area
        self.output_label = QLabel("Press Enter to execute query or ESC to close.")
        self.output_label.setWordWrap(True)
        self.output_label.setFont(QFont("Segoe UI", 9))
        self.output_label.setStyleSheet("""
            QLabel {
                color: #a1a1aa;
                background-color: #18181b;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #27272a;
            }
        """)
        container_layout.addWidget(self.output_label, 1)

        layout.addWidget(self.container)

        # Shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setYOffset(10)
        self.container.setGraphicsEffect(shadow)

    def _handle_submit(self):
        text = self.input_field.text().strip()
        if text:
            self.output_label.setText(f"⏳ Processing command: '{text}'...")
            self.command_submitted.emit(text)

    def set_result(self, result_text: str):
        self.output_label.setText(result_text)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            # Center on active monitor
            from PySide6.QtGui import QGuiApplication
            screen = QGuiApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 3
            self.move(x, y)
            self.show()
            self.raise_()
            self.activateWindow()
            self.input_field.setFocus()
            self.input_field.selectAll()
