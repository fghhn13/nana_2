# CommandExecutor/cmd_main.py
import os
import importlib
from global_config import settings

class CommandExecutor:
    """
    命令执行中心（总调度室）。
    负责加载所有插件，并根据指令调度正确的插件来执行任务。
    """

    def __init__(self):
        self.plugins = {}
        self._load_plugins()

    def _load_plugins(self):
        """
        动态加载所有在 a/nana_2.0/plugins/ 文件夹里的插件。
        这部分是插件系统的核心，非常酷！
        """
        current_file_path = os.path.abspath(__file__)
        # 获取CommandExecutor文件夹的路径
        command_executor_dir = os.path.dirname(current_file_path)
        # 获取项目的根目录(nana_2)的路径
        project_root = os.path.dirname(command_executor_dir)
         # 拼接出plugins文件夹的绝对路径
        plugins_dir = settings.PLUGINS_DIR
        print(f"[执行器] 正在从 '{plugins_dir}' 目录加载插件...")

        # 遍历 plugins 文件夹下的所有子文件夹
        for plugin_name in os.listdir(plugins_dir):
            plugin_path = os.path.join(plugins_dir, plugin_name)
            # 确保它是一个文件夹，并且不是以 __ 开头的（比如__pycache__）
            if os.path.isdir(plugin_path) and not plugin_name.startswith('__'):
                try:
                    # 动态导入插件模块，例如: importlib.import_module("plugins.note_taker")
                    module = importlib.import_module(f"plugins.{plugin_name}")
                    if hasattr(module, 'get_plugin'):
                        plugin_instance = module.get_plugin()
                        self.plugins[plugin_instance.get_name()] = plugin_instance
                        print(f"  - 成功加载插件: '{plugin_instance.get_name()}'")
                except Exception as e:
                    print(f"  - 加载插件 {plugin_name} 失败: {e}")

    def execute_command(self, command: dict, controller):
        """
        接收指令并执行。这是提供给外部调用的主方法。
        """
        plugin_name = command.get('plugin')

        if not plugin_name:
            # 如果指令没有指定插件，说明可能是一条纯聊天或无需执行的消息
            print(f"[执行器] 收到无需执行的指令。")
            return

        print(f"[执行器] 收到指令，需要插件 '{plugin_name}' 来执行。")

        if plugin_name in self.plugins:
            # 找到了对应的插件，让它执行
            plugin = self.plugins[plugin_name]
            # 把指令里的 command 和 args 交给插件
            plugin.execute(
                command.get('command'),
                command.get('args', {}),
                controller
                # 使用 .get 提供默认空字典，更安全
                # 我们还需要把主控制器传给插件，以便插件能和GUI通信
                # 这个我们下一步再完善
            )
        else:
            print(f"[执行器] 错误：找不到名为 '{plugin_name}' 的插件。")
            # 这里可以向GUI发送一个错误消息