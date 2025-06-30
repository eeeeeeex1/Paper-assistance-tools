import logging
import os
import time
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 确保日志目录存在
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志文件名（按日期生成）
LOG_FILENAME = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")

def setup_logging(debug=False):
    """配置并初始化日志系统"""
    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # 日志格式
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 2. 文件处理器（按大小分割日志，防止单个文件过大）
    file_handler = RotatingFileHandler(
        LOG_FILENAME,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5  # 保留5个备份文件
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    
    return logger

# 初始化日志（默认非调试模式）
logger = setup_logging(debug=False)