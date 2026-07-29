import sys
import os
import random
import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame,
    QLabel, QPushButton, QLineEdit, QScrollArea, QStackedWidget,
    QComboBox, QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QMessageBox, QFileDialog, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QCursor

from ui.styles import DARK_GLASS_STYLESHEET
from ui.components.chat_bubble import ChatBubble
from ui.components.jarvis_orb_widget import create_orb_widget, InvisibleIntelligenceOrbWidget
from ui.components.floating_widget import FloatingCornerWidget
from PySide6.QtCore import QEvent


class AIWorkerThread(QThread):
    """Background worker thread for generating AI responses without locking UI."""
    response_ready = Signal(dict)

    def __init__(self, core_controller, user_text: str, custom_func=None, session_id: str = "default"):
        super().__init__()
        self.core = core_controller
        self.user_text = user_text
        self.custom_func = custom_func
        self.session_id = session_id

    def run(self):
        try:
            if self.custom_func:
                result = self.custom_func()
            else:
                result = self.core.process_user_input(self.user_text, session_id=self.session_id)
            self.response_ready.emit(result)
        except Exception as e:
            self.response_ready.emit({
                "response": f"⚠️ Error: {e}",
                "agent": "SystemError",
                "type": "error"
            })




class MainWindow(QMainWindow):
    """
    Jarvis AI Assistant Main Window — Invisible Intelligence Design Language.
    Combines 40% Raycast, 30% Linear, 20% Arc Browser, 10% Apple Intelligence.
    Palette: #09090b Canvas | #121215 Surface | rgba(255,255,255,0.08) Border | #7C8CFF Accent
    """

    def __init__(self, core_controller):
        super().__init__()
        self.core = core_controller

        self.setWindowTitle("Jarvis — Invisible Intelligence")
        self._update_window_icon()
        self.resize(760, 840)
        self.setMinimumSize(540, 680)

        self.setStyleSheet(DARK_GLASS_STYLESHEET)
        self._active_threads = set()
        self.current_session_id = "default"

        # Floating Corner Widget for Minimized State
        self.floating_widget = FloatingCornerWidget()
        self.floating_widget.restore_requested.connect(self._restore_from_floating)
        self.floating_widget.voice_clicked.connect(self._on_voice_clicked)
        self.floating_widget.stop_clicked.connect(self._on_stop_clicked)

        # Command Palette & Global Alt+Space Hotkey
        try:
            from ui.components.command_palette import CommandPaletteDialog, GlobalHotkeyListener
            self.command_palette = CommandPaletteDialog(self)
            self.command_palette.command_submitted.connect(self._on_palette_command_submitted)

            self.hotkey_listener = GlobalHotkeyListener()
            self.hotkey_listener.hotkey_triggered.connect(self.command_palette.toggle_visibility)
            self.hotkey_listener.start()
        except Exception as e:
            print(f"[MainWindow Notice] Command palette init notice: {e}")



        # Ghost Copilot Monitor (Proactive Screen Monitor)
        try:
            from proactive.monitor import GhostCopilotMonitor
            self.ghost_copilot = GhostCopilotMonitor(core=self.core, interval_seconds=30)
            self.ghost_copilot.error_detected.connect(self._on_ghost_copilot_error)
            self.ghost_copilot.start()
        except Exception as e:
            print(f"[MainWindow Notice] Ghost copilot init notice: {e}")

        self._init_ui()
        self._load_chat_history()

        # Defer greeting so main window opens instantly (0ms launch lag)
        QTimer.singleShot(250, self._greet_user_on_startup)

        # Connect proactive monitor signals (Phase 10)
        self._setup_proactive_monitor()


    # ─────────────────────────────────────────────────────────────
    # Greeting Logic
    # ─────────────────────────────────────────────────────────────
    def _greet_user_on_startup(self):
        """Sets title greeting and speaks concise startup message."""
        now = datetime.datetime.now()
        hour = now.hour
        user_name = self.core.config.get("user_name", "Boss")

        if 5 <= hour < 12:
            title_text = "Good Morning"
            subtitle_text = f"Good morning, {user_name}. Ready when you are."
        elif 12 <= hour < 17:
            title_text = "Good Afternoon"
            subtitle_text = f"How can I help today, {user_name}?"
        elif 17 <= hour < 22:
            title_text = "Good Evening"
            subtitle_text = f"Good evening, {user_name}. What's the plan for tonight?"
        else:
            title_text = "Late Night"
            subtitle_text = f"Late night session, {user_name}? Standing by."

        if hasattr(self, "header_title_lbl"):
            self.header_title_lbl.setText(title_text)
        if hasattr(self, "header_subtitle_lbl"):
            self.header_subtitle_lbl.setText(subtitle_text)

        if hasattr(self.core, "tts") and self.core.config.get("auto_speak_responses", True):
            self.core.tts.speak(subtitle_text)

    # ─────────────────────────────────────────────────────────────
    # UI Setup
    # ─────────────────────────────────────────────────────────────
    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Stacked Pages
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_assistant_page())  # Index 0: Main Assistant
        self.stack.addWidget(self._build_memory_page())     # Index 1: Memory
        self.stack.addWidget(self._build_tools_page())      # Index 2: Tools & Skills
        self.stack.addWidget(self._build_settings_page())   # Index 3: Settings

        main_layout.addWidget(self.stack)

    def _switch_tab(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.footer_nav_btns):
            btn.setChecked(i == index)
        if index == 1:
            self._refresh_memory_view()

    # ─────────────────────────────────────────────────────────────
    # Page 0: Main Assistant Interface (ChatGPT Style Interface)
    # ─────────────────────────────────────────────────────────────
    def _build_assistant_page(self) -> QWidget:
        page = QWidget()
        outer_layout = QHBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # ── 1. ChatGPT Left Drawer Sidebar (Collapsible History) ──
        self.sidebar_widget = self._build_chatgpt_sidebar()
        outer_layout.addWidget(self.sidebar_widget)

        # ── 2. Main Chat Container ──
        main_container = QWidget()
        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # ChatGPT Model Selector Top Bar
        top_bar = self._build_chatgpt_top_bar()
        layout.addLayout(top_bar)

        # Expressive Orb Header (Centered)
        header_container = QVBoxLayout()
        header_container.setAlignment(Qt.AlignCenter)
        header_container.setSpacing(4)

        self.jarvis_orb = create_orb_widget(radius=45)

        self.header_title_lbl = QLabel("Good Afternoon")
        self.header_title_lbl.setObjectName("HeaderTitle")
        self.header_title_lbl.setAlignment(Qt.AlignCenter)

        self.header_subtitle_lbl = QLabel("How can I help today?")
        self.header_subtitle_lbl.setObjectName("HeaderSubtitle")
        self.header_subtitle_lbl.setAlignment(Qt.AlignCenter)

        header_container.addWidget(self.jarvis_orb, 0, Qt.AlignCenter)
        header_container.addWidget(self.header_title_lbl, 0, Qt.AlignCenter)
        header_container.addWidget(self.header_subtitle_lbl, 0, Qt.AlignCenter)

        layout.addLayout(header_container)

        # Vision Quick-Action Bar
        vision_bar = self._build_vision_bar()
        layout.addLayout(vision_bar)

        # Split Workspace Layout (Chat Area Left, Dynamic Workspace Panel Right)
        workspace_split = QHBoxLayout()
        workspace_split.setContentsMargins(0, 0, 0, 0)
        workspace_split.setSpacing(12)

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # Conversation Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(12)

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setSpacing(12)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)

        self.chat_layout.addWidget(self.messages_container)
        self.scroll_area.setWidget(self.chat_container)
        left_layout.addWidget(self.scroll_area, 1)

        # ChatGPT Style Input Pill Frame
        input_frame = QFrame()
        input_frame.setObjectName("InputFrame")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 6, 12, 6)
        input_layout.setSpacing(8)

        self.chat_input = QLineEdit()
        self.chat_input.setObjectName("ChatInput")
        self.chat_input.setPlaceholderText("Ask Jarvis anything...")
        self.chat_input.returnPressed.connect(self._on_send_clicked)

        self.voice_btn = QPushButton("🎤 Voice")
        self.voice_btn.setProperty("class", "voice-btn")
        self.voice_btn.setToolTip("Activate Voice Assistant")
        self.voice_btn.clicked.connect(self._on_voice_clicked)

        self.stop_btn = QPushButton("🛑 Stop")
        self.stop_btn.setProperty("class", "stop-btn")
        self.stop_btn.setToolTip("Interrupt speech and cancel active tasks")
        self.stop_btn.clicked.connect(self._on_stop_clicked)

        self.send_btn = QPushButton("Send ➔")
        self.send_btn.setProperty("class", "action-btn")
        self.send_btn.clicked.connect(self._on_send_clicked)

        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.voice_btn)
        input_layout.addWidget(self.stop_btn)
        input_layout.addWidget(self.send_btn)

        left_layout.addWidget(input_frame)
        workspace_split.addWidget(left_container, 1)

        # Dynamic Workspace Side Panel
        from ui.components.dynamic_panel import DynamicWorkspacePanel
        self.dynamic_panel = DynamicWorkspacePanel()
        self.dynamic_panel.setMaximumWidth(0)
        self.dynamic_panel.close_requested.connect(lambda: self.animate_workspace_panel(expand=False))
        workspace_split.addWidget(self.dynamic_panel)

        layout.addLayout(workspace_split, 1)

        # ── 4. Understated Footer Navigation Pills ──
        footer_nav = QHBoxLayout()
        footer_nav.setSpacing(8)
        footer_nav.setContentsMargins(4, 0, 4, 0)

        self.footer_nav_btns = []
        nav_items = [
            ("💬 Assistant", 0),
            ("🧠 Memory", 1),
            ("🛠️ Tools", 2),
            ("⚙️ Settings", 3),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setProperty("class", "footer-nav-btn")
            btn.setCheckable(True)
            if index == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, idx=index: self._switch_tab(idx))
            self.footer_nav_btns.append(btn)
            footer_nav.addWidget(btn)

        footer_nav.addStretch()

        # Status Pill
        self.status_pill = QLabel("● Ready")
        self.status_pill.setObjectName("StatusPill")
        footer_nav.addWidget(self.status_pill)

        # Clear Chat Button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setProperty("class", "pill-btn")
        clear_btn.clicked.connect(self._clear_chat)
        footer_nav.addWidget(clear_btn)

        layout.addLayout(footer_nav)

        outer_layout.addWidget(main_container, 1)

        # Load session history in sidebar
        QTimer.singleShot(100, self._refresh_sidebar_sessions)

        return page

    # ─────────────────────────────────────────────────────────────
    # ChatGPT Sidebar & Model Selector Components
    # ─────────────────────────────────────────────────────────────
    def _build_chatgpt_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("ChatGPTSidebar")
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet("""
            QFrame#ChatGPTSidebar {
                background-color: #171717;
                border-right: 1px solid #27272a;
            }
        """)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 14, 10, 14)
        layout.setSpacing(10)

        # New Chat Button
        new_chat_btn = QPushButton("➕ New Chat")
        new_chat_btn.setCursor(QCursor(Qt.PointingHandCursor))
        new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #212121;
                color: #fafafa;
                border: 1px solid #3f3f46;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2f2f2f;
                border-color: #7c8cff;
            }
        """)
        new_chat_btn.clicked.connect(self._create_new_chat_session)
        layout.addWidget(new_chat_btn)

        # Session History Label
        history_hdr = QLabel("Recent Chats")
        history_hdr.setStyleSheet("color: #a1a1aa; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-top: 6px;")
        layout.addWidget(history_hdr)

        # Sessions List Widget
        self.session_list = QListWidget()
        self.session_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                color: #e4e4e7;
            }
            QListWidget::item {
                padding: 7px 10px;
                border-radius: 6px;
                margin-bottom: 2px;
                font-size: 12px;
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
        self.session_list.itemClicked.connect(self._on_session_item_clicked)
        layout.addWidget(self.session_list, 1)

        # Clear All History Button
        clear_hist_btn = QPushButton("🗑️ Clear History")
        clear_hist_btn.setCursor(QCursor(Qt.PointingHandCursor))
        clear_hist_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ef4444;
                border: none;
                padding: 6px;
                font-size: 12px;
                text-align: left;
            }
            QPushButton:hover {
                color: #f87171;
                text-decoration: underline;
            }
        """)
        clear_hist_btn.clicked.connect(self._clear_all_chat_history)
        layout.addWidget(clear_hist_btn)

        return sidebar

    def _build_chatgpt_top_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(10)

        toggle_btn = QPushButton("☰")
        toggle_btn.setFixedSize(32, 32)
        toggle_btn.setCursor(QCursor(Qt.PointingHandCursor))
        toggle_btn.setToolTip("Toggle ChatGPT Sidebar")
        toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #212121;
                color: #f4f4f5;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2f2f2f;
                color: #7c8cff;
            }
        """)
        toggle_btn.clicked.connect(self._toggle_chatgpt_sidebar)
        bar.addWidget(toggle_btn)

        self.model_selector = QComboBox()
        self.model_selector.setStyleSheet("""
            QComboBox {
                background-color: #212121;
                color: #fafafa;
                border: 1px solid #3f3f46;
                border-radius: 8px;
                padding: 5px 12px;
                font-weight: bold;
                font-size: 13px;
                min-width: 220px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #18181b;
                color: #fafafa;
                selection-background-color: #3f3f46;
                selection-color: #7c8cff;
            }
        """)
        self.model_selector.addItems([
            "✨ Jarvis 2.0 (Gemini 2.0 Flash)",
            "🧠 Deep Reasoning (Gemini 2.0 Pro)",
            "🦙 Ollama Local (Llama 3)",
            "⚡ Mock Fast Mode"
        ])
        self.model_selector.currentIndexChanged.connect(self._on_model_selected)
        bar.addWidget(self.model_selector)

        bar.addStretch()

        self.model_status_badge = QLabel("● Gemini 2.0 Active")
        self.model_status_badge.setStyleSheet("color: #10b981; font-size: 12px; font-weight: 500;")
        bar.addWidget(self.model_status_badge)

        return bar

    def _toggle_chatgpt_sidebar(self):
        if hasattr(self, 'sidebar_widget'):
            visible = self.sidebar_widget.isVisible()
            self.sidebar_widget.setVisible(not visible)

    def _refresh_sidebar_sessions(self):
        if not hasattr(self, 'session_list'):
            return
        self.session_list.clear()
        sessions = self.core.db.get_all_chat_sessions()
        for sess in sessions:
            item = QListWidgetItem(f"💬 {sess['title']}")
            item.setData(Qt.UserRole, sess['session_id'])
            self.session_list.addItem(item)

    def _on_session_item_clicked(self, item: QListWidgetItem):
        sess_id = item.data(Qt.UserRole)
        if sess_id:
            self._switch_chat_session(sess_id)

    def _create_new_chat_session(self):
        import uuid
        self.current_session_id = str(uuid.uuid4())[:8]
        self._clear_messages_layout()
        self._refresh_sidebar_sessions()

    def _switch_chat_session(self, session_id: str):
        self.current_session_id = session_id
        self._clear_messages_layout()
        msgs = self.core.db.get_recent_messages(limit=50, session_id=session_id)
        for msg in msgs:
            sender = msg.get("sender", "User")
            content = msg.get("content", "")
            agent = msg.get("metadata", {}).get("agent", "Jarvis")
            if content:
                self._add_bubble_to_layout(sender, content, agent_name=agent)

    def _clear_messages_layout(self):
        if hasattr(self, 'messages_layout'):
            for i in reversed(range(self.messages_layout.count())):
                w = self.messages_layout.itemAt(i).widget()
                if w:
                    w.deleteLater()

    def _clear_all_chat_history(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to delete all chat history?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.core.db.delete_chat_session(self.current_session_id)
            self._clear_messages_layout()
            self._refresh_sidebar_sessions()

    def _on_model_selected(self, index: int):
        if index == 0:
            self.core.config["ai_provider"] = "gemini"
            self.core.config["gemini_model"] = "gemini-2.0-flash"
            self.model_status_badge.setText("● Gemini 2.0 Active")
            self.model_status_badge.setStyleSheet("color: #10b981; font-size: 12px; font-weight: 500;")
        elif index == 1:
            self.core.config["ai_provider"] = "gemini"
            self.core.config["gemini_model"] = "gemini-2.0-pro"
            self.model_status_badge.setText("● Gemini 2.0 Pro Active")
            self.model_status_badge.setStyleSheet("color: #a855f7; font-size: 12px; font-weight: 500;")
        elif index == 2:
            self.core.config["ai_provider"] = "ollama"
            self.model_status_badge.setText("● Ollama Local Active")
            self.model_status_badge.setStyleSheet("color: #3b82f6; font-size: 12px; font-weight: 500;")
        else:
            self.core.config["ai_provider"] = "mock"
            self.model_status_badge.setText("● Mock Fast Active")
            self.model_status_badge.setStyleSheet("color: #f59e0b; font-size: 12px; font-weight: 500;")


    # ─────────────────────────────────────────────────────────────
    # Vision Quick Bar & Tab Target Picker
    # ─────────────────────────────────────────────────────────────
    def _build_vision_bar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(6)
        row.setAlignment(Qt.AlignCenter)

        screen_btn = QPushButton("📸 Screen")
        screen_btn.setProperty("class", "pill-btn")
        screen_btn.setFixedHeight(26)
        screen_btn.clicked.connect(self._trigger_screen_picker)
        row.addWidget(screen_btn)

        other_btns = [
            ("👁️ Camera", "What do you see?"),
            ("🐛 Errors", "Explain this error on screen"),
            ("💻 Code", "Read code on screen"),
        ]
        for label, prompt in other_btns:
            btn = QPushButton(label)
            btn.setProperty("class", "pill-btn")
            btn.setFixedHeight(26)
            btn.clicked.connect(lambda checked, p=prompt: self._send_quick_prompt(p))
            row.addWidget(btn)
        return row

    def _trigger_screen_picker(self):
        from PySide6.QtWidgets import QDialog
        from ui.components.screen_picker_dialog import ScreenTargetDialog

        dlg = ScreenTargetDialog(self)
        if dlg.exec() == QDialog.Accepted:
            hwnd = dlg.selected_hwnd
            title = dlg.selected_title
            prompt = f"Analyze the visible contents of window '{title}'."
            self._send_screen_analysis_with_hwnd(prompt, hwnd=hwnd)

    def _send_screen_analysis_with_hwnd(self, prompt_text: str, hwnd=None):
        self._add_bubble_to_layout("User", prompt_text)
        self.send_btn.setEnabled(False)
        self.status_pill.setText("● Analyzing Screen...")

        if hasattr(self.jarvis_orb, 'set_state'):
            self.jarvis_orb.set_state("thinking")

        def run_analysis():
            res = self.core.screen_vision.analyze_screen(custom_prompt=prompt_text, hwnd=hwnd)
            return {"response": res, "agent": "VisionAgent", "type": "vision"}

        worker = AIWorkerThread(self.core, prompt_text, custom_func=run_analysis)
        self._active_threads.add(worker)
        worker.response_ready.connect(self._handle_ai_response)
        worker.finished.connect(lambda: self._active_threads.discard(worker))
        worker.finished.connect(worker.deleteLater)
        worker.start()


    # ─────────────────────────────────────────────────────────────
    # Page 1: Memory & Notes
    # ─────────────────────────────────────────────────────────────
    def _build_memory_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Top Bar with Back Button
        top_row = QHBoxLayout()
        back_btn = QPushButton("← Back to Assistant")
        back_btn.setProperty("class", "pill-btn")
        back_btn.clicked.connect(lambda: self._switch_tab(0))
        title = QLabel("Jarvis Memory & Facts Store")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #fafafa;")
        top_row.addWidget(back_btn)
        top_row.addWidget(title)
        top_row.addStretch()
        layout.addLayout(top_row)

        # Search row
        search_row = QHBoxLayout()
        self.memory_search_input = QLineEdit()
        self.memory_search_input.setPlaceholderText("Search memory facts...")
        self.memory_search_input.returnPressed.connect(self._search_memory)
        search_btn = QPushButton("🔍 Search")
        search_btn.setProperty("class", "pill-btn")
        search_btn.clicked.connect(self._search_memory)
        delete_selected_btn = QPushButton("🗑️ Delete Selected")
        delete_selected_btn.setProperty("class", "stop-btn")
        delete_selected_btn.clicked.connect(self._delete_selected_memory)
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setProperty("class", "pill-btn")
        refresh_btn.clicked.connect(self._refresh_memory_view)

        search_row.addWidget(self.memory_search_input)
        search_row.addWidget(search_btn)
        search_row.addWidget(delete_selected_btn)
        search_row.addWidget(refresh_btn)
        layout.addLayout(search_row)

        # Table
        self.memory_table = QTableWidget(0, 4)
        self.memory_table.setHorizontalHeaderLabels(["Category", "Key", "Content", "Updated At"])
        self.memory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.memory_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.memory_table)

        return page

    # ─────────────────────────────────────────────────────────────
    # Page 2: Tools, Skills & Knowledge Base
    # ─────────────────────────────────────────────────────────────
    def _build_tools_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)

        # Top Bar
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(24, 16, 24, 0)
        back_btn = QPushButton("← Back to Assistant")
        back_btn.setProperty("class", "pill-btn")
        back_btn.clicked.connect(lambda: self._switch_tab(0))
        title = QLabel("Tools, Skills & Knowledge Base")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #fafafa;")
        top_layout.addWidget(back_btn)
        top_layout.addWidget(title)
        top_layout.addStretch()
        layout.addWidget(top_widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(24, 16, 24, 20)
        scroll_layout.setSpacing(20)

        # Skills
        skills_header = QLabel("⚡ Registered Skills / Plugins")
        skills_header.setStyleSheet("font-size: 14px; font-weight: 600; color: #7c8cff;")
        scroll_layout.addWidget(skills_header)

        skills_list = self.core.skills.list_skills()
        for s in skills_list:
            card = QFrame()
            card.setObjectName("ActionCard")
            card_layout = QHBoxLayout(card)
            info_layout = QVBoxLayout()
            name_lbl = QLabel(f"🔌 {s['name'].upper()}")
            name_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #7c8cff;")
            desc_lbl = QLabel(s['description'])
            desc_lbl.setStyleSheet("font-size: 12px; color: #a1a1aa;")
            desc_lbl.setWordWrap(True)
            trigger_lbl = QLabel(f"🗝️ Triggers: {s['triggers']}")
            trigger_lbl.setStyleSheet("font-size: 11px; color: #71717a;")
            info_layout.addWidget(name_lbl)
            info_layout.addWidget(desc_lbl)
            info_layout.addWidget(trigger_lbl)
            card_layout.addLayout(info_layout)
            scroll_layout.addWidget(card)

        # Knowledge Base RAG
        kb_header = QLabel("📚 Local Knowledge Base (RAG)")
        kb_header.setStyleSheet("font-size: 14px; font-weight: 600; color: #7c8cff; margin-top: 12px;")
        scroll_layout.addWidget(kb_header)

        kb_btn_row = QHBoxLayout()
        index_folder_btn = QPushButton("📁 Index Folder")
        index_folder_btn.setProperty("class", "action-btn")
        index_folder_btn.clicked.connect(self._index_knowledge_folder)

        index_file_btn = QPushButton("📄 Index File")
        index_file_btn.setProperty("class", "pill-btn")
        index_file_btn.clicked.connect(self._index_knowledge_file)

        clear_kb_btn = QPushButton("🗑️ Clear All Files")
        clear_kb_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f1d1d;
                color: #fca5a5;
                border: 1px solid #991b1b;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #991b1b;
                color: #ffffff;
            }
        """)
        clear_kb_btn.clicked.connect(self._clear_all_knowledge_base)

        kb_btn_row.addWidget(index_folder_btn)
        kb_btn_row.addWidget(index_file_btn)
        kb_btn_row.addWidget(clear_kb_btn)
        kb_btn_row.addStretch()
        scroll_layout.addLayout(kb_btn_row)

        self.kb_status_lbl = QLabel("")
        self.kb_status_lbl.setStyleSheet("font-size: 12px; color: #7c8cff; padding: 4px;")
        scroll_layout.addWidget(self.kb_status_lbl)

        self.kb_files_lbl = QLabel("Indexed Files: 0")
        self.kb_files_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #a1a1aa; margin-top: 6px;")
        scroll_layout.addWidget(self.kb_files_lbl)

        # Knowledge Base Indexed Files Table
        self.kb_table = QTableWidget()
        self.kb_table.setColumnCount(4)
        self.kb_table.setHorizontalHeaderLabels(["Filename", "Chunks", "Path", "Action"])
        self.kb_table.setMinimumHeight(150)
        self.kb_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.kb_table.setStyleSheet("""
            QTableWidget {
                background-color: #18181b;
                color: #f4f4f5;
                border: 1px solid #27272a;
                border-radius: 8px;
                gridline-color: #27272a;
            }
            QHeaderView::section {
                background-color: #27272a;
                color: #a1a1aa;
                padding: 4px;
                border: none;
                font-weight: bold;
            }
        """)
        self.kb_table.horizontalHeader().setStretchLastSection(True)
        scroll_layout.addWidget(self.kb_table)

        self._refresh_kb_files()

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        return page


    # ─────────────────────────────────────────────────────────────
    # Page 3: Settings Page
    # ─────────────────────────────────────────────────────────────
    def _build_settings_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        # Top Bar
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(24, 16, 24, 0)
        back_btn = QPushButton("← Back to Assistant")
        back_btn.setProperty("class", "pill-btn")
        back_btn.clicked.connect(lambda: self._switch_tab(0))
        title = QLabel("System Settings")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #fafafa;")
        top_layout.addWidget(back_btn)
        top_layout.addWidget(title)
        top_layout.addStretch()
        page_layout.addWidget(top_widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(24, 16, 24, 20)
        scroll_layout.setSpacing(16)

        # Provider Card
        prov_card = QFrame()
        prov_card.setObjectName("SettingsCard")
        prov_layout = QVBoxLayout(prov_card)
        prov_layout.setContentsMargins(16, 16, 16, 16)
        prov_layout.setSpacing(10)

        lbl_prov = QLabel("AI Provider:")
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["gemini", "openai", "ollama", "mock"])
        current_p = self.core.config.get("ai_provider", "gemini")
        idx = self.provider_combo.findText(current_p)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)

        lbl_gem_key = QLabel("Gemini API Key:")
        self.gemini_key_input = QLineEdit(self.core.config.get("gemini_api_key", ""))
        self.gemini_key_input.setEchoMode(QLineEdit.Password)

        lbl_gem_model = QLabel("Gemini Model:")
        self.gemini_model_combo = QComboBox()
        self.gemini_model_combo.addItems(["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"])
        cur_m = self.core.config.get("gemini_model", "gemini-2.5-flash")
        m_idx = self.gemini_model_combo.findText(cur_m)
        if m_idx >= 0:
            self.gemini_model_combo.setCurrentIndex(m_idx)

        lbl_oai_key = QLabel("OpenAI API Key:")
        self.api_key_input = QLineEdit(self.core.config.get("openai_api_key", ""))
        self.api_key_input.setEchoMode(QLineEdit.Password)

        lbl_ollama = QLabel("Ollama Server URL:")
        self.ollama_url_input = QLineEdit(self.core.config.get("ollama_url", "http://localhost:11434"))

        prov_layout.addWidget(lbl_prov)
        prov_layout.addWidget(self.provider_combo)
        prov_layout.addWidget(lbl_gem_key)
        prov_layout.addWidget(self.gemini_key_input)
        prov_layout.addWidget(lbl_gem_model)
        prov_layout.addWidget(self.gemini_model_combo)
        prov_layout.addWidget(lbl_oai_key)
        prov_layout.addWidget(self.api_key_input)
        prov_layout.addWidget(lbl_ollama)
        prov_layout.addWidget(self.ollama_url_input)
        scroll_layout.addWidget(prov_card)

        # Integrations Card
        int_card = QFrame()
        int_card.setObjectName("SettingsCard")
        int_layout = QVBoxLayout(int_card)
        int_layout.setContentsMargins(16, 16, 16, 16)
        int_layout.setSpacing(10)

        lbl_gh = QLabel("GitHub Personal Access Token (PAT):")
        self.github_token_input = QLineEdit(self.core.config.get("github_token", ""))
        self.github_token_input.setEchoMode(QLineEdit.Password)
        int_layout.addWidget(lbl_gh)
        int_layout.addWidget(self.github_token_input)
        scroll_layout.addWidget(int_card)

        # Options Card
        opt_card = QFrame()
        opt_card.setObjectName("SettingsCard")
        opt_layout = QVBoxLayout(opt_card)
        opt_layout.setContentsMargins(16, 16, 16, 16)
        opt_layout.setSpacing(10)

        self.auto_speak_cb = QCheckBox("Automatically Speak AI Responses (TTS)")
        self.auto_speak_cb.setChecked(self.core.config.get("auto_speak_responses", True))

        self.enable_floating_cb = QCheckBox("Enable Floating Widget when Minimized")
        self.enable_floating_cb.setChecked(self.core.config.get("enable_floating_widget", True))

        self.wake_word_cb = QCheckBox("Enable Wake Word ('Hey Jarvis')")
        self.wake_word_cb.setChecked(self.core.config.get("enable_wake_word", False))

        self.proactive_cb = QCheckBox("Enable Proactive Intelligence (Battery/CPU Alerts)")
        self.proactive_cb.setChecked(self.core.config.get("enable_proactive_monitor", True))

        opt_layout.addWidget(self.auto_speak_cb)
        opt_layout.addWidget(self.enable_floating_cb)
        opt_layout.addWidget(self.wake_word_cb)
        opt_layout.addWidget(self.proactive_cb)
        scroll_layout.addWidget(opt_card)

        # Custom App Icon & Logo Card
        icon_card = QFrame()
        icon_card.setObjectName("SettingsCard")
        icon_layout = QVBoxLayout(icon_card)
        icon_layout.setContentsMargins(16, 16, 16, 16)
        icon_layout.setSpacing(10)

        lbl_icon_title = QLabel("🖼️ Custom Window Icon & Title Bar Logo:")
        lbl_icon_title.setStyleSheet("font-weight: bold; color: #fafafa;")

        lbl_icon_desc = QLabel("Set your own custom image for the Jarvis application window icon & title bar.")
        lbl_icon_desc.setStyleSheet("color: #a1a1aa; font-size: 12px;")

        change_icon_btn = QPushButton("📁 Choose Custom Image...")
        change_icon_btn.setProperty("class", "pill-btn")
        change_icon_btn.setFixedWidth(200)
        change_icon_btn.clicked.connect(self._change_custom_window_icon)

        icon_layout.addWidget(lbl_icon_title)
        icon_layout.addWidget(lbl_icon_desc)
        icon_layout.addWidget(change_icon_btn)
        scroll_layout.addWidget(icon_card)

        # Save Button
        save_btn = QPushButton("Save Settings")
        save_btn.setProperty("class", "action-btn")
        save_btn.clicked.connect(self._save_settings)
        scroll_layout.addWidget(save_btn)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        page_layout.addWidget(scroll)
        return page

    def _update_window_icon(self):
        """Loads custom or generated jarvis_icon image onto application window title bar."""
        from PySide6.QtGui import QIcon
        from pathlib import Path
        assets_dir = Path(os.path.dirname(__file__)) / ".." / "assets"
        for name in ["jarvis_icon.png", "jarvis_icon.ico", "jarvis_icon.jpg", "logo.png"]:
            icon_path = (assets_dir / name).resolve()
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
                break

    def _change_custom_window_icon(self):
        """Allows user to select any image from disk to set as custom window icon."""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import shutil
        from pathlib import Path

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Custom App Icon",
            "",
            "Image Files (*.png *.jpg *.jpeg *.ico *.webp)"
        )
        if file_path:
            try:
                assets_dir = Path(os.path.dirname(__file__)) / ".." / "assets"
                assets_dir.mkdir(parents=True, exist_ok=True)
                dest = assets_dir / "jarvis_icon.png"
                shutil.copy(file_path, dest)
                self._update_window_icon()
                QMessageBox.information(
                    self,
                    "Icon Updated",
                    f"✅ Custom window icon set successfully!\nSelected image: {os.path.basename(file_path)}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to set custom icon: {e}")


    # ─────────────────────────────────────────────────────────────
    # Event Handlers & Core Logic
    # ─────────────────────────────────────────────────────────────
    def _load_chat_history(self):
        msgs = self.core.db.get_recent_messages(limit=15)
        for msg in msgs:
            sender = msg.get("sender", "User")
            content = msg.get("content", "")
            agent = msg.get("metadata", {}).get("agent", "Jarvis")
            if content:
                self._add_bubble_to_layout(sender, content, agent_name=agent)

    def _add_bubble_to_layout(self, sender: str, content: str, agent_name: str = "Jarvis", timestamp: str = None):
        bubble = ChatBubble(sender=sender, content=content, agent_name=agent_name, timestamp=timestamp)
        self.messages_layout.addWidget(bubble)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def _on_send_clicked(self):
        text = self.chat_input.text().strip()
        if not text:
            return
        self.chat_input.clear()
        self._add_bubble_to_layout("User", text)

        # Update orb state to thinking
        if hasattr(self.jarvis_orb, 'set_state'):
            self.jarvis_orb.set_state("thinking")

        self.send_btn.setEnabled(False)
        self.status_pill.setText("● Thinking...")

        session_id = getattr(self, "current_session_id", "default")
        worker = AIWorkerThread(self.core, text, session_id=session_id)
        self._active_threads.add(worker)
        worker.response_ready.connect(self._handle_ai_response)
        worker.finished.connect(lambda: self._active_threads.discard(worker))
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def animate_workspace_panel(self, expand: bool, target_width: int = 400):
        if not hasattr(self, "dynamic_panel"):
            return

        start_val = self.dynamic_panel.maximumWidth()
        end_val = target_width if expand else 0

        self.panel_anim = QPropertyAnimation(self.dynamic_panel, b"maximumWidth")
        self.panel_anim.setDuration(350)
        self.panel_anim.setStartValue(start_val)
        self.panel_anim.setEndValue(end_val)
        self.panel_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.panel_anim.start()

    def _handle_ai_response(self, result: dict):
        self.send_btn.setEnabled(True)
        self.status_pill.setText("● Ready")
        self._refresh_sidebar_sessions()

        # Update orb state to speaking
        if hasattr(self.jarvis_orb, 'set_state'):
            self.jarvis_orb.set_state("speaking")
            QTimer.singleShot(2500, lambda: self.jarvis_orb.set_state("idle") if hasattr(self.jarvis_orb, 'set_state') else None)


        if result.get("response"):
            self._add_bubble_to_layout("Jarvis", result["response"], agent_name=result.get("agent", "Jarvis"))

        # Workspace Panel Morphing
        if result.get("type") == "workspace" or result.get("workspace_mode"):
            mode = result.get("workspace_mode", "news")
            data = result.get("workspace_data")
            if hasattr(self, 'dynamic_panel'):
                self.dynamic_panel.switch_mode(mode, items=data)
                self.animate_workspace_panel(expand=True)



    def _send_quick_prompt(self, prompt_text: str):
        cleaned = prompt_text.replace("⚡ ", "").replace("🌐 ", "").replace("📝 ", "").replace("📸 ", "").replace("❓ ", "")
        self.chat_input.setText(cleaned)
        self._on_send_clicked()

    def _on_voice_clicked(self):
        from speech.stt import VoiceListenerThread
        self.status_pill.setText("🔴 Listening...")

        if hasattr(self.jarvis_orb, 'set_state'):
            self.jarvis_orb.set_state("listening")

        self.voice_btn.setEnabled(False)
        self.voice_btn.setText("🎤 Listening...")

        voice_thread = VoiceListenerThread(timeout=6, phrase_time_limit=10)
        self._active_threads.add(voice_thread)

        def on_recognized(text):
            self.status_pill.setText("● Thinking...")
            if hasattr(self.jarvis_orb, 'set_state'):
                self.jarvis_orb.set_state("thinking")

            worker = AIWorkerThread(self.core, text)
            self._active_threads.add(worker)
            worker.response_ready.connect(self._handle_voice_response)
            worker.finished.connect(lambda: self._active_threads.discard(worker))
            worker.finished.connect(worker.deleteLater)
            worker.start()

        def on_error(err_msg):
            self.status_pill.setText("● Ready")
            if hasattr(self.jarvis_orb, 'set_state'):
                self.jarvis_orb.set_state("idle")
            self.voice_btn.setEnabled(True)
            self.voice_btn.setText("🎤 Voice")
            if "listening timed out" not in err_msg.lower() and "no speech" not in err_msg.lower():
                if hasattr(self.core, "tts"):
                    self.core.tts.speak(f"Notice: {err_msg}")

        voice_thread.text_recognized.connect(on_recognized)
        voice_thread.error_occurred.connect(on_error)
        voice_thread.finished.connect(lambda: self._active_threads.discard(voice_thread))
        voice_thread.finished.connect(voice_thread.deleteLater)
        voice_thread.start()

    def _handle_voice_response(self, result: dict):
        self.voice_btn.setEnabled(True)
        self.voice_btn.setText("🎤 Voice")
        self.status_pill.setText("● Ready")

        if hasattr(self.jarvis_orb, 'set_state'):
            self.jarvis_orb.set_state("speaking")
            QTimer.singleShot(2500, lambda: self.jarvis_orb.set_state("idle") if hasattr(self.jarvis_orb, 'set_state') else None)

        if result.get("response"):
            self._add_bubble_to_layout("Jarvis", result["response"], agent_name=result.get("agent", "Jarvis"))

    def _on_stop_clicked(self):
        """Interrupts speech and cancels active tasks."""
        if hasattr(self.core, "tts"):
            self.core.tts.stop_audio()

        for thread in list(self._active_threads):
            if thread.isRunning():
                thread.quit()
                thread.wait(300)

        self._active_threads.clear()

        if hasattr(self.jarvis_orb, 'set_state'):
            self.jarvis_orb.set_state("idle")

        self.status_pill.setText("● Ready")
        self.voice_btn.setEnabled(True)
        self.voice_btn.setText("🎤 Voice")
        self.send_btn.setEnabled(True)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                if self.core.config.get("enable_floating_widget", True):
                    self.floating_widget.reposition_to_corner()
                    self.floating_widget.show()
            elif not self.isMinimized():
                if hasattr(self, "floating_widget"):
                    self.floating_widget.hide()
        super().changeEvent(event)

    def _restore_from_floating(self):
        self.showNormal()
        self.activateWindow()
        if hasattr(self, "floating_widget"):
            self.floating_widget.hide()

    def closeEvent(self, event):
        if hasattr(self, "floating_widget"):
            self.floating_widget.close()

        # Stop pynput-based hotkey listener thread
        if hasattr(self, "hotkey_listener") and self.hotkey_listener.isRunning():
            try:
                self.hotkey_listener.stop()          # signals inner loop to exit
                self.hotkey_listener.quit()
                self.hotkey_listener.wait(800)
                if self.hotkey_listener.isRunning():
                    self.hotkey_listener.terminate()
                    self.hotkey_listener.wait(300)
            except Exception:
                pass

        # Stop Ghost Copilot proactive monitor thread
        if hasattr(self, "ghost_copilot") and self.ghost_copilot.isRunning():
            try:
                self.ghost_copilot.quit()
                self.ghost_copilot.wait(800)
            except Exception:
                pass

        # Stop TTS audio
        if hasattr(self.core, "tts"):
            self.core.tts.stop_audio()

        # Stop proactive intelligence monitor
        if hasattr(self.core, "stop_proactive_monitor"):
            self.core.stop_proactive_monitor()

        # Stop all AI / voice worker threads
        for thread in list(self._active_threads):
            if thread.isRunning():
                thread.quit()
                thread.wait(500)
        self._active_threads.clear()

        event.accept()


    def _clear_chat(self):
        self.core.db.clear_history()
        while self.messages_layout.count():
            child = self.messages_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _save_settings(self):
        prov = self.provider_combo.currentText()
        gemini_key = self.gemini_key_input.text().strip()
        gemini_model = self.gemini_model_combo.currentText()
        openai_key = self.api_key_input.text().strip()
        url = self.ollama_url_input.text().strip()
        auto_speak = self.auto_speak_cb.isChecked()
        github_token = self.github_token_input.text().strip()

        model = gemini_model if prov == "gemini" else ""
        self.core.update_provider_config(prov, api_key=openai_key, gemini_api_key=gemini_key,
                                          gemini_model=gemini_model, ollama_url=url, model=model)
        self.core.config.set("auto_speak_responses", auto_speak)
        self.core.config.set("enable_floating_widget", self.enable_floating_cb.isChecked())
        self.core.config.set("enable_wake_word", self.wake_word_cb.isChecked())
        self.core.config.set("enable_proactive_monitor", self.proactive_cb.isChecked())
        if github_token:
            self.core.config.set("github_token", github_token)
        QMessageBox.information(self, "Settings Saved", f"Settings updated successfully!\nProvider: {prov.upper()}")

    # ─────────────────────────────────────────────────────────────
    # Memory Helpers
    # ─────────────────────────────────────────────────────────────
    def _search_memory(self):
        query = self.memory_search_input.text().strip()
        if not query:
            self._refresh_memory_view()
            return
        facts = self.core.db.search_memory_facts(query)
        self._populate_memory_table(facts)

    def _delete_selected_memory(self):
        selected = self.memory_table.selectedItems()
        if not selected:
            return
        row = self.memory_table.currentRow()
        key_item = self.memory_table.item(row, 1)
        if key_item:
            key = key_item.text()
            self.core.db.delete_memory_fact(key)
            self._refresh_memory_view()

    def _populate_memory_table(self, facts: list):
        self.memory_table.setRowCount(len(facts))
        for idx, f in enumerate(facts):
            self.memory_table.setItem(idx, 0, QTableWidgetItem(f["category"]))
            self.memory_table.setItem(idx, 1, QTableWidgetItem(f["key"]))
            self.memory_table.setItem(idx, 2, QTableWidgetItem(f["value"]))
            self.memory_table.setItem(idx, 3, QTableWidgetItem(f["updated_at"]))

    def _refresh_memory_view(self):
        facts = self.core.db.get_all_memory_facts()
        self._populate_memory_table(facts)

    # ─────────────────────────────────────────────────────────────
    # Knowledge Base RAG Helpers
    # ─────────────────────────────────────────────────────────────
    def _index_knowledge_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Index")
        if folder:
            self.kb_status_lbl.setText("⏳ Indexing folder...")
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()
            result = self.core.index_knowledge_folder(folder)
            if result.get("success", True):
                count = result.get("indexed", 0)
                self.kb_status_lbl.setText(f"✅ Indexed {count} files from {folder}")
            else:
                self.kb_status_lbl.setText(f"❌ {result.get('error', 'Failed')}")
            self._refresh_kb_files()

    def _index_knowledge_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select File to Index", "",
            "Supported Files (*.txt *.md *.py *.js *.pdf *.json *.yaml *.html);;All Files (*)"
        )
        if filepath:
            result = self.core.index_knowledge_file(filepath)
            chunks = result.get("chunks", 0)
            if result.get("success") and chunks > 0:
                self.kb_status_lbl.setText(f"✅ Indexed {chunks} chunks from {result.get('file', '')}")
            else:
                err = result.get("error", "Empty file or image-only PDF with no text layer")
                self.kb_status_lbl.setText(f"⚠️ {err} ({result.get('file', '')})")
            self._refresh_kb_files()


    def _refresh_kb_files(self):
        if hasattr(self, 'kb_files_lbl') and hasattr(self, 'kb_table'):
            items = self.core.db.get_indexed_files_with_counts()
            self.kb_files_lbl.setText(f"Indexed Files: {len(items)}")
            self.kb_table.setRowCount(len(items))

            from pathlib import Path
            for idx, item in enumerate(items):
                path_str = item["filepath"]
                fname = Path(path_str).name
                chunks_str = str(item["chunks"])

                self.kb_table.setItem(idx, 0, QTableWidgetItem(fname))
                self.kb_table.setItem(idx, 1, QTableWidgetItem(chunks_str))
                self.kb_table.setItem(idx, 2, QTableWidgetItem(path_str))

                del_btn = QPushButton("🗑️ Remove")
                del_btn.setCursor(QCursor(Qt.PointingHandCursor))
                del_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #7f1d1d;
                        color: #fca5a5;
                        border: none;
                        border-radius: 4px;
                        padding: 3px 8px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #991b1b;
                        color: #ffffff;
                    }
                """)
                del_btn.clicked.connect(lambda checked, p=path_str: self._delete_indexed_file(p))
                self.kb_table.setCellWidget(idx, 3, del_btn)

    def _delete_indexed_file(self, filepath: str):
        from pathlib import Path
        self.core.db.clear_rag_chunks_for_file(filepath)
        self.kb_status_lbl.setText(f"🗑️ Removed: {Path(filepath).name}")
        self._refresh_kb_files()

    def _clear_all_knowledge_base(self):
        reply = QMessageBox.question(
            self, "Clear Knowledge Base",
            "Are you sure you want to remove ALL indexed files and folders from the local knowledge base?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.core.db.clear_all_rag_chunks()
            self.kb_status_lbl.setText("🗑️ Knowledge Base cleared completely.")
            self._refresh_kb_files()


    # ─────────────────────────────────────────────────────────────
    # Proactive Monitor Signals
    # ─────────────────────────────────────────────────────────────
    def _setup_proactive_monitor(self):
        monitor = self.core.get_proactive_monitor()
        if monitor:
            monitor.alert_fired.connect(self._on_proactive_alert)
            monitor.daily_briefing.connect(self._on_daily_briefing)

    def _on_proactive_alert(self, alert_type: str, title: str, message: str):
        full_message = f"**{title}**\n{message}"
        self._add_bubble_to_layout("Jarvis", full_message, agent_name="ProactiveAlert")
        if alert_type in ("battery_critical", "battery_low") and hasattr(self.core, 'tts'):
            if self.core.config.get("auto_speak_responses", True):
                self.core.tts.speak(message[:150])

    def _on_daily_briefing(self, briefing: str):
        self._add_bubble_to_layout("Jarvis", briefing, agent_name="DailyBriefing")
        if hasattr(self.core, 'tts') and self.core.config.get("auto_speak_responses", True):
            self.core.tts.speak("Good morning! Here's your daily briefing.")

    # ─────────────────────────────────────────────────────────────
    # Phase 11 Extension Handlers (Palette, Floating Orb, Ghost Copilot)
    # ─────────────────────────────────────────────────────────────
    def _toggle_main_window_visibility(self):
        if self.isVisible() and not self.isMinimized():
            self.hide()
        else:
            self.showNormal()
            self.activateWindow()

    def _on_palette_command_submitted(self, text: str):
        worker = AIWorkerThread(self.core, text)
        worker.response_ready.connect(lambda res: self._handle_palette_response(text, res))
        self._active_threads.add(worker)
        worker.finished.connect(lambda: self._active_threads.discard(worker))
        worker.start()

    def _handle_palette_response(self, prompt: str, result: dict):
        response_text = result.get("response", "Done.")
        if hasattr(self, 'command_palette'):
            self.command_palette.set_result(response_text)
        self._add_bubble_to_layout("User", prompt)
        self._add_bubble_to_layout("Jarvis", response_text, agent_name=result.get("agent", "Jarvis"))

    def _on_ghost_copilot_error(self, title: str, suggestion: str):
        full_msg = f"{title}\n\n{suggestion}"
        self._add_bubble_to_layout("Jarvis", full_msg, agent_name="GhostCopilot")

