from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Signal, Qt

from gui_app.ui.threads import SearchThread


class SearchPage(QWidget):
    search_finished = Signal(list)
    search_error = Signal(str)

    def __init__(self):
        super().__init__()
        self.search_thread = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 60, 40, 40)
        layout.setSpacing(20)

        title_label = QLabel("Bilibili 装扮/收藏集下载器")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: 600; color: #303133;")
        layout.addWidget(title_label)

        subtitle_label = QLabel("搜索你想要下载的装扮或收藏集")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 14px; color: #909399;")
        layout.addWidget(subtitle_label)

        layout.addStretch()

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("请输入装扮或收藏集名称")
        self.search_input.setStyleSheet("font-size: 16px; padding: 12px 16px;")
        self.search_input.returnPressed.connect(self.on_search)
        search_layout.addWidget(self.search_input, 1)

        self.search_btn = QPushButton("搜索")
        self.search_btn.setStyleSheet("font-size: 16px; padding: 12px 30px;")
        self.search_btn.clicked.connect(self.on_search)
        search_layout.addWidget(self.search_btn)

        layout.addLayout(search_layout)

        layout.addStretch()

        tip_label = QLabel("提示：输入关键词后按回车键或点击搜索按钮")
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet("font-size: 12px; color: #c0c4cc;")
        layout.addWidget(tip_label)

    def on_search(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入搜索关键词")
            return

        self.search_btn.setEnabled(False)
        self.search_btn.setText("搜索中...")
        self.search_input.setEnabled(False)

        self.search_thread = SearchThread(keyword)
        self.search_thread.finished.connect(self._on_search_finished)
        self.search_thread.error.connect(self._on_search_error)
        self.search_thread.start()

    def _on_search_finished(self, results: list):
        self.search_btn.setEnabled(True)
        self.search_btn.setText("搜索")
        self.search_input.setEnabled(True)
        self.search_finished.emit(results)

    def _on_search_error(self, error_msg: str):
        self.search_btn.setEnabled(True)
        self.search_btn.setText("搜索")
        self.search_input.setEnabled(True)
        self.search_error.emit(error_msg)