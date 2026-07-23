from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QTextEdit, QMessageBox,
    QCheckBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal

from gui_app.config.style import ELEMENTUI_STYLE
from gui_app.core.downloader import Downloader


class ResultPage(QWidget):
    add_to_download = Signal(dict, list)

    def __init__(self):
        super().__init__()
        self.search_results = []
        self.selected_item = None
        self.resource_checkboxes = {}
        self.added_item_ids = set()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        title_label = QLabel("搜索结果")
        title_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #303133;")
        header_layout.addWidget(title_label)

        self.count_label = QLabel("")
        self.count_label.setStyleSheet("font-size: 13px; color: #909399;")
        header_layout.addWidget(self.count_label)

        header_layout.addStretch()

        self.add_all_btn = QPushButton("一键添加所有")
        self.add_all_btn.clicked.connect(self.on_add_all_to_download)
        self.add_all_btn.setEnabled(False)
        header_layout.addWidget(self.add_all_btn)

        self.add_btn = QPushButton("添加到下载列表")
        self.add_btn.clicked.connect(self.on_add_to_download)
        self.add_btn.setEnabled(False)
        header_layout.addWidget(self.add_btn)

        layout.addLayout(header_layout)

        splitter_layout = QHBoxLayout()
        splitter_layout.setSpacing(15)

        result_group = QWidget()
        result_group.setStyleSheet("background-color: white; border-radius: 4px; border: 1px solid #ebeef5;")
        result_layout = QVBoxLayout(result_group)
        result_layout.setContentsMargins(0, 0, 0, 0)

        result_header = QLabel("搜索结果列表")
        result_header.setStyleSheet("padding: 10px 15px; font-weight: 500; color: #606266; border-bottom: 1px solid #f2f6fc;")
        result_layout.addWidget(result_header)

        self.result_list = QListWidget()
        self.result_list.itemClicked.connect(self.on_select_item)
        self.result_list.setStyleSheet("""
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
        result_layout.addWidget(self.result_list)
        self._show_empty_result_hint()

        splitter_layout.addWidget(result_group, 1)

        detail_group = QWidget()
        detail_group.setStyleSheet("background-color: white; border-radius: 4px; border: 1px solid #ebeef5;")
        detail_layout = QVBoxLayout(detail_group)
        detail_layout.setContentsMargins(0, 0, 0, 0)

        detail_header = QLabel("详情信息")
        detail_header.setStyleSheet("padding: 10px 15px; font-weight: 500; color: #606266; border-bottom: 1px solid #f2f6fc;")
        detail_layout.addWidget(detail_header)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setPlaceholderText("选择一个项目查看详情...")
        self.detail_text.setStyleSheet("""
            QTextEdit {
                font-size: 13px;
                background-color: white;
            }
        """)
        detail_layout.addWidget(self.detail_text)

        self.resource_group = QGroupBox("下载资源类别")
        self.resource_group.setEnabled(False)
        self.resource_layout = QGridLayout(self.resource_group)
        self.resource_layout.setSpacing(8)
        detail_layout.addWidget(self.resource_group)

        splitter_layout.addWidget(detail_group, 1)

        layout.addLayout(splitter_layout)

    def _clear_resource_checkboxes(self):
        for checkbox in self.resource_checkboxes.values():
            checkbox.setParent(None)
        self.resource_checkboxes.clear()

    def _setup_resource_checkboxes(self, resource_types: dict, defaults: list = None):
        self._clear_resource_checkboxes()
        row, col = 0, 0
        for key, label in resource_types.items():
            checkbox = QCheckBox(label)
            checkbox.setChecked(key in (defaults or []))
            checkbox.setProperty("resource_key", key)
            self.resource_checkboxes[key] = checkbox
            self.resource_layout.addWidget(checkbox, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def set_results(self, results: list):
        self.search_results = results
        self.result_list.clear()
        self.detail_text.clear()
        self.selected_item = None
        self.add_btn.setEnabled(False)
        self.add_all_btn.setEnabled(len(results) > 0)
        self.resource_group.setEnabled(False)
        self._clear_resource_checkboxes()
        self.added_item_ids.clear()

        if not results:
            self._show_empty_result_hint()
            self.count_label.setText("")
            return

        self.count_label.setText(f"共 {len(results)} 条结果")

        for item in results:
            name = item.get("name", "未知")
            part_id = item.get("part_id", 0)
            item_type = "收藏集" if part_id == 0 else "装扮"

            list_item = QListWidgetItem(f"[{item_type}] {name}")
            list_item.setData(Qt.UserRole, item)
            self.result_list.addItem(list_item)

    def _show_empty_result_hint(self):
        hint_item = QListWidgetItem("暂无搜索结果，请前往「搜索」页面进行搜索")
        hint_item.setForeground(Qt.GlobalColor.gray)
        hint_item.setFlags(hint_item.flags() & ~Qt.ItemIsSelectable & ~Qt.ItemIsEnabled)
        self.result_list.addItem(hint_item)

    def on_select_item(self, item: QListWidgetItem):
        data = item.data(Qt.UserRole)
        if not data:
            return

        self.selected_item = data
        self.add_btn.setEnabled(True)

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
            self._setup_resource_checkboxes(
                Downloader.COLLECTIBLE_RESOURCE_TYPES,
                defaults=["card_img", "video_list"]
            )
        else:
            info_text += f"item_id：{item_id}\n"
            self._setup_resource_checkboxes(
                Downloader.SUIT_RESOURCE_TYPES,
                defaults=["emoji_package", "space_bg"]
            )
        info_text += f"封面：{cover[:80]}{'...' if len(cover) > 80 else ''}"

        self.detail_text.setText(info_text)
        self.resource_group.setEnabled(True)

    def get_selected_resource_types(self) -> list:
        types = []
        for key, checkbox in self.resource_checkboxes.items():
            if checkbox.isChecked():
                types.append(key)
        return types

    def _get_unique_id(self, item: dict) -> str:
        part_id = item.get("part_id", 0)
        if part_id == 0:
            properties = item.get("properties", {})
            act_id = properties.get("dlc_act_id", "")
            lottery_id = properties.get("dlc_lottery_id", "")
            return f"collect_{act_id}_{lottery_id}"
        else:
            return f"suit_{item.get('item_id', '')}"

    def on_add_to_download(self):
        if self.selected_item:
            resource_types = self.get_selected_resource_types()
            if not resource_types:
                QMessageBox.warning(self, "提示", "请至少选择一个资源类别")
                return
            unique_id = self._get_unique_id(self.selected_item)
            if unique_id:
                self.added_item_ids.add(unique_id)
            self.add_to_download.emit(self.selected_item, resource_types)
            self.add_btn.setEnabled(False)
            self.selected_item = None
            self.resource_group.setEnabled(False)

    def on_add_all_to_download(self):
        if not self.search_results:
            return

        added_count = 0
        for item in self.search_results:
            unique_id = self._get_unique_id(item)
            if unique_id and unique_id in self.added_item_ids:
                continue

            part_id = item.get("part_id", 0)
            if part_id == 0:
                resource_types = ["card_img", "video_list"]
            else:
                resource_types = ["emoji_package", "space_bg"]

            self.add_to_download.emit(item, resource_types)
            if unique_id:
                self.added_item_ids.add(unique_id)
            added_count += 1

        if added_count == 0:
            QMessageBox.information(self, "提示", "所有任务已添加")
        self.add_all_btn.setEnabled(False)