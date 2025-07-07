# Gui/windows/main_window.py

import queue
from PySide6.QtWidgets import (
    QMainWindow, QTextEdit, QLineEdit, QPushButton, QWidget,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QPixmap, QIcon, QFont
from PySide6.QtCore import QTimer
from ..config import gui_config
from ..handle import event_handlers
from global_config import settings


class MainWindow(QMainWindow):
    def __init__(self, app_controller):
        """主窗口构造函数"""
        super().__init__()

        self.settings = settings
        self.controller = app_controller
        self.gui_config = gui_config


        self.note_listbox = None

        # 加载按钮图片
        self.img_send_normal = QPixmap(self.gui_config.IMG_SEND_NORMAL)
        self.img_send_hover = QPixmap(self.gui_config.IMG_SEND_HOVER)
        self.img_send_press = QPixmap(self.gui_config.IMG_SEND_PRESS)
        if self.img_send_normal.isNull():
            QMessageBox.critical(self, "资源错误", "找不到按钮图片文件！")

        # --- 1. 基础窗口设置 ---
        self.setWindowTitle(self.gui_config.APP_TITLE)
        self.resize(1100, 800)
        self.setStyleSheet(f"background-color: {self.gui_config.BG_MAIN};")

        # --- 2. 状态与通信 ---
        self.ui_queue = queue.Queue()

        # --- 3. 创建界面和绑定事件 ---
        self.handler = event_handlers.EventHandler(self, self.controller)
        self._create_widgets()
        self.handler.bind_events()
        self.handler.add_placeholder()

        # --- 4. 启动UI更新循环 ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_ui_queue)
        self.timer.start(100)

        # --- 5. 初始化完成 ---
        self.user_input_entry.setFocus()

        self.show()


    def _create_widgets(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # 聊天显示框
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont(self.gui_config.GENERAL_FONT_FAMILY, self.gui_config.GENERAL_FONT_SIZE))
        self.chat_display.setStyleSheet(
            f"background-color: {self.gui_config.BG_INPUT};"
            f"color: {self.gui_config.FG_TEXT};"
        )
        main_layout.addWidget(self.chat_display, 1)

        # 输入框和发送按钮
        input_layout = QHBoxLayout()
        main_layout.addLayout(input_layout)

        self.user_input_entry = QLineEdit()
        self.user_input_entry.setFont(QFont(self.gui_config.GENERAL_FONT_FAMILY, self.gui_config.GENERAL_FONT_SIZE))
        self.user_input_entry.setStyleSheet(
            f"background-color: {self.gui_config.BG_INPUT};"
            f"color: {self.gui_config.FG_TEXT};"
        )
        input_layout.addWidget(self.user_input_entry, 1)

        self.send_button = QPushButton()
        if not self.img_send_normal.isNull():
            self.send_button.setIcon(QIcon(self.img_send_normal))
        else:
            self.send_button.setText("发送")
        self.send_button.setStyleSheet(f"background-color: {self.gui_config.BG_MAIN}; border: none;")
        input_layout.addWidget(self.send_button)

    def append_message(self, sender, message, sender_tag):
        color_map = {
            "user_sender": "#81C784",
            "nana_sender": "#82AAFF",
            "error_sender": "#FF5370",
        }
        color = color_map.get(sender_tag, self.gui_config.FG_TEXT)
        self.chat_display.setReadOnly(False)
        self.chat_display.append(
            f'<span style="color:{color}; font-weight:bold">{sender}:</span> {message}<br/>'
        )
        self.chat_display.setReadOnly(True)

    def set_ui_state(self, state: str):
        """
        设置UI的交互状态，'enabled' 或 'disabled'。
        """
        enabled = state == 'enabled'
        self.user_input_entry.setEnabled(enabled)
        self.send_button.setEnabled(enabled)

    def process_ui_queue(self):
        """
        处理消息队列，在主线程中安全地更新UI。
        """
        try:
            while not self.ui_queue.empty():
                msg_type, data = self.ui_queue.get_nowait()

                # 在这里根据消息类型，调用不同的UI更新方法
                if msg_type == "APPEND_MESSAGE":
                    sender, message, tag = data
                    self.append_message(sender, message, tag)
                elif msg_type == "SET_STATE":
                    self.set_ui_state(data)
                # elif msg_type == "SHOW_ERROR":
                #     messagebox.showerror("错误", data)
                # ... 在这里可以定义和处理更多类型的UI更新消息 ...
        finally:
            pass  # QTimer 会持续调用，无需手动重新启动

    def on_closing(self):

        self.is_running = False

        self.controller.on_app_exit()

    def closeEvent(self, event):
        self.on_closing()
        event.accept()

