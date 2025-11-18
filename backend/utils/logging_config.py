"""日志配置模块

提供统一的日志配置和日志记录器获取功能。
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


class LoggingConfigurator:
    """配置应用程序日志系统"""
    
    # 日志配置常量
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_FILE_PATH = "logs/app.log"
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    _configured = False
    
    @classmethod
    def setup_logging(
        cls,
        log_level: str = 'INFO',
        log_file: Optional[str] = None,
        log_to_console: bool = True,
        log_to_file: bool = True
    ) -> None:
        """
        配置根日志记录器
        
        Args:
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: 日志文件路径，默认使用 LOG_FILE_PATH
            log_to_console: 是否输出到控制台
            log_to_file: 是否输出到文件
        """
        if cls._configured:
            return
        
        # 获取根日志记录器
        root_logger = logging.getLogger()
        
        # 设置日志级别
        level = getattr(logging, log_level.upper(), logging.INFO)
        root_logger.setLevel(level)
        
        # 清除现有处理器
        root_logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            fmt=cls.LOG_FORMAT,
            datefmt=cls.LOG_DATE_FORMAT
        )
        
        # 配置控制台处理器
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # 配置文件处理器
        if log_to_file:
            log_file_path = log_file or cls.LOG_FILE_PATH
            
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 创建滚动文件处理器
            file_handler = RotatingFileHandler(
                filename=log_file_path,
                maxBytes=cls.LOG_MAX_BYTES,
                backupCount=cls.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        cls._configured = True
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        获取指定名称的日志记录器
        
        Args:
            name: 日志记录器名称，通常使用 __name__
            
        Returns:
            配置好的 Logger 实例
        """
        return logging.getLogger(name)
