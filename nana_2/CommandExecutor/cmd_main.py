# CommandExecutor/cmd_main.py
import os
import importlib
from global_config import settings
from core.log.logger_config import logger
from IntentDetector.intent_registry import load_intent_mapping
from plugins.base_plugin import BasePlugin

class CommandExecutor:
    """
    命令执行中心（总调度室）。
    负责加载所有插件，并根据指令调度正确的插件来执行任务。
    """

    def __init__(self):
        self.plugins = {}
        self._load_plugins()

    def refresh_commands(self):
        """Reload all plugin modules to refresh available commands."""
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
        logger.info(f"[执行器] 正在从 '{plugins_dir}' 目录加载插件...")

        # 遍历 plugins 文件夹下的所有子文件夹
        for plugin_name in os.listdir(plugins_dir):
            plugin_path = os.path.join(plugins_dir, plugin_name)
            if os.path.isdir(plugin_path) and not plugin_name.startswith('__'):
                try:
                    # 动态导入插件模块，例如: importlib.import_module("plugins.note_taker")
                    module = importlib.import_module(f"plugins.{plugin_name}")
                    if hasattr(module, 'get_plugin'):
                        plugin_instance = module.get_plugin()
                        if not isinstance(plugin_instance, BasePlugin):
                            raise TypeError(
                                f"插件 '{plugin_name}' 必须继承 BasePlugin"
                            )

                        for method in ("get_name", "get_commands", "execute"):
                            if not hasattr(plugin_instance, method):
                                raise AttributeError(
                                    f"插件 '{plugin_name}' 缺少必要方法 '{method}'"
                                )

                        plugin_instance.on_load()
                        self.plugins[plugin_instance.get_name()] = plugin_instance
                        load_intent_mapping(plugin_instance.get_name())
                        logger.info(f"  - 成功加载插件: '{plugin_instance.get_name()}'")
                except Exception as e:
                    logger.info(f"  - 加载插件 {plugin_name} 失败: {e}")

    @property
    def loaded_plugins(self) -> dict:
        """
        一个公开的属性，让外部可以获取到所有已加载的插件。
        就像一个透明的展示柜，展示着所有可用的工具。
        """
        return self.plugins

    def execute_command(self, command: dict, controller):
        """
        接收指令并执行。这是提供给外部调用的主方法。
        """
        plugin_name = command.get('plugin')

        if not plugin_name:
            # 如果指令没有指定插件，说明可能是一条纯聊天或无需执行的消息
            logger.info(f"[执行器] 收到无需执行的指令。")
            return

        logger.info(f"[执行器] 收到指令，需要插件 '{plugin_name}' 来执行。")

        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            cmd_name = command.get('command')
            cmd_args = command.get('args', {})
            logger.info(
                f"[执行器] 调用插件 '{plugin_name}' 执行命令 '{cmd_name}'，参数: {cmd_args}"
            )
            try:
                plugin.execute(cmd_name, cmd_args, controller)
            except Exception as e:
                logger.error(
                    f"[执行器] 插件 '{plugin_name}' 执行命令 '{cmd_name}' 失败: {e}",
                    exc_info=True,
                )
        else:
            logger.info(f"[执行器] 错误：找不到名为 '{plugin_name}' 的插件。")
