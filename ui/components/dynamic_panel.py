import webbrowser
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QUrl
from PySide6.QtGui import QFont, QColor, QCursor, QDesktopServices

class CardWidget(QFrame):
    """Interactive dark-glass content card for dynamic panel."""

    clicked = Signal()

    def __init__(self, title: str, subtitle: str, body: str = "", link: str = None, tag: str = None, parent=None):
        super().__init__(parent)
        self.link = link
        self.setObjectName("DynamicCard")
        self.setStyleSheet("""
            QFrame#DynamicCard {
                background-color: #18181b;
                border: 1px solid #27272a;
                border-radius: 10px;
                padding: 12px;
            }
            QFrame#DynamicCard:hover {
                border: 1px solid #7c8cff;
                background-color: #1f1f23;
            }
        """)
        self.setCursor(QCursor(Qt.PointingHandCursor) if (link or tag == "Video") else QCursor(Qt.ArrowCursor))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header tag if present
        if tag:
            tag_lbl = QLabel(tag.upper())
            tag_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
            tag_lbl.setStyleSheet("color: #7c8cff; letter-spacing: 0.5px;")
            layout.addWidget(tag_lbl)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_lbl.setStyleSheet("color: #f4f4f5;")
        title_lbl.setWordWrap(True)
        layout.addWidget(title_lbl)

        # Subtitle / Source info
        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setFont(QFont("Segoe UI", 8))
            sub_lbl.setStyleSheet("color: #a1a1aa;")
            layout.addWidget(sub_lbl)

        # Body snippet
        if body:
            body_lbl = QLabel(body)
            body_lbl.setFont(QFont("Segoe UI", 9))
            body_lbl.setStyleSheet("color: #d4d4d8;")
            body_lbl.setWordWrap(True)
            layout.addWidget(body_lbl)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            if self.link:
                try:
                    QDesktopServices.openUrl(QUrl(self.link))
                except Exception:
                    pass
        super().mousePressEvent(event)


class DynamicWorkspacePanel(QFrame):
    """
    Morphing Dynamic Workspace Panel.
    Displays News 🌍, Trends 📈, Tech 💻, Videos 📺, and Newsletter 📄 cards with Embedded Video Player.
    """

    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DynamicPanel")
        self.setStyleSheet("""
            QFrame#DynamicPanel {
                background-color: #121215;
                border-left: 1px solid #27272a;
            }
        """)

        self.current_mode = "news"
        self.current_videos_cache = []

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # ── 1. Top Header Bar ──
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        self.title_lbl = QLabel("🌍 World News")
        self.title_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.title_lbl.setStyleSheet("color: #f4f4f5;")
        header.addWidget(self.title_lbl, 1)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #a1a1aa;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27272a;
                color: #ffffff;
            }
        """)
        self.close_btn.clicked.connect(self.close_requested.emit)
        header.addWidget(self.close_btn)

        main_layout.addLayout(header)

        # ── 2. Mode Switcher Selector Pills ──
        pills_layout = QHBoxLayout()
        pills_layout.setSpacing(6)

        self.mode_buttons = {}
        modes = [
            ("news", "🌍 News"),
            ("trends", "📈 Trends"),
            ("tech", "💻 Tech"),
            ("videos", "📺 Videos"),
            ("brief", "📄 Brief")
        ]

        for mode_key, mode_title in modes:
            btn = QPushButton(mode_title)
            btn.setFont(QFont("Segoe UI", 8, QFont.Bold))
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #18181b;
                    color: #a1a1aa;
                    border: 1px solid #27272a;
                    border-radius: 6px;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    border: 1px solid #7c8cff;
                    color: #ffffff;
                }
                QPushButton:checked {
                    background-color: #7c8cff;
                    color: #09090b;
                    border: 1px solid #7c8cff;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, m=mode_key: self.switch_mode(m))
            self.mode_buttons[mode_key] = btn
            pills_layout.addWidget(btn)

        self.mode_buttons["news"].setChecked(True)
        main_layout.addLayout(pills_layout)

        # ── 3. Scrollable Cards List Area ──
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #121215;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background: #27272a;
                border-radius: 3px;
            }
        """)

        self.card_container = QWidget()
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setContentsMargins(0, 4, 0, 4)
        self.card_layout.setSpacing(10)
        self.card_layout.setAlignment(Qt.AlignTop)

        self.scroll.setWidget(self.card_container)
        main_layout.addWidget(self.scroll, 1)

    def switch_mode(self, mode: str, items: list = None, query: str = None):
        self.current_mode = mode
        for m, btn in self.mode_buttons.items():
            btn.setChecked(m == mode)

        title_map = {
            "news": "🌍 World News",
            "trends": "📈 Trending Topics",
            "tech": "💻 Tech & AI Insights",
            "videos": f"📺 Videos: {query}" if query else "📺 Related Videos",
            "brief": "📄 Daily Briefing"
        }
        self.title_lbl.setText(title_map.get(mode, "Dynamic Workspace"))

        from search.dynamic_feed import DynamicFeedEngine
        engine = DynamicFeedEngine()

        if items:
            if mode == "news":
                self.populate_news(items)
            elif mode == "trends":
                self.populate_trends(items)
            elif mode == "tech":
                self.populate_tech(items)
            elif mode == "videos":
                self.populate_videos(items)
            elif mode == "brief":
                self.populate_briefing(items)
            return

        if mode == "news":
            fetched_items = engine.fetch_news_feed("world")
            self.populate_news(fetched_items)
        elif mode == "trends":
            fetched_items = engine.fetch_trending_topics()
            self.populate_trends(fetched_items)
        elif mode == "tech":
            fetched_items = engine.fetch_tech_ai_feed()
            self.populate_tech(fetched_items)
        elif mode == "videos":
            search_topic = query if query else "trending highlights"
            fetched_items = engine.fetch_video_feed(search_topic)
            self.populate_videos(fetched_items)
        elif mode == "brief":
            digest = engine.generate_newsletter_digest()
            self.populate_briefing(digest)


    def _clear_cards(self):
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def populate_news(self, articles: list):
        self._clear_cards()
        for art in articles:
            sub = f"📰 {art.get('source', 'News')} • {art.get('pub_date', '')}"
            card = CardWidget(
                title=art.get("title", ""),
                subtitle=sub,
                body=art.get("snippet", ""),
                link=art.get("link"),
                tag=art.get("category", "News")
            )
            self.card_layout.addWidget(card)

    def populate_trends(self, trends: list):
        self._clear_cards()
        for t in trends:
            sub = f"🔥 Rank #{t.get('rank', 1)} • Source: {t.get('source', 'Web')}"
            card = CardWidget(
                title=f"{t.get('rank')}. {t.get('topic')}",
                subtitle=sub,
                body=f"**Why it's trending**: {t.get('reason')}\n{t.get('summary')}",
                link=t.get("link"),
                tag=t.get("tag", "Trending")
            )
            self.card_layout.addWidget(card)

    def populate_tech(self, tech_items: list):
        self._clear_cards()
        for item in tech_items:
            sub = f"🏢 {item.get('company')} • Official Update"
            card = CardWidget(
                title=item.get("title", ""),
                subtitle=sub,
                body=item.get("summary", ""),
                link=item.get("link"),
                tag=item.get("badge", "Tech")
            )
            self.card_layout.addWidget(card)

    def populate_videos(self, videos: list, current_query: str = ""):
        self.current_videos_cache = videos
        self._clear_cards()

        # Add Search Bar for Video Panel
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 Search YouTube videos...")
        if current_query:
            search_box.setText(current_query)
        search_box.setFont(QFont("Segoe UI", 9))
        search_box.setStyleSheet("""
            QLineEdit {
                background-color: #18181b;
                color: #f4f4f5;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                padding: 6px 10px;
                margin-bottom: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #7c8cff;
            }
        """)

        def on_video_search():
            q = search_box.text().strip()
            if q:
                from search.dynamic_feed import DynamicFeedEngine
                vids = DynamicFeedEngine().fetch_video_feed(q)
                self.populate_videos(vids, current_query=q)

        search_box.returnPressed.connect(on_video_search)
        self.card_layout.addWidget(search_box)

        for vid in videos:
            embed_url = vid.get("embed_url", f"https://www.youtube-nocookie.com/embed/{vid.get('video_id', '')}?autoplay=1")
            video_id = vid.get("video_id", "")
            title = vid.get("title", "")
            sub = f"🎬 {vid.get('channel')} • Click to Play inside Jarvis"
            
            card = CardWidget(
                title=title,
                subtitle=sub,
                body="▶ Click card to stream embedded video directly inside Jarvis.",
                link=None,  # Do not pass external link so browser isn't opened
                tag="Video"
            )
            # Bind card click to inline player
            card.clicked.connect(lambda u=embed_url, t=title, v=video_id: self.play_embedded_video(u, t, v))
            self.card_layout.addWidget(card)


    def play_embedded_video(self, embed_url: str, title: str, video_id: str = None):
        """Plays YouTube video directly inside the Jarvis panel using QWebEngineView with youtube-nocookie HTML5 player."""
        self._clear_cards()

        # Extract 11-char video ID if missing
        if not video_id:
            import re
            match = re.search(r'(?:v=|\/embed\/|\/watch\?v=)([a-zA-Z0-9_-]{11})', embed_url)
            if match:
                video_id = match.group(1)

        # Top Control Bar for Video
        control_bar = QHBoxLayout()
        back_btn = QPushButton("◀ Back to Videos")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #18181b;
                color: #7c8cff;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27272a;
                color: #ffffff;
            }
        """)
        back_btn.clicked.connect(lambda: self.populate_videos(self.current_videos_cache))
        control_bar.addWidget(back_btn)
        control_bar.addStretch()
        self.card_layout.addLayout(control_bar)

        # Video Title Label
        vid_title = QLabel(title)
        vid_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        vid_title.setStyleSheet("color: #f4f4f5;")
        vid_title.setWordWrap(True)
        self.card_layout.addWidget(vid_title)

        # Embedded HTML5 WebEngine View Player
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from PySide6.QtWebEngineCore import QWebEngineSettings

            web_view = QWebEngineView()
            web_view.setMinimumHeight(300)
            web_view.setStyleSheet("background-color: #000000; border-radius: 8px;")

            page = web_view.page()
            page.profile().setHttpUserAgent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

            settings = page.settings()
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
            settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)

            if video_id:
                html_code = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * {{ margin: 0; padding: 0; background: #000000; overflow: hidden; }}
    html, body {{ width: 100%; height: 100%; }}
    iframe {{ width: 100%; height: 100%; border: none; }}
  </style>
</head>
<body>
  <iframe src="https://www.youtube-nocookie.com/embed/{video_id}?autoplay=1&enablejsapi=1&rel=0&modestbranding=1" 
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
          allowfullscreen>
  </iframe>
</body>
</html>"""
                web_view.setHtml(html_code, QUrl("https://www.youtube-nocookie.com"))
            else:
                web_view.setUrl(QUrl(embed_url))

            self.card_layout.addWidget(web_view, 1)
        except Exception as e:
            err_lbl = QLabel(f"⚠️ Unable to load embedded web player: {e}")
            err_lbl.setStyleSheet("color: #ef4444;")
            self.card_layout.addWidget(err_lbl)


    def populate_briefing(self, digest: dict):
        self._clear_cards()
        title_card = CardWidget(
            title=digest.get("title", "Daily Briefing"),
            subtitle=digest.get("date", ""),
            tag="Morning Brief"
        )
        self.card_layout.addWidget(title_card)

        for sec in digest.get("sections", []):
            sec_card = CardWidget(
                title=sec.get("heading", ""),
                subtitle="",
                body=sec.get("text", "")
            )
            self.card_layout.addWidget(sec_card)
