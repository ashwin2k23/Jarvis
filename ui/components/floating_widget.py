from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFrame
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QGuiApplication
from ui.components.jarvis_orb_widget import create_orb_widget

class FloatingCornerWidget(QWidget):
    """Sleek, pixel-perfect floating overlay widget that appears in the corner when Jarvis is minimized."""

    restore_requested = Signal()
    voice_clicked = Signal()
    stop_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(220, 52)
        
        self.drag_position = QPoint()

        self._init_ui()
        self.reposition_to_corner()

    def _init_ui(self):
        container = QFrame(self)
        container.setObjectName("FloatingContainer")
        container.setFixedSize(220, 52)
        container.setStyleSheet("""
            QFrame#FloatingContainer {
                background-color: rgba(18, 18, 21, 0.96);
                border: 1.5px solid rgba(255, 255, 255, 0.35);
                border-radius: 26px;
            }
        """)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignVCenter)

        # Custom Animated GIF or 3D Procedural Moving Sphere (Mini)
        self.orb = create_orb_widget(radius=16)
        layout.addWidget(self.orb, 0, Qt.AlignVCenter)

        layout.addStretch()

        # Voice Button
        self.voice_btn = QPushButton("🎙️")
        self.voice_btn.setToolTip("Voice Assist")
        self.voice_btn.setFixedSize(32, 32)
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #27272a;
                color: #fafafa;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 16px;
                font-size: 13px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #3f3f46;
                border-color: #818cf8;
            }
        """)
        self.voice_btn.clicked.connect(self.voice_clicked.emit)
        layout.addWidget(self.voice_btn, 0, Qt.AlignVCenter)

        # Stop Button
        self.stop_btn = QPushButton("🛑")
        self.stop_btn.setToolTip("Interrupt / Stop")
        self.stop_btn.setFixedSize(32, 32)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f1d1d;
                color: #fca5a5;
                border: 1px solid #991b1b;
                border-radius: 16px;
                font-size: 12px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #991b1b;
                color: #ffffff;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        layout.addWidget(self.stop_btn, 0, Qt.AlignVCenter)

        # Restore / Expand Window Button
        self.restore_btn = QPushButton("🗖")
        self.restore_btn.setToolTip("Restore Jarvis Window")
        self.restore_btn.setFixedSize(32, 32)
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 16px;
                font-size: 13px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
                border-color: #818cf8;
            }
        """)
        self.restore_btn.clicked.connect(self.restore_requested.emit)
        layout.addWidget(self.restore_btn, 0, Qt.AlignVCenter)

    def reposition_to_corner(self):
        """Positions the widget at the bottom-right corner of the screen."""
        screen = QGuiApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            x = geom.right() - self.width() - 20
            y = geom.bottom() - self.height() - 20
            self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
