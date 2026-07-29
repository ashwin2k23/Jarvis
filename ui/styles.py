"""
Invisible Intelligence — Raycast, Linear, Arc & Apple Intelligence Inspired Stylesheet.
Quiet. Minimal. Confident.
Palette:
  Canvas:    #09090b
  Surface:   #121215
  Border:    rgba(255, 255, 255, 0.08) / #27272a
  Primary:   #FAFAFA
  Secondary: #A1A1AA
  Accent:    #7C8CFF (single accent color)
"""

DARK_GLASS_STYLESHEET = """
/* ─────────────────────────────────────────────────────────────
   Base Canvas & Window Setup
   ───────────────────────────────────────────────────────────── */
QMainWindow {
    background-color: #09090b;
    color: #fafafa;
    font-family: 'Inter', 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

QWidget {
    font-family: 'Inter', 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #a1a1aa;
}

/* Explicitly prevent unwanted default borders on labels */
QLabel, QLabel.form-label, QLabel.card-header, QFrame QLabel {
    border: none !important;
    background: transparent;
}

QLabel.form-label {
    color: #a1a1aa;
    font-size: 13px;
    font-weight: 500;
}

QLabel.card-header {
    color: #fafafa;
    font-size: 15px;
    font-weight: 600;
}

/* ─────────────────────────────────────────────────────────────
   Minimal Top Header & Greeting
   ───────────────────────────────────────────────────────────── */
#HeaderTitle {
    color: #fafafa;
    font-size: 28px;
    font-weight: 600;
    letter-spacing: -0.5px;
    background: transparent;
    border: none;
}

#HeaderSubtitle {
    color: #a1a1aa;
    font-size: 16px;
    font-weight: 400;
    background: transparent;
    border: none;
}

/* ─────────────────────────────────────────────────────────────
   Chat Scroll Area & Custom Minimal Scrollbar
   ───────────────────────────────────────────────────────────── */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background: #09090b;
    width: 6px;
    margin: 0px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.12);
    min-height: 24px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.22);
}

/* ─────────────────────────────────────────────────────────────
   Raycast & Linear Style Floating Command / Input Pill
   ───────────────────────────────────────────────────────────── */
#InputFrame {
    background-color: #121215;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 8px 14px;
}

#InputFrame:focus-within {
    border: 1px solid #7c8cff;
}

#ChatInput {
    background-color: transparent;
    border: none;
    color: #fafafa;
    font-size: 15px;
    padding: 4px;
}

/* ─────────────────────────────────────────────────────────────
   Action Buttons (Raycast / Linear Aesthetic)
   ───────────────────────────────────────────────────────────── */
QPushButton.action-btn {
    background-color: #7c8cff;
    color: #09090b;
    border: 1px solid #7c8cff;
    border-radius: 8px;
    padding: 7px 16px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.action-btn:hover {
    background-color: #94a3ff;
    border-color: #94a3ff;
}

QPushButton.voice-btn {
    background-color: rgba(255, 255, 255, 0.05);
    color: #a1a1aa;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton.voice-btn:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: #fafafa;
    border-color: rgba(255, 255, 255, 0.16);
}

QPushButton.stop-btn {
    background-color: rgba(239, 68, 68, 0.12);
    color: #fca5a5;
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton.stop-btn:hover {
    background-color: rgba(239, 68, 68, 0.25);
    color: #ffffff;
}

/* ─────────────────────────────────────────────────────────────
   Minimal Footer Navigation Bar
   ───────────────────────────────────────────────────────────── */
QPushButton.footer-nav-btn {
    background-color: transparent;
    color: #a1a1aa;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton.footer-nav-btn:hover {
    background-color: rgba(255, 255, 255, 0.05);
    color: #fafafa;
}

QPushButton.footer-nav-btn:checked {
    background-color: rgba(124, 140, 255, 0.12);
    color: #7c8cff;
    border: 1px solid rgba(124, 140, 255, 0.25);
    font-weight: 600;
}

/* ─────────────────────────────────────────────────────────────
   User & Assistant Message Cards (Linear Typography & Spacing)
   ───────────────────────────────────────────────────────────── */
QFrame.user-bubble {
    background-color: #181820;
    border: 1px solid rgba(124, 140, 255, 0.2);
    border-radius: 12px;
    border-bottom-right-radius: 4px;
    padding: 12px 16px;
}

QFrame.jarvis-bubble {
    background-color: #121215;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    border-bottom-left-radius: 4px;
    padding: 12px 16px;
}

QFrame.system-bubble {
    background-color: #121215;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 8px 12px;
}

/* ─────────────────────────────────────────────────────────────
   Settings & Card Containers
   ───────────────────────────────────────────────────────────── */
#SettingsCard, #ActionCard, QFrame.settings-card, QFrame.card-panel {
    background-color: #121215;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
}

/* Quick Action Pills */
QPushButton.pill-btn {
    background-color: #121215;
    color: #a1a1aa;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton.pill-btn:hover {
    background-color: rgba(255, 255, 255, 0.05);
    color: #fafafa;
    border-color: #7c8cff;
}

/* Status Indicator Pill */
#StatusPill {
    background-color: #121215;
    color: #7c8cff;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 500;
}

/* Form Inputs, Dropdowns, Text Editors */
QLineEdit, QComboBox, QTextEdit, QTableWidget, QListView, QListWidget {
    background-color: #121215;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 8px 12px;
    color: #fafafa;
    font-size: 13px;
    min-height: 20px;
}

QLineEdit:hover, QComboBox:hover, QTextEdit:hover {
    border: 1px solid rgba(255, 255, 255, 0.16);
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QTableWidget:focus {
    border: 1px solid #7c8cff;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #121215;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    color: #fafafa;
    selection-background-color: rgba(124, 140, 255, 0.2);
    selection-color: #ffffff;
    padding: 4px;
}

QCheckBox {
    border: none;
    background: transparent;
    color: #fafafa;
    font-size: 13px;
    font-weight: 500;
    padding: 4px 0px;
}
"""
