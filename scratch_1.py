import os
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit,
                             QListWidget, QVBoxLayout, QLabel,
                             QPushButton, QHBoxLayout, QSizeGrip)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QCursor


class DesktopSearchPlugin(QWidget):
    def __init__(self):
        super().__init__()
        # 先定义属性
        self.default_size = (400, 500)
        self.min_size = (300, 400)
        self.m_drag = False
        self.m_DragPosition = None
        self.m_resize = False
        self.m_ResizePosition = None

        self.initUI()
        self.desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        self.all_files = []
        self.load_desktop_files()

    def initUI(self):
        # 设置窗口属性
        self.setWindowTitle('桌面文件搜索')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(100, 100, self.default_size[0], self.default_size[1])
        self.setMinimumSize(self.min_size[0], self.min_size[1])

        # 创建标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("background-color: #e0e0e0;")

        # 标题栏布局
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(5, 0, 5, 0)

        # 标题标签
        self.title_label = QLabel("桌面文件搜索")
        self.title_label.setStyleSheet("font-weight: bold;")

        # 窗口控制按钮
        self.minimize_btn = QPushButton("—")
        self.minimize_btn.setFixedSize(20, 20)
        self.minimize_btn.clicked.connect(self.showMinimized)

        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(20, 20)
        self.maximize_btn.clicked.connect(self.toggle_maximize)

        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)

        # 设置按钮样式
        btn_style = """
            QPushButton {
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton#close_btn:hover {
                color: red;
            }
        """
        self.minimize_btn.setStyleSheet(btn_style)
        self.maximize_btn.setStyleSheet(btn_style)
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setStyleSheet(btn_style)
        self.close_btn.clicked.connect(self.close)

        # 添加到标题栏
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.minimize_btn)
        title_layout.addWidget(self.maximize_btn)
        title_layout.addWidget(self.close_btn)

        # 创建UI元素
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("输入文件名搜索...")
        self.search_box.textChanged.connect(self.search_files)

        self.result_list = QListWidget()
        self.result_list.itemDoubleClicked.connect(self.open_file)

        self.info_label = QLabel("双击打开文件 | ESC隐藏窗口 | 拖动边缘调整大小")
        self.info_label.setAlignment(Qt.AlignCenter)

        # 设置主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 0, 5, 5)
        main_layout.setSpacing(5)
        main_layout.addWidget(title_bar)
        main_layout.addWidget(self.search_box)
        main_layout.addWidget(self.result_list)
        main_layout.addWidget(self.info_label)

        # 添加右下角的大小调整手柄
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(16, 16)

        self.setLayout(main_layout)

        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QLabel {
                padding: 5px;
                font-size: 11px;
                color: #666;
            }
            QSizeGrip {
                width: 16px;
                height: 16px;
                background: none;
            }
        """)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.showMaximized()
            self.maximize_btn.setText("❐")

    # 鼠标事件处理 - 拖动窗口
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 检查是否在边缘区域 (用于调整大小)
            margin = 5
            rect = self.rect()
            top_rect = QRect(0, 0, rect.width(), margin)
            bottom_rect = QRect(0, rect.height() - margin, rect.width(), margin)
            left_rect = QRect(0, 0, margin, rect.height())
            right_rect = QRect(rect.width() - margin, 0, margin, rect.height())

            pos = event.pos()
            if (bottom_rect.contains(pos) or right_rect.contains(pos)) and not self.isMaximized():
                self.m_resize = True
                self.m_ResizePosition = pos
            else:
                self.m_drag = True
                self.m_DragPosition = event.globalPos() - self.pos()
            self.setCursor(QCursor(Qt.SizeAllCursor if not self.m_resize else Qt.SizeFDiagCursor))

    def mouseMoveEvent(self, event):
        if self.m_drag:
            self.move(event.globalPos() - self.m_DragPosition)
            event.accept()
        elif self.m_resize and not self.isMaximized():
            diff = event.pos() - self.m_ResizePosition
            new_width = max(self.min_size[0], self.width() + diff.x())
            new_height = max(self.min_size[1], self.height() + diff.y())
            self.resize(new_width, new_height)
            self.m_ResizePosition = event.pos()
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_drag = False
        self.m_resize = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def resizeEvent(self, event):
        # 调整右下角手柄位置
        self.size_grip.move(self.width() - 20, self.height() - 20)
        super().resizeEvent(event)

    def load_desktop_files(self):
        """加载桌面所有文件"""
        self.all_files = []
        for root, dirs, files in os.walk(self.desktop_path):
            for file in files:
                self.all_files.append({
                    'name': file,
                    'path': os.path.join(root, file),
                    'lower_name': file.lower()
                })

    def search_files(self):
        """根据输入搜索文件"""
        search_text = self.search_box.text().lower()
        self.result_list.clear()

        if not search_text:
            return

        for file in self.all_files:
            if search_text in file['lower_name']:
                self.result_list.addItem(file['name'])

    def open_file(self, item):
        """双击打开文件"""
        file_name = item.text()
        for file in self.all_files:
            if file['name'] == file_name:
                os.startfile(file['path'])
                self.hide()
                break

    def keyPressEvent(self, event):
        """快捷键处理"""
        if event.key() == Qt.Key_Escape:
            self.hide()
        elif event.key() == Qt.Key_Return and self.result_list.currentItem():
            self.open_file(self.result_list.currentItem())

    def showEvent(self, event):
        """显示时刷新文件列表并将焦点置于搜索框"""
        self.load_desktop_files()
        self.search_box.setFocus()
        self.search_box.clear()


def main():
    app = QApplication(sys.argv)
    plugin = DesktopSearchPlugin()
    plugin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()