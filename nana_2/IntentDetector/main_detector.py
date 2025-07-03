# IntentDetector/main_detector.py

# 导入我们刚刚创建的 AI 服务模块
from .ai_service.ai_service import AIService
from .CommandParser.parser import CommandParser


class MainDetector:
    """
    意图识别模块的主控制器 (部门主管).
    负责协调 AI服务 和 (未来的)命令解析器.
    """

    def __init__(self):
        """
        在初始化的时候，创建好自己的下属实例。
        """
        self.ai_service = AIService()
        self.command_parser = CommandParser() # “参谋部”我们下一步再建

        print("[检测器] 意图检测器已初始化。")

    def detect_and_parse(self, conversation_history: list) -> dict:
        """
        这是提供给外部调用的主方法。
        它会完整地执行“意图检测和解析”的整个流程。

        :param conversation_history: 对话历史
        :return: 一个经过校验和解析的、干净的指令字典
        """
        print("[检测器] 开始检测用户意图...")

        # --- 第 1 步：让“联络员”(AIService)去调用AI ---
        raw_command_from_ai = self.ai_service.recognize_command(conversation_history)
        print(f"[检测器] 从AI服务收到原始指令: {raw_command_from_ai}")

        # --- 第 2 步：(即将到来) 让“参谋部”(CommandParser)去审查和翻译指令 ---
        # 这一步我们先注释掉，等建好 CommandParser 再启用
        clean_command = self.command_parser.parse(raw_command_from_ai)
        # print(f"[检测器] 经过解析器处理后的干净指令: {clean_command}")

        # 在“参谋部”建好之前，我们先直接把原始指令当作最终结果返回
        final_command = raw_command_from_ai

        print("[检测器] 意图检测流程完成。")
        return final_command