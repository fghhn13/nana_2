# Gui/handle/event_handlers.py
from core.log.logger_config import logger
from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QIcon


class EventHandler(QObject):
    def __init__(self, main_view, controller):
        super().__init__()
        self.view = main_view
        self.controller = controller
        self.placeholder_text = self.view.gui_config.INPUT_PLACEHOLDER

    def on_send_click(self, event=None):
        """
        处理“发送”按钮的点击事件 或 输入框的回车事件。
        """
        user_text = self.view.user_input_entry.get().strip()

        # 如果输入为空或者是占位符，则不执行任何操作
        if not user_text or user_text == self.placeholder_text:
            return

        logger.info(f"捕获到用户输入: {user_text}")

        # 清空输入框
        self.view.user_input_entry.clear()

        # 通过控制器将用户输入发送到后端逻辑
        self.controller.process_user_input(user_text)

        return


    def bind_events(self):
        """集中绑定所有事件。"""
        self.view.send_button.clicked.connect(self.on_send_click)
        self.view.send_button.installEventFilter(self)
        self.view.user_input_entry.returnPressed.connect(self.on_input_enter)
        self.view.user_input_entry.installEventFilter(self)
        self.view.chat_display.viewport().installEventFilter(self)


    def eventFilter(self, obj, event):
        if obj == self.view.send_button:
            if event.type() == QEvent.Enter and not self.view.img_send_hover.isNull():
                self.view.send_button.setIcon(QIcon(self.view.img_send_hover))
            elif event.type() == QEvent.Leave and not self.view.img_send_normal.isNull():
                self.view.send_button.setIcon(QIcon(self.view.img_send_normal))
            elif event.type() == QEvent.MouseButtonPress and not self.view.img_send_press.isNull():
                self.view.send_button.setIcon(QIcon(self.view.img_send_press))
            elif event.type() == QEvent.MouseButtonRelease:
                if self.view.send_button.rect().contains(event.pos()) and not self.view.img_send_hover.isNull():
                    self.view.send_button.setIcon(QIcon(self.view.img_send_hover))
                elif not self.view.img_send_normal.isNull():
                    self.view.send_button.setIcon(QIcon(self.view.img_send_normal))
        elif obj == self.view.chat_display.viewport() and event.type() == QEvent.Wheel:
            delta = event.angleDelta().y()
            bar = self.view.chat_display.verticalScrollBar()
            bar.setValue(bar.value() - delta)
            return True
        elif obj == self.view.user_input_entry:
            if event.type() == QEvent.FocusIn:
                self.on_entry_focus_in()
            elif event.type() == QEvent.FocusOut:
                self.on_entry_focus_out()
        return super().eventFilter(obj, event)

    def on_input_enter(self):
        self.on_send_click()


    def add_placeholder(self):
        """添加占位提示文本"""
        self.view.user_input_entry.setPlaceholderText(self.placeholder_text)

    def remove_placeholder(self):
        """移除占位提示文本"""
        self.view.user_input_entry.setPlaceholderText("")

    def on_entry_focus_in(self, event):
        """当输入框获得焦点时触发"""
        # 如果当前显示的是提示文本，就清空它
        if self.view.user_input_entry.text() == "":
            self.remove_placeholder()

    def on_entry_focus_out(self, event):
        """当输入框失去焦点时触发"""
        # 如果输入框里什么都没有，就重新显示提示文本
        if not self.view.user_input_entry.text():
            self.add_placeholder()


