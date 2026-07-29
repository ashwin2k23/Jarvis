from PySide6.QtWidgets import QWidget, QVBoxLayout, QMenu
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QAction, QCursor
from ui.components.jarvis_orb_widget import create_orb_widget

class FloatingOrbWindow(QWidget):
    """Frameless, draggable, always-on-top Desktop Floating AI Orb Widget."""

    orb_clicked = Signal()
    toggle_main_window_requested = Signal()
    toggle_listening_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(140, 140)

        self._drag_pos = QPoint()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        # Create expressive animated orb widget
        self.orb_widget = create_orb_widget(radius=50, parent=self)
        layout.addWidget(self.orb_widget)

    def set_state(self, state: str):
        if hasattr(self.orb_widget, 'set_state'):
            self.orb_widget.set_state(state)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = QPoint()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_listening_requested.emit()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #18181b;
                color: #f4f4f5;
                border: 1px solid #3f3f46;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item:selected {
                background-color: #27272a;
                color: #7c8cff;
            }
        """)

        action_listen = menu.addAction("🎙️ Toggle Listening (Double-Click)")
        action_main = menu.addAction("🖥️ Open Jarvis Window")
        menu.addSeparator()
        action_hide = menu.addAction("❌ Hide Floating Orb")

        action = menu.exec(QCursor.pos())
        if action == action_listen:
            self.toggle_listening_requested.emit()
        elif action == action_main:
            self.toggle_main_window_requested.emit()
        elif action == action_hide:
            self.hide()
