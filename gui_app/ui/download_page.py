import os
from typing import List, Dict

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel,
    QProgressBar, QTextEdit, QFileDialog, QMessageBox,
    QRadioButton, QGroupBox
)
from PySide6.QtCore import Qt, Signal

from gui_app.ui.threads import DownloadThread


class DownloadPage(QWidget):
    def __init__(self):
        super().__init__()
        self.download_queue: List[Dict] = []
        self.download_thread = None
        self.current_task_index = -1
        self.save_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.is_paused = False
        self.download_mode = "all"
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        path_layout = QHBoxLayout()
        path_layout.setSpacing(10)

        self.save_dir_label = QLabel(f"保存目录：{self.save_dir}")
        self.save_dir_label.setStyleSheet("font-size: 13px; color: #606266;")
        path_layout.addWidget(self.save_dir_label, 1)

        self.select_path_btn = QPushButton("选择保存目录")
        self.select_path_btn.clicked.connect(self.on_select_save_dir)
        path_layout.addWidget(self.select_path_btn)

        layout.addLayout(path_layout)

        filter_group = QGroupBox("下载选项")
        filter_layout = QVBoxLayout(filter_group)
        filter_layout.setSpacing(12)

        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(20)

        self.all_mode_radio = QRadioButton("全部下载")
        self.all_mode_radio.setChecked(True)
        self.all_mode_radio.toggled.connect(self.on_download_mode_changed)
        mode_layout.addWidget(self.all_mode_radio)

        self.selected_mode_radio = QRadioButton("当前选择下载")
        self.selected_mode_radio.toggled.connect(self.on_download_mode_changed)
        mode_layout.addWidget(self.selected_mode_radio)

        filter_layout.addLayout(mode_layout)
        layout.addWidget(filter_group)

        queue_group = QWidget()
        queue_group.setStyleSheet("background-color: white; border-radius: 4px; border: 1px solid #ebeef5;")
        queue_layout = QVBoxLayout(queue_group)
        queue_layout.setContentsMargins(0, 0, 0, 0)

        queue_header_layout = QHBoxLayout()
        queue_header = QLabel("下载队列")
        queue_header.setStyleSheet("padding: 10px 15px; font-weight: 500; color: #606266;")
        queue_header_layout.addWidget(queue_header)

        self.clear_btn = QPushButton("清空队列")
        self.clear_btn.setStyleSheet("font-size: 12px; padding: 4px 12px;")
        self.clear_btn.clicked.connect(self.on_clear_queue)
        queue_header_layout.addWidget(self.clear_btn)

        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setStyleSheet("font-size: 12px; padding: 4px 12px;")
        self.select_all_btn.clicked.connect(self.on_select_all)
        queue_header_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("取消全选")
        self.deselect_all_btn.setStyleSheet("font-size: 12px; padding: 4px 12px;")
        self.deselect_all_btn.clicked.connect(self.on_deselect_all)
        queue_header_layout.addWidget(self.deselect_all_btn)

        queue_layout.addLayout(queue_header_layout)

        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet("border: none;")
        self.queue_list.setSelectionMode(QListWidget.ExtendedSelection)
        queue_layout.addWidget(self.queue_list)

        layout.addWidget(queue_group, 1)

        progress_group = QWidget()
        progress_group.setStyleSheet("background-color: white; border-radius: 4px; border: 1px solid #ebeef5;")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(15, 15, 15, 15)
        progress_layout.setSpacing(10)

        progress_header = QLabel("下载进度")
        progress_header.setStyleSheet("font-weight: 500; color: #606266;")
        progress_layout.addWidget(progress_header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% (%v/%m)")
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("等待下载...")
        self.progress_label.setStyleSheet("font-size: 13px; color: #909399;")
        progress_layout.addWidget(self.progress_label)

        layout.addWidget(progress_group)

        log_group = QWidget()
        log_group.setStyleSheet("background-color: white; border-radius: 4px; border: 1px solid #ebeef5;")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(0, 0, 0, 0)

        log_header = QLabel("下载日志")
        log_header.setStyleSheet("padding: 10px 15px; font-weight: 500; color: #606266; border-bottom: 1px solid #f2f6fc;")
        log_layout.addWidget(log_header)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("border: none; font-size: 12px; font-family: Consolas, monospace;")
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_group, 1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.start_btn = QPushButton("开始下载")
        self.start_btn.clicked.connect(self.on_start_download)
        btn_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("暂停下载")
        self.pause_btn.clicked.connect(self.on_pause_download)
        self.pause_btn.setEnabled(False)
        btn_layout.addWidget(self.pause_btn)

        self.cancel_btn = QPushButton("取消下载")
        self.cancel_btn.clicked.connect(self.on_cancel_download)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setProperty("class", "cancel-btn")
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def add_task(self, item: dict, resource_types: list):
        name = item.get("name", "未知")
        part_id = item.get("part_id", 0)
        item_type = "收藏集" if part_id == 0 else "装扮"

        list_item = QListWidgetItem(f"[等待] [{item_type}] {name}")
        task_data = {
            "item": item,
            "resource_types": resource_types
        }
        list_item.setData(Qt.UserRole, task_data)
        list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
        list_item.setCheckState(Qt.Unchecked)
        self.queue_list.addItem(list_item)
        self.download_queue.append(task_data)

    def on_select_save_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择保存目录", self.save_dir)
        if dir_path:
            self.save_dir = dir_path
            self.save_dir_label.setText(f"保存目录：{self.save_dir}")

    def on_download_mode_changed(self):
        if self.all_mode_radio.isChecked():
            self.download_mode = "all"
        else:
            self.download_mode = "selected"

    def on_select_all(self):
        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            if item.text().startswith("[等待]"):
                item.setCheckState(Qt.Checked)

    def on_deselect_all(self):
        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            item.setCheckState(Qt.Unchecked)

    def on_clear_queue(self):
        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.warning(self, "提示", "正在下载中，无法清空队列")
            return
        self.queue_list.clear()
        self.download_queue.clear()
        self.current_task_index = -1

    def on_start_download(self):
        if self.download_thread and self.download_thread.isRunning():
            if self.is_paused:
                self.is_paused = False
                self.download_thread.resume()
                self.pause_btn.setText("暂停下载")
                self.log_text.append("继续下载...")
                return
            return

        download_indices = []
        if self.download_mode == "all":
            for i in range(len(self.download_queue)):
                item = self.queue_list.item(i)
                if item.text().startswith("[等待]"):
                    download_indices.append(i)
        else:
            for i in range(len(self.download_queue)):
                item = self.queue_list.item(i)
                if item.checkState() == Qt.Checked and item.text().startswith("[等待]"):
                    download_indices.append(i)

        if not download_indices:
            QMessageBox.warning(self, "提示", "没有可下载的任务")
            return

        self.download_indices = download_indices
        self.current_task_index = 0
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.select_path_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.all_mode_radio.setEnabled(False)
        self.selected_mode_radio.setEnabled(False)

        self._start_next_task()

    def _start_next_task(self):
        if self.current_task_index >= len(self.download_indices):
            self.log_text.append("所有任务下载完成！")
            self._reset_ui()
            return

        queue_index = self.download_indices[self.current_task_index]
        current_task = self.download_queue[queue_index]
        current_item = current_task["item"]
        resource_types = current_task["resource_types"]
        name = current_item.get("name", "未知")
        part_id = current_item.get("part_id", 0)
        item_type = "收藏集" if part_id == 0 else "装扮"

        self.progress_bar.setValue(0)
        self.progress_label.setText(f"正在下载：[{item_type}] {name}")

        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            if i == queue_index:
                item.setText(f"[下载中] [{item_type}] {name}")
            elif i in self.download_indices[self.current_task_index + 1:]:
                task_data = item.data(Qt.UserRole)
                item_name = task_data["item"].get("name", "未知")
                item_part_id = task_data["item"].get("part_id", 0)
                it_type = "收藏集" if item_part_id == 0 else "装扮"
                item.setText(f"[等待] [{it_type}] {item_name}")

        self.download_thread = DownloadThread(current_item, self.save_dir, resource_types)
        self.download_thread.progress.connect(self.on_download_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.error.connect(self.on_download_error)
        self.download_thread.log.connect(self.on_download_log)
        self.download_thread.finished.connect(self._on_task_finished)
        self.download_thread.error.connect(self._on_task_finished)
        self.download_thread.start()

    def _on_task_finished(self):
        self.current_task_index += 1
        self._start_next_task()

    def on_pause_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.download_thread.pause()
                self.pause_btn.setText("继续下载")
                self.progress_label.setText("下载已暂停")
                self.log_text.append("下载已暂停")
            else:
                self.download_thread.resume()
                self.pause_btn.setText("暂停下载")
                self.log_text.append("继续下载")

    def on_cancel_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.progress_label.setText("取消中...")

    def on_download_progress(self, percent: int, file_name: str):
        self.progress_bar.setValue(percent)
        self.progress_label.setText(f"正在下载：{file_name}")

    def on_download_log(self, log_msg: str):
        self.log_text.append(log_msg)

    def on_download_finished(self, count: int):
        queue_index = self.download_indices[self.current_task_index]
        current_task = self.download_queue[queue_index]
        current_item = current_task["item"]
        name = current_item.get("name", "未知")
        part_id = current_item.get("part_id", 0)
        item_type = "收藏集" if part_id == 0 else "装扮"

        self.queue_list.item(queue_index).setText(f"[已完成] [{item_type}] {name}")
        self.log_text.append(f"✓ [{item_type}] {name} 下载完成，共 {count} 个文件")

    def on_download_error(self, error_msg: str):
        queue_index = self.download_indices[self.current_task_index]
        current_task = self.download_queue[queue_index]
        current_item = current_task["item"]
        name = current_item.get("name", "未知")
        part_id = current_item.get("part_id", 0)
        item_type = "收藏集" if part_id == 0 else "装扮"

        self.queue_list.item(queue_index).setText(f"[失败] [{item_type}] {name}")
        self.log_text.append(f"✗ [{item_type}] {name} 下载失败：{error_msg}")

    def _reset_ui(self):
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.select_path_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.all_mode_radio.setEnabled(True)
        self.selected_mode_radio.setEnabled(True)

        self.progress_bar.setValue(0)
        self.progress_label.setText("等待下载...")
        self.is_paused = False
        self.pause_btn.setText("暂停下载")