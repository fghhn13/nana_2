# IntentDetector/ai_service/service.py

import os
import json
from openai import OpenAI
# 假设你的全局配置文件在 a/nana_2.0/global_config/config.py
# from global_config import config as global_cfg

# 为了先能跑起来，我们暂时还用 .env 和之前的方式
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件里的环境变量


class AIService:
    """
    封装与云端/本地AI模型的通信。
    它的唯一职责就是：接收对话历史，返回一个结构化的指令JSON。
    """

    def __init__(self):
     # 从环境变量获取你的DashScope API Key
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            print("错误：未在.env文件中找到 DASHSCOPE_API_KEY")
            self.client = None
        else:
            # 使用你的API Key和DashScope的兼容地址初始化客户端
            self.client = OpenAI(api_key=self.api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

    #     # 加载我们精心设计的prompts.json文件
    #     self._load_prompts()
    #
    # def _load_prompts(self):
    #     try:
    #         with open(app_config.PROMPTS_FILE, 'r', encoding='utf-8') as f:
    #             self.prompts = json.load(f)
    #     except Exception as e:
    #         # 可以在错误信息中打印正确的路径
    #         print(f"错误：加载prompts文件 '{app_config.PROMPTS_FILE}' 失败: {e}")
    #         self.prompts = {}
        # 将来这里会加载我们为指令路由设计的 prompts.json
        # self._load_prompts()

    def recognize_command(self, conversation_history: list) -> dict:
        """
        调用AI模型，将对话历史转化为结构化指令。

        :param conversation_history: 到目前为止的对话列表
        :return: 一个包含 plugin, command, args, response 的字典
        """
        if not self.client:
            print("[AI服务] AI客户端未初始化，返回错误信息。")
            return {
                "plugin": None, "command": None, "args": None,
                "response": "抱歉，我的AI大脑没有正确连接，请检查API Key配置。"
            }

        print(f"[AI服务] 收到对话历史，准备调用AI模型...")

        # --- 【核心】调用AI模型的逻辑将在这里 ---
        # messages = self._build_prompt(conversation_history)
        # response = self.client.chat.completions.create(...)
        # command_json = json.loads(response.choices[0].message.content)
        # return command_json

        # =============================================================
        # 【测试阶段】: 为了先测试流程，我们暂时不实际调用API
        # 而是返回一个写死的、模拟的指令JSON
        # =============================================================
        # 【测试阶段】: 修改这里的模拟指令
        print("[AI服务] 测试模式：返回一个专门用于测试的指令。")
        last_user_message = conversation_history[-1]['content']
        dummy_command = {
            "plugin": "test_plugin",  # <--- 修改这里，指向我们的测试插件
            "command": "echo",  # <--- 修改这里，调用插件的echo命令
            "args": {"text_from_user": last_user_message},  # 随便传点参数
            "response": "（模拟AI对话）收到，正在派发测试任务..."
        }
        return dummy_command