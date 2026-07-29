import sys
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from PySide6.QtWidgets import QApplication
        from app.core import JarvisCoreController
        from ui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName("Jarvis AI Desktop Assistant")

        # Set default application font — prevents 'QFont::setPointSize <= 0' warnings
        from PySide6.QtGui import QFont
        default_font = QFont("Segoe UI", 10)
        default_font.setPointSize(10)
        app.setFont(default_font)

        # Initialize Core Controller & Main UI Window
        core = JarvisCoreController()
        window = MainWindow(core)
        window.show()

        sys.exit(app.exec())
    except ImportError as e:
        print(f"[Jarvis Launcher Error] Missing required dependency: {e}")
        print("Please install required dependencies using: pip install -r requirements.txt")
    except Exception as e:
        print(f"[Jarvis Launcher Error] Fatal startup error: {e}")

if __name__ == "__main__":
    main()
