import sys

from PySide6.QtWidgets import QApplication

from gui_app.ui.main_window import BiliGarbGUI


def main():
    app = QApplication(sys.argv)
    window = BiliGarbGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()