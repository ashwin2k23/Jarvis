from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor
from vision.screen_vision import ScreenVision


class ScreenTargetDialog(QDialog):
    """
    Pop-up modal dialog asking the user which screen window, browser tab, or monitor to capture.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📸 Screen Capture Target Selection")
        self.setFixedSize(520, 420)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.selected_hwnd = None
        self.selected_title = "Entire Desktop Screen"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Dark Glass Container
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #121215;
                border: 1px solid #3f3f46;
                border-radius: 12px;
            }
        """)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(12)

        # Header
        title_lbl = QLabel("📸 Select Screen / Application Window to Capture")
        title_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_lbl.setStyleSheet("color: #fafafa; border: none;")

        sub_lbl = QLabel("Which open application window, browser tab, or monitor would you like Jarvis to analyze?")
        sub_lbl.setFont(QFont("Segoe UI", 9))
        sub_lbl.setStyleSheet("color: #a1a1aa; border: none;")
        sub_lbl.setWordWrap(True)

        c_layout.addWidget(title_lbl)
        c_layout.addWidget(sub_lbl)

        # List Widget for open windows
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #18181b;
                color: #f4f4f5;
                border: 1px solid #27272a;
                border-radius: 8px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 6px;
                margin-bottom: 2px;
            }
            QListWidget::item:hover {
                background-color: #27272a;
            }
            QListWidget::item:selected {
                background-color: #3f3f46;
                color: #7c8cff;
                font-weight: bold;
            }
        """)

        # Populate open windows & tabs
        self.windows_data = ScreenVision.get_open_windows()
        for item in self.windows_data:
            w_item = QListWidgetItem(item["title"])
            w_item.setData(Qt.UserRole, item["hwnd"])
            self.list_widget.addItem(w_item)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

        c_layout.addWidget(self.list_widget, 1)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #27272a;
                color: #a1a1aa;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3f3f46;
                color: #ffffff;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        capture_btn = QPushButton("📸 Capture & Analyze")
        capture_btn.setCursor(QCursor(Qt.PointingHandCursor))
        capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #7c8cff;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6366f1;
            }
        """)
        capture_btn.clicked.connect(self._on_capture_clicked)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(capture_btn)
        c_layout.addLayout(btn_row)

        layout.addWidget(container)

    def _on_capture_clicked(self):
        curr = self.list_widget.currentItem()
        if curr:
            self.selected_hwnd = curr.data(Qt.UserRole)
            self.selected_title = curr.text()
        self.accept()
