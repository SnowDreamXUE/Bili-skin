import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem,
    QTextEdit, QProgressBar, QGroupBox, QSplitter, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt

from gui_app.config.style import ELEMENTUI_STYLE
from gui_app.ui.threads import SearchThread, DownloadThread


class BiliGarbGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bilibili 装扮/收藏集下载器")
        self.setMinimumSize(900, 650)

        self.search_results = []
        self.download_thread = None
        self.save_dir = os.path.dirname(os.path.abspath(__file__))

        self._init_ui()
        self._apply_style()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("请输入装扮或收藏集名称")
        self.search_input.returnPressed.connect(self.on_search)
        header_layout.addWidget(self.search_input, 1)

        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.on_search)
        header_layout.addWidget(self.search_btn)

        self.save_dir_btn = QPushButton("选择保存目录")
        self.save_dir_btn.clicked.connect(self.on_select_save_dir)
        header_layout.addWidget(self.save_dir_btn)

        main_layout.addLayout(header_layout)

        save_dir_label = QLabel(f"当前保存目录：{self.save_dir}")
        save_dir_label.setStyleSheet("color: #909399; font-size: 12px;")
        main_layout.addWidget(save_dir_label)
        self.save_dir_label = save_dir_label

        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)

        result_group = QGroupBox("搜索结果")
        result_layout = QVBoxLayout(result_group)

        self.result_list = QListWidget()
        self.result_list.itemClicked.connect(self.on_select_item)
        result_layout.addWidget(self.result_list)

        splitter.addWidget(result_group)
        splitter.setStretchFactor(0, 2)

        detail_group = QGroupBox("下载信息")
        detail_layout = QVBoxLayout(detail_group)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setPlaceholderText("搜索结果将显示在这里...")
        detail_layout.addWidget(self.detail_text)

        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% (%v/%m)")
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("等待下载...")
        self.progress_label.setStyleSheet("color: #909399;")
        progress_layout.addWidget(self.progress_label)

        detail_layout.addLayout(progress_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.download_btn = QPushButton("开始下载")
        self.download_btn.clicked.connect(self.on_download)
        self.download_btn.setEnabled(False)
        btn_layout.addWidget(self.download_btn)

        self.cancel_btn = QPushButton("取消下载")
        self.cancel_btn.clicked.connect(self.on_cancel_download)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setProperty("class", "cancel-btn")
        btn_layout.addWidget(self.cancel_btn)

        detail_layout.addLayout(btn_layout)

        splitter.addWidget(detail_group)
        splitter.setStretchFactor(1, 1)

    def _apply_style(self):
        self.setStyleSheet(ELEMENTUI_STYLE)

    def on_search(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入搜索关键词")
            return

        self.search_btn.setEnabled(False)
        self.search_btn.setText("搜索中...")
        self.result_list.clear()
        self.detail_text.clear()
        self.download_btn.setEnabled(False)

        self.search_thread = SearchThread(keyword)
        self.search_thread.finished.connect(self.on_search_finished)
        self.search_thread.error.connect(self.on_search_error)
        self.search_thread.start()

    def on_search_finished(self, results: list):
        self.search_results = results
        self.search_btn.setEnabled(True)
        self.search_btn.setText("搜索")

        if not results:
            QMessageBox.information(self, "提示", "未找到相关结果，请尝试其他关键词")
            return

        self.result_list.clear()
        for item in results:
            name = item.get("name", "未知")
            part_id = item.get("part_id", 0)
            item_type = "收藏集" if part_id == 0 else "装扮"
            properties = item.get("properties", {})
            cover = properties.get("image_cover", "")

            list_item = QListWidgetItem(f"[{item_type}] {name}")
            list_item.setData(Qt.UserRole, item)
            self.result_list.addItem(list_item)

    def on_search_error(self, error_msg: str):
        self.search_btn.setEnabled(True)
        self.search_btn.setText("搜索")
        QMessageBox.critical(self, "搜索错误", error_msg)

    def on_select_item(self, item: QListWidgetItem):
        data = item.data(Qt.UserRole)
        if not data:
            return

        name = data.get("name", "未知")
        part_id = data.get("part_id", 0)
        item_type = "收藏集" if part_id == 0 else "装扮"
        properties = data.get("properties", {})
        cover = properties.get("image_cover", "")
        item_id = data.get("item_id", "")

        info_text = f"名称：{name}\n"
        info_text += f"类型：{item_type}\n"
        if item_type == "收藏集":
            info_text += f"act_id：{properties.get('dlc_act_id', '未知')}\n"
            info_text += f"lottery_id：{properties.get('dlc_lottery_id', '未知')}\n"
        else:
            info_text += f"item_id：{item_id}\n"
        info_text += f"封面：{cover[:80]}{'...' if len(cover) > 80 else ''}"

        self.detail_text.setText(info_text)
        self.download_btn.setEnabled(True)
        self.selected_item = data

    def on_select_save_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择保存目录", self.save_dir)
        if dir_path:
            self.save_dir = dir_path
            self.save_dir_label.setText(f"当前保存目录：{self.save_dir}")

    def on_download(self):
        if not hasattr(self, 'selected_item') or not self.selected_item:
            QMessageBox.warning(self, "提示", "请先选择一个项目")
            return

        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.search_btn.setEnabled(False)
        self.search_input.setEnabled(False)
        self.result_list.setEnabled(False)

        self.progress_bar.setValue(0)
        self.progress_label.setText("准备下载...")

        self.download_thread = DownloadThread(self.selected_item, self.save_dir)
        self.download_thread.progress.connect(self.on_download_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.error.connect(self.on_download_error)
        self.download_thread.log.connect(self.on_download_log)
        self.download_thread.start()

    def on_download_progress(self, percent: int, file_name: str):
        self.progress_bar.setValue(percent)
        self.progress_label.setText(f"正在下载：{file_name}")

    def on_download_log(self, log_msg: str):
        self.detail_text.append(log_msg)

    def on_download_finished(self, count: int):
        self.progress_bar.setValue(100)
        self.progress_label.setText("下载完成")
        QMessageBox.information(self, "下载完成", f"共下载 {count} 个文件")
        self._reset_download_ui()

    def on_download_error(self, error_msg: str):
        QMessageBox.critical(self, "下载错误", error_msg)
        self._reset_download_ui()

    def on_cancel_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.progress_label.setText("取消中...")

    def _reset_download_ui(self):
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.search_btn.setEnabled(True)
        self.search_input.setEnabled(True)
        self.result_list.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("等待下载...")