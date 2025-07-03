# config/logger_config.py
import logging
import os
from .app_config import ROOT_DIR

def setup_logger():
    """配置并返回一个日志记录器"""
    log_file_path = os.path.join(ROOT_DIR, 'nana_log.txt')

    # 创建一个日志记录器
    logger = logging.getLogger('NanaLogger')
    logger.setLevel(logging.INFO)

    # 防止重复添加处理器
    if not logger.handlers:
        # 创建一个文件处理器，用于写入日志文件
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 创建一个控制台处理器，用于在终端打印日志（方便调试）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 定义日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 将处理器添加到日志记录器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# 创建一个全局日志实例
logger = setup_logger()