# nana_2/IntentDetector/ai_service/ai_service.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from global_config import settings
from core.log.logger_config import logger

load_dotenv()


class AIService:
    def __init__(self):
        """初始化AI服务，连接到DashScope并加载prompts。"""
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            logger.error("[AI服务] 未在.env文件中找到 DASHSCOPE_API_KEY")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

        # 【修正点 #1】
        # self.prompts 似乎没有被使用，我们可以先用 self.main_prompts
        self.main_prompts = {}
        # 调用和定义的方法名保持一致！
        self._load_main_prompts()

    def _load_main_prompts(self):
        """只加载“主教科书”"""
        try:
            with open(settings.PROMPTS_FILE, 'r', encoding='utf-8') as f:
                self.main_prompts = json.load(f)
            logger.info(f"[AI服务] 成功加载“主教科书”: {settings.PROMPTS_FILE}")
        except Exception as e:
            logger.error(f"[AI服务] 加载“主教科书”失败: {e}")

    def _build_dynamic_prompt(self, loaded_plugins: dict) -> dict:
        """动态构建一个包含所有已加载插件知识的“超级教科书”。"""
        if "command_recognizer" not in self.main_prompts:
            return {}

        dynamic_prompts = json.loads(json.dumps(self.main_prompts["command_recognizer"]))

        logger.info("[AI服务] 开始为AI动态构建“超级教科书”...")
        for plugin_name, plugin_instance in loaded_plugins.items():
            prompt_path = os.path.join(settings.PLUGINS_DIR, plugin_name, f"{plugin_name}_prompt.json")
            if os.path.exists(prompt_path):
                try:
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        plugin_prompt = json.load(f)
                        dynamic_prompts["system_prompt"] += " " + plugin_prompt.get("description", "")
                        dynamic_prompts["examples"].extend(plugin_prompt.get("examples", []))
                        logger.info(f"  - 已加载插件 '{plugin_name}' 的专业技能。")
                except Exception as e:
                    logger.error(f"  - 加载插件 '{plugin_name}' 的教科书失败: {e}")

        return dynamic_prompts

    # 【修正点 #2】
    # 在方法的参数列表里，加上 loaded_plugins: dict
    def recognize_command(self, conversation_history: list, loaded_plugins: dict) -> dict:
        """根据对话历史和已加载插件的知识，调用AI识别用户指令。"""
        fallback_command = {"plugin": None, "command": None, "args": None, "response": "嗯...我好像没太听懂你的意思。"}

        # 在这里，self.prompts 没有被初始化，应该检查 self.main_prompts
        if not self.client or not self.main_prompts:
            logger.warning("[AI服务] AI客户端未初始化或主prompts未加载，返回默认指令。")
            return fallback_command

        prompt_config = self._build_dynamic_prompt(loaded_plugins)

        if not prompt_config:
            logger.error("[AI服务] 动态构建“超级教科书”失败！")
            return fallback_command

        messages = [{"role": "system", "content": prompt_config["system_prompt"]}]
        for example in prompt_config.get("examples", []):
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": json.dumps(example["ai"], ensure_ascii=False)})

        messages.extend(conversation_history)

        logger.info("[AI服务] 准备调用AI模型...")
        try:
            response = self.client.chat.completions.create(
                model="qwen-plus",
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            response_text = response.choices[0].message.content
            logger.info(f"[AI服务] AI模型返回原始结果: {response_text}")
            parsed_response = json.loads(response_text)
            if not isinstance(parsed_response, dict):
                logger.error(f"[AI服务] AI返回了非预期的格式 (类型: {type(parsed_response)})。")
                return fallback_command
            return parsed_response
        except json.JSONDecodeError:
            logger.error(f"[AI服务] AI未返回有效的JSON格式。收到的原始文本: '{response_text}'")
            return fallback_command
        except Exception as e:
            logger.error(f"[AI服务] 调用API时发生未知错误: {e}")
            return fallback_command