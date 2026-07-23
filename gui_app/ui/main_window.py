from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox

from gui_app.config.style import ELEMENTUI_STYLE
from gui_app.ui.search_page import SearchPage
from gui_app.ui.result_page import ResultPage
from gui_app.ui.download_page import DownloadPage


class BiliGarbGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bilibili 装扮/收藏集下载器")
        self.setMinimumSize(900, 650)

        self._init_ui()
        self._apply_style()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()

        self.search_page = SearchPage()
        self.search_page.search_finished.connect(self.on_search_finished)
        self.search_page.search_error.connect(self.on_search_error)

        self.result_page = ResultPage()
        self.result_page.add_to_download.connect(self.on_add_to_download)

        self.download_page = DownloadPage()

        self.tab_widget.addTab(self.search_page, "搜索")
        self.tab_widget.addTab(self.result_page, "搜索结果")
        self.tab_widget.addTab(self.download_page, "下载管理")

        self.tab_widget.setTabEnabled(1, False)

        main_layout.addWidget(self.tab_widget)

    def _apply_style(self):
        self.setStyleSheet(ELEMENTUI_STYLE)

    def on_search_finished(self, results: list):
        if not results:
            QMessageBox.information(self, "提示", "未找到相关结果，请尝试其他关键词")
            return

        self.result_page.set_results(results)
        self.tab_widget.setTabEnabled(1, True)
        self.tab_widget.setCurrentIndex(1)

    def on_search_error(self, error_msg: str):
        QMessageBox.critical(self, "搜索错误", error_msg)

    def on_add_to_download(self, item: dict, resource_types: list):
        self.download_page.add_task(item, resource_types)