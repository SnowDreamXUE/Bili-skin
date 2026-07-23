import sys
import os

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.dirname(base_path))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from gui_app.ui.main_window import BiliGarbGUI


def main():
    app = QApplication(sys.argv)
    icon_path = os.path.join(base_path, "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    window = BiliGarbGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()