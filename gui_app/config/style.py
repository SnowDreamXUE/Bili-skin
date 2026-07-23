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