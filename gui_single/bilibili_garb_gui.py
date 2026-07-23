#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili 装扮/收藏集素材下载工具 - GUI 版本
ElementUI 风格界面，支持搜索、选择和下载装扮及收藏集素材
"""

import os
import sys
import re
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem,
    QTextEdit, QProgressBar, QGroupBox, QScrollArea, QFrame,
    QSplitter, QMessageBox, QFileDialog, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize
from PySide6.QtGui import QPixmap, QColor, QFont, QIcon

import requests

SEARCH_API = "https://api.bilibili.com/x/garb/v2/mall/home/search"
SUIT_DETAIL_API = "https://api.bilibili.com/x/garb/v2/mall/suit/detail"
DLC_DETAIL_API = "https://api.bilibili.com/x/vas/dlc_act/lottery_home_detail"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
}

ELEMENTUI_STYLE = """
QMainWindow {
    background-color: #f5f7fa;
}

QWidget {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 14px;
    color: #606266;
}

QLineEdit {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 6px 12px;
    background-color: white;
    color: #606266;
}

QLineEdit:hover {
    border-color: #c0c4cc;
}

QLineEdit:focus {
    border-color: #409eff;
    outline: none;
}

QPushButton {
    background-color: #409eff;
    border: none;
    border-radius: 4px;
    padding: 6px 20px;
    color: white;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #66b1ff;
}

QPushButton:pressed {
    background-color: #3a8ee6;
}

QPushButton:disabled {
    background-color: #a0cfff;
    color: #fff;
}

QPushButton.cancel-btn {
    background-color: #fff;
    border: 1px solid #dcdfe6;
    color: #606266;
}

QPushButton.cancel-btn:hover {
    background-color: #f5f7fa;
}

QGroupBox {
    border: 1px solid #ebeef5;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 15px;
    background-color: white;
}

QGroupBox::title {
    color: #303133;
    font-weight: 600;
    padding-left: 8px;
    padding-right: 8px;
    top: -10px;
    background-color: white;
}

QListWidget {
    border: 1px solid #ebeef5;
    border-radius: 4px;
    background-color: white;
    outline: none;
}

QListWidget::item {
    padding: 12px;
    border-bottom: 1px solid #f2f6fc;
}

QListWidget::item:hover {
    background-color: #ecf5ff;
}

QListWidget::item:selected {
    background-color: #e6f7ff;
    color: #409eff;
}

QTextEdit {
    border: 1px solid #ebeef5;
    border-radius: 4px;
    background-color: #fafafa;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 13px;
}

QProgressBar {
    border: none;
    border-radius: 4px;
    height: 8px;
    background-color: #ebeef5;
}

QProgressBar::chunk {
    background-color: #409eff;
    border-radius: 4px;
}

QLabel.title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
}

QLabel.info {
    color: #909399;
    font-size: 12px;
}

QLabel.success {
    color: #67c23a;
}

QLabel.warning {
    color: #e6a23c;
}

QLabel.error {
    color: #f56c6c;
}

QSplitter::handle {
    background-color: #ebeef5;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QFrame.card {
    background-color: white;
    border-radius: 4px;
    border: 1px solid #ebeef5;
    padding: 15px;
    margin-bottom: 10px;
}

QFrame.card:hover {
    border-color: #dcdfe6;
}

QRadioButton {
    color: #606266;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
}

QRadioButton::indicator::unchecked {
    border: 2px solid #dcdfe6;
    border-radius: 8px;
    background-color: white;
}

QRadioButton::indicator::checked {
    border: 2px solid #409eff;
    border-radius: 8px;
    background-color: #409eff;
}

QRadioButton::indicator::checked::after {
    content: "";
    width: 6px;
    height: 6px;
    background-color: white;
    border-radius: 3px;
    position: absolute;
    top: 3px;
    left: 3px;
}
"""


class SearchThread(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, keyword: str):
        super().__init__()
        self.keyword = keyword

    def run(self):
        try:
            params = {"key_word": self.keyword, "ps": 20, "pn": 1}
            resp = requests.get(SEARCH_API, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == 0 and data.get("data", {}).get("list"):
                self.finished.emit(data["data"]["list"])
            else:
                self.finished.emit([])
        except Exception as e:
            self.error.emit(f"搜索失败：{str(e)}")


class DownloadThread(QThread):
    progress = Signal(int, str)
    finished = Signal(int)
    error = Signal(str)
    log = Signal(str)

    def __init__(self, item: dict, save_dir: str):
        super().__init__()
        self.item = item
        self.save_dir = save_dir
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            name = self.item.get("name", "未知")
            part_id = self.item.get("part_id", 0)
            properties = self.item.get("properties", {})

            if part_id == 0:
                act_id = properties.get("dlc_act_id")
                lottery_id = properties.get("dlc_lottery_id")
                if not act_id or not lottery_id:
                    self.error.emit("无法获取收藏集的 act_id 或 lottery_id")
                    return
                self._download_collectible(name, int(act_id), int(lottery_id), self.save_dir)
            else:
                item_id = self.item.get("item_id")
                if not item_id:
                    self.error.emit("无法获取装扮的 item_id")
                    return
                self._download_suit(name, int(item_id), self.save_dir)
        except Exception as e:
            self.error.emit(f"下载失败：{str(e)}")

    def _download_file(self, url: str, save_path: str) -> bool:
        if not self._is_running:
            return False
        try:
            resp = requests.get(url, headers=HEADERS, timeout=60, stream=True)
            resp.raise_for_status()
            total_size = int(resp.headers.get("content-length", 0))
            downloaded = 0
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if not self._is_running:
                        return False
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = int((downloaded / total_size) * 100)
                        self.progress.emit(percent, os.path.basename(save_path))
            return True
        except Exception as e:
            self.log.emit(f"下载失败 {url}: {e}")
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except:
                    pass
            return False

    def _sanitize_filename(self, name: str) -> str:
        illegal_chars = r'[<>:"/\\|？*]'
        name = re.sub(illegal_chars, "_", name)
        name = name.strip().strip(".")
        if len(name) > 200:
            name = name[:200]
        return name

    def _download_collectible(self, name: str, act_id: int, lottery_id: int, base_dir: str):
        self.log.emit(f"正在获取收藏集详情：{name}")

        try:
            params = {"act_id": act_id, "lottery_id": lottery_id}
            resp = requests.get(DLC_DETAIL_API, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            detail = resp.json()
            if detail.get("code") != 0:
                self.error.emit("无法获取收藏集详情")
                return
            detail = detail.get("data")
        except Exception as e:
            self.error.emit(f"获取收藏集详情失败：{e}")
            return

        if not detail:
            self.error.emit("无法获取收藏集详情")
            return

        collect_dir = os.path.join(base_dir, "收藏集", self._sanitize_filename(name))
        os.makedirs(collect_dir, exist_ok=True)

        item_list = detail.get("item_list", [])
        if not item_list:
            self.log.emit("该收藏集没有可下载的卡片")
            self.finished.emit(0)
            return

        downloaded_count = 0
        total_items = len(item_list)

        for i, item in enumerate(item_list):
            if not self._is_running:
                break
            card_info = item.get("card_info", {})
            if not card_info:
                continue

            card_name = card_info.get("card_name", "未知卡片")
            card_name = self._sanitize_filename(card_name)

            card_img = card_info.get("card_img")
            if card_img:
                img_ext = os.path.splitext(card_img.split("?")[0])[1] or ".png"
                img_path = os.path.join(collect_dir, f"{card_name}{img_ext}")
                if self._download_file(card_img, img_path):
                    self.log.emit(f"✓ 卡片图片：{card_name}")
                    downloaded_count += 1

            video_list = card_info.get("video_list", [])
            if video_list:
                video_url = video_list[0]
                video_ext = os.path.splitext(video_url.split("?")[0])[1] or ".mp4"
                video_path = os.path.join(collect_dir, f"{card_name}{video_ext}")
                if self._download_file(video_url, video_path):
                    self.log.emit(f"✓ 卡片视频：{card_name}")
                    downloaded_count += 1

            overall_percent = int(((i + 1) / total_items) * 100)
            self.progress.emit(overall_percent, f"正在处理 {card_name}...")

        self.log.emit(f"\n收藏集下载完成，共下载 {downloaded_count} 个文件")
        self.finished.emit(downloaded_count)

    def _download_suit(self, name: str, item_id: int, base_dir: str):
        self.log.emit(f"正在获取装扮详情：{name}")

        try:
            params = {"item_id": item_id}
            resp = requests.get(SUIT_DETAIL_API, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            detail = resp.json()
            if detail.get("code") != 0:
                self.error.emit("无法获取装扮详情")
                return
            detail = detail.get("data")
        except Exception as e:
            self.error.emit(f"获取装扮详情失败：{e}")
            return

        if not detail:
            self.error.emit("无法获取装扮详情")
            return

        suit_items = detail.get("suit_items", {})
        if not suit_items:
            self.log.emit("该装扮没有可下载的素材")
            self.finished.emit(0)
            return

        suit_dir = os.path.join(base_dir, "装扮", self._sanitize_filename(name))
        os.makedirs(suit_dir, exist_ok=True)

        downloaded_count = 0
        total_files = 0

        emoji_package = suit_items.get("emoji_package", [])
        space_bg = suit_items.get("space_bg", [])

        for emoji_item in emoji_package:
            items = emoji_item.get("items", [])
            total_files += len(items)

        for bg_item in space_bg:
            props = bg_item.get("properties", {})
            image_pairs = {}
            for key, value in props.items():
                if not value:
                    continue
                match = re.match(r'image(\d+)_(landscape|portrait)', key)
                if match:
                    num = match.group(1)
                    if num not in image_pairs:
                        image_pairs[num] = 0
                    image_pairs[num] += 1
            total_files += sum(image_pairs.values())

        current_file = 0

        if emoji_package:
            emoji_dir = os.path.join(suit_dir, "表情包")
            os.makedirs(emoji_dir, exist_ok=True)

            for emoji_item in emoji_package:
                items = emoji_item.get("items", [])
                for item in items:
                    if not self._is_running:
                        break
                    item_name = item.get("name", "")
                    match = re.match(r'\[.*?_(.*?)\]', item_name)
                    if match:
                        emoji_name = match.group(1)
                    else:
                        emoji_name = item_name
                    emoji_name = self._sanitize_filename(emoji_name)

                    img_url = item.get("properties", {}).get("image")
                    if img_url:
                        img_ext = os.path.splitext(img_url.split("?")[0])[1] or ".png"
                        img_path = os.path.join(emoji_dir, f"{emoji_name}{img_ext}")
                        if self._download_file(img_url, img_path):
                            self.log.emit(f"✓ 表情包：{emoji_name}")
                            downloaded_count += 1
                    current_file += 1
                    overall_percent = int((current_file / total_files) * 100)
                    self.progress.emit(overall_percent, f"正在处理表情包 {emoji_name}...")

        if space_bg:
            bg_dir = os.path.join(suit_dir, "背景图")
            os.makedirs(bg_dir, exist_ok=True)

            for bg_item in space_bg:
                if not self._is_running:
                    break
                props = bg_item.get("properties", {})
                image_pairs = {}
                for key, value in props.items():
                    if not value:
                        continue
                    match = re.match(r'image(\d+)_(landscape|portrait)', key)
                    if match:
                        num = match.group(1)
                        orientation = match.group(2)
                        if num not in image_pairs:
                            image_pairs[num] = {}
                        image_pairs[num][orientation] = value

                for num, orientations in sorted(image_pairs.items(), key=lambda x: int(x[0])):
                    if not self._is_running:
                        break
                    base_name = f"{self._sanitize_filename(name)}_{num}"

                    if "landscape" in orientations:
                        img_url = orientations["landscape"]
                        img_ext = os.path.splitext(img_url.split("?")[0])[1] or ".jpg"
                        img_path = os.path.join(bg_dir, f"{base_name}_landscape{img_ext}")
                        if self._download_file(img_url, img_path):
                            self.log.emit(f"✓ 背景图横版：{base_name}_landscape")
                            downloaded_count += 1
                        current_file += 1
                        overall_percent = int((current_file / total_files) * 100)
                        self.progress.emit(overall_percent, f"正在处理背景图 {base_name}_landscape...")

                    if "portrait" in orientations:
                        img_url = orientations["portrait"]
                        img_ext = os.path.splitext(img_url.split("?")[0])[1] or ".jpg"
                        img_path = os.path.join(bg_dir, f"{base_name}_portrait{img_ext}")
                        if self._download_file(img_url, img_path):
                            self.log.emit(f"✓ 背景图竖版：{base_name}_portrait")
                            downloaded_count += 1
                        current_file += 1
                        overall_percent = int((current_file / total_files) * 100)
                        self.progress.emit(overall_percent, f"正在处理背景图 {base_name}_portrait...")

        self.log.emit(f"\n装扮下载完成，共下载 {downloaded_count} 个文件")
        self.finished.emit(downloaded_count)


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BiliGarbGUI()
    window.show()
    sys.exit(app.exec())