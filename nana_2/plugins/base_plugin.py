# plugins/base_plugin.py

from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """
    所有功能插件的基类（插件契约）。
    它定义了每个插件都必须实现的一套标准接口（方法），
    这样我们的主程序（CommandExecutor）就知道如何与任何一个插件进行统一的交互。
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        【必须实现】返回插件的唯一名称。
        这个名字要和AI指令里的'plugin'字段对应。
        例如: "note_taker"
        """
        pass

    @abstractmethod
    def get_commands(self) -> list[str]:
        """
        【必须实现】返回这个插件能执行的所有命令的列表。
        例如: ["create", "delete", "search"]
        """
        pass

    @abstractmethod
    def execute(self, command: str, args: dict, controller):
        """
        【必须实现】执行一个具体的命令。
        这是插件最核心的功能实现部分。

        :param command: 要执行的命令名，例如 "create"。
        :param args: 命令需要的参数字典，例如 {"entity": "我的新笔记"}。
        :param controller: AppController的实例，插件可以通过它与GUI通信，
                           例如 controller.view.ui_queue.put(...)。
        """
        pass