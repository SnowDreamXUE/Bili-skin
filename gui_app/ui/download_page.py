import os
from typing import List, Dict

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit,
    QFileDialog, QMessageBox, QScrollArea, QGroupBox,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor

from gui_app.ui.threads import DownloadThread


class DownloadItemWidget(QWidget):
    download_clicked = Signal(int)
    pause_clicked = Signal(int)
    terminate_clicked = Signal(int)
    delete_clicked = Signal(int)

    STATUS_WAITING = "waiting"
    STATUS_DOWNLOADING = "downloading"
    STATUS_PAUSED = "paused"
    STATUS_TERMINATED = "terminated"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    def __init__(self, task_id: int, name: str, item_type: str):
        super().__init__()
        self.task_id = task_id
        self.name = name
        self.item_type = item_type
        self.status = self.STATUS_WAITING
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(4)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(6)

        self.name_label = QLabel(f"[{self.item_type}] {self.name}")
        self.name_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #303133;")
        self.name_label.setWordWrap(True)
        top_layout.addWidget(self.name_label, 1)

        self.download_btn = QPushButton("下载")
        self.download_btn.setFixedWidth(60)
        self.download_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 4px;
                background-color: #409EFF;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #66B1FF;
            }
            QPushButton:pressed {
                background-color: #3A8EE6;
            }
            QPushButton:disabled {
                background-color: #C0C4CC;
            }
        """)
        self.download_btn.clicked.connect(self._on_download_clicked)
        top_layout.addWidget(self.download_btn)

        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setFixedWidth(60)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 4px;
                background-color: #E6A23C;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #E8B86D;
            }
            QPushButton:pressed {
                background-color: #D49232;
            }
            QPushButton:disabled {
                background-color: #C0C4CC;
            }
        """)
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        self.pause_btn.setEnabled(False)
        top_layout.addWidget(self.pause_btn)

        self.delete_btn = QPushButton("取消")
        self.delete_btn.setFixedWidth(60)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 4px;
                background-color: #F56C6C;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #F78989;
            }
            QPushButton:pressed {
                background-color: #E85A5A;
            }
            QPushButton:disabled {
                background-color: #C0C4CC;
            }
        """)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        top_layout.addWidget(self.delete_btn)

        layout.addLayout(top_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                height: 6px;
                border-radius: 3px;
                background-color: #E4E7ED;
                text-align: center;
                font-size: 10px;
                color: #606266;
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background-color: #409EFF;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.setStyleSheet("""
            background-color: white;
            border-radius: 6px;
            border: 1px solid #EBEEF5;
            max-height: 80px;
        """)

    def _on_download_clicked(self):
        if self.status == self.STATUS_WAITING:
            self.download_clicked.emit(self.task_id)
        elif self.status == self.STATUS_PAUSED:
            self.pause_clicked.emit(self.task_id)

    def _on_pause_clicked(self):
        if self.status == self.STATUS_DOWNLOADING:
            self.pause_clicked.emit(self.task_id)
        elif self.status == self.STATUS_PAUSED:
            self.download_clicked.emit(self.task_id)

    def _on_delete_clicked(self):
        if self.status == self.STATUS_WAITING:
            self.delete_clicked.emit(self.task_id)
        elif self.status == self.STATUS_DOWNLOADING or self.status == self.STATUS_PAUSED:
            self.terminate_clicked.emit(self.task_id)
        elif self.status == self.STATUS_TERMINATED or self.status == self.STATUS_COMPLETED or self.status == self.STATUS_FAILED:
            self.delete_clicked.emit(self.task_id)

    def set_status(self, status: str):
        self.status = status

        if status == self.STATUS_DOWNLOADING:
            self.download_btn.setText("下载")
            self.download_btn.setEnabled(False)
            self.pause_btn.setText("暂停")
            self.pause_btn.setEnabled(True)
            self.delete_btn.setText("终止")
            self.delete_btn.setEnabled(True)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    height: 6px;
                    border-radius: 3px;
                    background-color: #E4E7ED;
                    text-align: center;
                    font-size: 10px;
                    color: #606266;
                }
                QProgressBar::chunk {
                    border-radius: 3px;
                    background-color: #409EFF;
                }
            """)
        elif status == self.STATUS_PAUSED:
            self.download_btn.setText("继续")
            self.download_btn.setEnabled(True)
            self.pause_btn.setText("暂停")
            self.pause_btn.setEnabled(False)
            self.delete_btn.setText("终止")
            self.delete_btn.setEnabled(True)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    height: 6px;
                    border-radius: 3px;
                    background-color: #E4E7ED;
                    text-align: center;
                    font-size: 10px;
                    color: #606266;
                }
                QProgressBar::chunk {
                    border-radius: 3px;
                    background-color: #E6A23C;
                }
            """)
        elif status == self.STATUS_TERMINATED:
            self.download_btn.setText("下载")
            self.download_btn.setEnabled(True)
            self.pause_btn.setText("暂停")
            self.pause_btn.setEnabled(False)
            self.delete_btn.setText("删除")
            self.delete_btn.setEnabled(True)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    height: 6px;
                    border-radius: 3px;
                    background-color: #E4E7ED;
                    text-align: center;
                    font-size: 10px;
                    color: #606266;
                }
                QProgressBar::chunk {
                    border-radius: 3px;
                    background-color: #909399;
                }
            """)
        elif status == self.STATUS_COMPLETED:
            self.download_btn.setText("下载")
            self.download_btn.setEnabled(True)
            self.pause_btn.setText("暂停")
            self.pause_btn.setEnabled(False)
            self.delete_btn.setText("删除")
            self.delete_btn.setEnabled(True)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    height: 6px;
                    border-radius: 3px;
                    background-color: #E4E7ED;
                    text-align: center;
                    font-size: 10px;
                    color: #606266;
                }
                QProgressBar::chunk {
                    border-radius: 3px;
                    background-color: #67C23A;
                }
            """)
        elif status == self.STATUS_FAILED:
            self.download_btn.setText("下载")
            self.download_btn.setEnabled(True)
            self.pause_btn.setText("暂停")
            self.pause_btn.setEnabled(False)
            self.delete_btn.setText("删除")
            self.delete_btn.setEnabled(True)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    height: 6px;
                    border-radius: 3px;
                    background-color: #E4E7ED;
                    text-align: center;
                    font-size: 10px;
                    color: #606266;
                }
                QProgressBar::chunk {
                    border-radius: 3px;
                    background-color: #F56C6C;
                }
            """)
        else:
            self.download_btn.setText("下载")
            self.download_btn.setEnabled(True)
            self.pause_btn.setText("暂停")
            self.pause_btn.setEnabled(False)
            self.delete_btn.setText("取消")
            self.delete_btn.setEnabled(True)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    height: 6px;
                    border-radius: 3px;
                    background-color: #E4E7ED;
                    text-align: center;
                    font-size: 10px;
                    color: #606266;
                }
                QProgressBar::chunk {
                    border-radius: 3px;
                    background-color: #409EFF;
                }
            """)

    def set_progress(self, percent: int):
        self.progress_bar.setValue(percent)


class DownloadPage(QWidget):
    def __init__(self):
        super().__init__()
        self.download_queue: List[Dict] = []
        self.download_thread = None
        self.current_task_id = -1
        self.save_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.task_widgets: Dict[int, DownloadItemWidget] = {}
        self.next_task_id = 0
        self.all_download_mode = False
        self.all_download_queue = []
        self.all_download_index = -1
        self.is_paused = False
        self.is_terminated = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(10)

        self.all_download_btn = QPushButton("全部下载")
        self.all_download_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 6px 20px;
                border-radius: 4px;
                background-color: #409EFF;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #66B1FF;
            }
            QPushButton:pressed {
                background-color: #3A8EE6;
            }
            QPushButton:disabled {
                background-color: #C0C4CC;
            }
        """)
        self.all_download_btn.clicked.connect(self.on_all_download)
        toolbar_layout.addWidget(self.all_download_btn)

        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 6px 20px;
                border-radius: 4px;
                background-color: #F56C6C;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #F78989;
            }
            QPushButton:pressed {
                background-color: #E85A5A;
            }
            QPushButton:disabled {
                background-color: #C0C4CC;
            }
        """)
        self.clear_btn.clicked.connect(self.on_clear_queue)
        toolbar_layout.addWidget(self.clear_btn)

        toolbar_layout.addStretch()

        self.path_label = QLabel(f"下载路径：{self.save_dir}")
        self.path_label.setStyleSheet("font-size: 13px; color: #409EFF;")
        self.path_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.path_label.setToolTip("点击选择下载路径")
        self.path_label.mousePressEvent = self.on_select_save_dir
        toolbar_layout.addWidget(self.path_label)

        layout.addWidget(toolbar_widget, 1)

        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(8, 8, 8, 8)
        list_widget.setStyleSheet("""
            background-color: white;
            border-radius: 6px;
            border: 1px solid #EBEEF5;
        """)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                width: 6px;
                background-color: transparent;
                margin: 0px;
                padding: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #D9D9D9;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #C0C4CC;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
        """)

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(6)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        self.empty_hint_label = QLabel("暂无下载任务，请前往「搜索结果」页面添加")
        self.empty_hint_label.setStyleSheet("""
            QLabel {
                color: #909399;
                font-size: 13px;
                padding: 20px;
            }
        """)
        self.empty_hint_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.empty_hint_label)

        scroll_area.setWidget(self.scroll_content)
        list_layout.addWidget(scroll_area)

        layout.addWidget(list_widget, 5)

        log_group = QGroupBox("下载日志")
        log_group.setStyleSheet("""
            QGroupBox {
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                font-size: 14px;
                font-weight: 500;
                color: #606266;
                border: 1px solid #EBEEF5;
                border-radius: 6px;
                margin-top: 0px;
                padding-top: 30px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: padding;
                subcontrol-position: top left;
                left: 10px;
                top: 6px;
                padding-left: 6px;
                padding-right: 6px;
                padding-top: 0px;
                padding-bottom: 0px;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                font-size: 14px;
                font-weight: 500;
                color: #606266;
                background-color: transparent;
            }
        """)
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(10, 10, 10, 10)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: none;
                font-size: 12px;
                font-family: Consolas, monospace;
                color: #606266;
                background-color: white;
            }
            QScrollBar:vertical {
                width: 6px;
                background-color: transparent;
                margin: 0px;
                padding: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #D9D9D9;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #C0C4CC;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
        """)
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_group, 4)

    def add_task(self, item: dict, resource_types: list):
        task_id = self.next_task_id
        self.next_task_id += 1

        name = item.get("name", "未知")
        part_id = item.get("part_id", 0)
        item_type = "收藏集" if part_id == 0 else "装扮"

        task_data = {
            "task_id": task_id,
            "item": item,
            "resource_types": resource_types
        }
        self.download_queue.append(task_data)

        if self.empty_hint_label.isVisible():
            self.empty_hint_label.hide()

        widget = DownloadItemWidget(task_id, name, item_type)
        widget.download_clicked.connect(self.on_single_download)
        widget.pause_clicked.connect(self.on_pause_download)
        widget.terminate_clicked.connect(self.on_terminate_download)
        widget.delete_clicked.connect(self.on_delete_task)
        self.task_widgets[task_id] = widget

        self.scroll_layout.addWidget(widget)

    def on_select_save_dir(self, event=None):
        dir_path = QFileDialog.getExistingDirectory(self, "选择保存目录", self.save_dir)
        if dir_path:
            self.save_dir = dir_path
            self.path_label.setText(f"下载路径：{self.save_dir}")

    def on_clear_queue(self):
        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.warning(self, "提示", "正在下载中，无法清空队列")
            return

        for widget in self.task_widgets.values():
            widget.setParent(None)
        self.task_widgets.clear()
        self.download_queue.clear()
        self.next_task_id = 0
        self.current_task_id = -1
        self.all_download_mode = False
        self.all_download_queue = []
        self.all_download_index = -1

        self.empty_hint_label.show()

    def on_delete_task(self, task_id: int):
        if self.download_thread and self.download_thread.isRunning() and self.current_task_id == task_id:
            QMessageBox.warning(self, "提示", "该任务正在下载中，请先终止")
            return

        widget = self.task_widgets.get(task_id)
        if widget:
            widget.setParent(None)
            del self.task_widgets[task_id]

        self.download_queue = [t for t in self.download_queue if t["task_id"] != task_id]

        if self.all_download_mode and task_id in self.all_download_queue:
            self.all_download_queue.remove(task_id)

        if len(self.task_widgets) == 0:
            self.empty_hint_label.show()

    def on_terminate_download(self, task_id: int):
        if self.download_thread and self.download_thread.isRunning() and self.current_task_id == task_id:
            self.is_terminated = True
            self.download_thread.stop()
            self.log_text.append("下载已终止")

    def on_single_download(self, task_id: int):
        if self.all_download_mode:
            QMessageBox.warning(self, "提示", "全部下载模式下，请使用全部下载控制")
            return

        if self.download_thread and self.download_thread.isRunning() and self.current_task_id == task_id:
            if self.is_paused:
                self.is_paused = False
                self.download_thread.resume()
                self._update_widget_status(task_id, DownloadItemWidget.STATUS_DOWNLOADING)
                self.log_text.append("继续下载")
                return

        self._start_download(task_id, False)

    def on_pause_download(self, task_id: int):
        if self.download_thread and self.download_thread.isRunning() and self.current_task_id == task_id:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.download_thread.pause()
                self._update_widget_status(task_id, DownloadItemWidget.STATUS_PAUSED)
                self.log_text.append("下载已暂停")
            else:
                self.download_thread.resume()
                self._update_widget_status(task_id, DownloadItemWidget.STATUS_DOWNLOADING)
                self.log_text.append("继续下载")

    def on_all_download(self):
        if self.download_thread and self.download_thread.isRunning():
            if self.is_paused:
                self.is_paused = False
                self.download_thread.resume()
                self._update_widget_status(self.current_task_id, DownloadItemWidget.STATUS_DOWNLOADING)
                self.log_text.append("继续下载...")
                return
            return

        waiting_tasks = [t for t in self.download_queue if self.task_widgets[t["task_id"]].status == DownloadItemWidget.STATUS_WAITING]
        if not waiting_tasks:
            QMessageBox.warning(self, "提示", "没有等待下载的任务")
            return

        self.all_download_mode = True
        self.all_download_queue = [t["task_id"] for t in waiting_tasks]
        self.all_download_index = 0

        self.all_download_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)

        self._start_next_all_download()

    def _start_next_all_download(self):
        if self.all_download_index >= len(self.all_download_queue):
            self.log_text.append("所有任务下载完成！")
            self.all_download_mode = False
            self.all_download_queue = []
            self.all_download_index = -1
            self.all_download_btn.setEnabled(True)
            self.clear_btn.setEnabled(True)
            return

        task_id = self.all_download_queue[self.all_download_index]
        self._start_download(task_id, True)

    def _start_download(self, task_id: int, is_all_download: bool):
        task_data = next((t for t in self.download_queue if t["task_id"] == task_id), None)
        if not task_data:
            return

        if self.download_thread and self.download_thread.isRunning():
            return

        self.current_task_id = task_id
        self.is_paused = False
        self.is_terminated = False

        widget = self.task_widgets.get(task_id)
        if widget:
            widget.set_status(DownloadItemWidget.STATUS_DOWNLOADING)
            widget.set_progress(0)

        current_item = task_data["item"]
        resource_types = task_data["resource_types"]
        name = current_item.get("name", "未知")
        part_id = current_item.get("part_id", 0)
        item_type = "收藏集" if part_id == 0 else "装扮"

        self.log_text.append(f"开始下载：[{item_type}] {name}")

        self.download_thread = DownloadThread(current_item, self.save_dir, resource_types)
        self.download_thread.progress.connect(lambda p, f, tid=task_id: self.on_download_progress(tid, p, f))
        self.download_thread.finished.connect(lambda c, tid=task_id, all_dl=is_all_download: self.on_download_finished(tid, c, all_dl))
        self.download_thread.error.connect(lambda e, tid=task_id, all_dl=is_all_download: self.on_download_error(tid, e, all_dl))
        self.download_thread.log.connect(self.on_download_log)
        self.download_thread.start()

    def _update_widget_status(self, task_id: int, status: str):
        widget = self.task_widgets.get(task_id)
        if widget:
            widget.set_status(status)

    def on_download_progress(self, task_id: int, percent: int, file_name: str):
        widget = self.task_widgets.get(task_id)
        if widget:
            widget.set_progress(percent)

    def on_download_log(self, log_msg: str):
        self.log_text.append(log_msg)

    def on_download_finished(self, task_id: int, count: int, is_all_download: bool):
        if self.is_terminated:
            self._update_widget_status(task_id, DownloadItemWidget.STATUS_TERMINATED)
            self.log_text.append("下载已终止")
        else:
            widget = self.task_widgets.get(task_id)
            if widget:
                widget.set_status(DownloadItemWidget.STATUS_COMPLETED)
                widget.set_progress(100)

            task_data = next((t for t in self.download_queue if t["task_id"] == task_id), None)
            if task_data:
                item = task_data["item"]
                name = item.get("name", "未知")
                part_id = item.get("part_id", 0)
                item_type = "收藏集" if part_id == 0 else "装扮"
                self.log_text.append(f"✓ [{item_type}] {name} 下载完成，共 {count} 个文件")

        if is_all_download:
            self.all_download_index += 1
            self._start_next_all_download()
        else:
            self.current_task_id = -1

    def on_download_error(self, task_id: int, error_msg: str, is_all_download: bool):
        if self.is_terminated:
            self._update_widget_status(task_id, DownloadItemWidget.STATUS_TERMINATED)
        else:
            widget = self.task_widgets.get(task_id)
            if widget:
                widget.set_status(DownloadItemWidget.STATUS_FAILED)

            task_data = next((t for t in self.download_queue if t["task_id"] == task_id), None)
            if task_data and not self.is_terminated:
                item = task_data["item"]
                name = item.get("name", "未知")
                part_id = item.get("part_id", 0)
                item_type = "收藏集" if part_id == 0 else "装扮"
                self.log_text.append(f"✗ [{item_type}] {name} 下载失败：{error_msg}")

        if is_all_download:
            self.all_download_index += 1
            self._start_next_all_download()
        else:
            self.current_task_id = -1