"""Application configuration settings"""
import os
import logging
from typing import Optional

from backend.config.constants import (
    DEFAULT_HISTORY_COLLECTION_INTERVAL,
    DEFAULT_HISTORY_RESOLUTION,
    HISTORY_CACHE_TTL,
    HISTORY_DEFAULT_LIMIT,
    HISTORY_MAX_LIMIT,
    DEFAULT_TRADING_CONCURRENCY,
    DEFAULT_MODEL_CYCLE_TIMEOUT,
)


class ConfigurationError(Exception):
    """配置错误异常"""
    pass


class Config:
    """Application configuration loaded from environment variables"""
    
    def __init__(self):
        """初始化并验证配置"""
        self._logger: Optional[logging.Logger] = None
        self._load_and_validate()
    
    def _get_logger(self) -> logging.Logger:
        """获取日志记录器（延迟初始化）"""
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger
    
    def _load_and_validate(self) -> None:
        """加载并验证所有配置"""
        # API server configuration
        self.DEBUG = os.getenv('DEBUG', 'False') == 'True'
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = self._validate_port(os.getenv('PORT', '5000'))
        
        # Database configuration (PostgreSQL only)
        self.POSTGRES_URI = os.getenv(
            'POSTGRES_URI',
            'postgresql://aitrade:aitrade@localhost:5432/aitrade'
        )
        self._validate_database_config()
        
        # Market data configuration
        self.MARKET_CACHE_DURATION = self._validate_positive_int(
            os.getenv('MARKET_CACHE_DURATION', '5'),
            'MARKET_CACHE_DURATION'
        )
        self.MARKET_API_URL = os.getenv('MARKET_API_URL', 'https://api.coingecko.com/api/v3')
        
        # Market history configuration
        self.MARKET_HISTORY_ENABLED = os.getenv('MARKET_HISTORY_ENABLED', 'True') == 'True'
        self.MARKET_HISTORY_INTERVAL = self._validate_positive_int(
            os.getenv('MARKET_HISTORY_INTERVAL', str(DEFAULT_HISTORY_COLLECTION_INTERVAL)),
            'MARKET_HISTORY_INTERVAL'
        )
        self.MARKET_HISTORY_RESOLUTION = self._validate_positive_int(
            os.getenv('MARKET_HISTORY_RESOLUTION', str(DEFAULT_HISTORY_RESOLUTION)),
            'MARKET_HISTORY_RESOLUTION'
        )
        self.MARKET_HISTORY_MAX_POINTS = self._validate_positive_int(
            os.getenv('MARKET_HISTORY_MAX_POINTS', str(HISTORY_DEFAULT_LIMIT)),
            'MARKET_HISTORY_MAX_POINTS'
        )
        if self.MARKET_HISTORY_MAX_POINTS > HISTORY_MAX_LIMIT:
            self.MARKET_HISTORY_MAX_POINTS = HISTORY_MAX_LIMIT
        self.MARKET_HISTORY_CACHE_TTL = self._validate_positive_int(
            os.getenv('MARKET_HISTORY_CACHE_TTL', str(HISTORY_CACHE_TTL)),
            'MARKET_HISTORY_CACHE_TTL'
        )
        
        # Trading coins configuration
        _coins_str = os.getenv('TRADING_COINS', 'BTC,ETH,SOL,BNB,XRP,DOGE')
        self.DEFAULT_COINS = [coin.strip() for coin in _coins_str.split(',') if coin.strip()]
        
        # Auto trading
        self.AUTO_TRADING = os.getenv('AUTO_TRADING', 'True') == 'True'
        self.TRADING_MAX_CONCURRENCY = self._validate_positive_int(
            os.getenv('TRADING_MAX_CONCURRENCY', str(DEFAULT_TRADING_CONCURRENCY)),
            'TRADING_MAX_CONCURRENCY'
        )
        self.MODEL_CYCLE_TIMEOUT = self._validate_positive_int(
            os.getenv('MODEL_CYCLE_TIMEOUT', str(DEFAULT_MODEL_CYCLE_TIMEOUT)),
            'MODEL_CYCLE_TIMEOUT'
        )
        
        # Logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
        if self.LOG_LEVEL not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ConfigurationError(f"无效的日志级别: {self.LOG_LEVEL}")
        
        # 记录配置（排除敏感信息）
        self._log_configuration()
    
    def _validate_port(self, port_str: str) -> int:
        """
        验证端口号范围（1-65535）
        
        Args:
            port_str: 端口号字符串
            
        Returns:
            验证后的端口号
            
        Raises:
            ConfigurationError: 端口号无效
        """
        try:
            port = int(port_str)
        except ValueError:
            raise ConfigurationError(f"端口号必须是整数: {port_str}")
        
        if port < 1 or port > 65535:
            raise ConfigurationError(f"端口号必须在 1-65535 范围内: {port}")
        
        return port
    
    def _validate_positive_int(self, value_str: str, name: str) -> int:
        """
        验证正整数配置
        
        Args:
            value_str: 配置值字符串
            name: 配置名称
            
        Returns:
            验证后的正整数
            
        Raises:
            ConfigurationError: 配置值无效
        """
        try:
            value = int(value_str)
        except ValueError:
            raise ConfigurationError(f"{name} 必须是整数: {value_str}")
        
        if value <= 0:
            raise ConfigurationError(f"{name} 必须是正整数: {value}")
        
        return value
    
    def _validate_database_config(self) -> None:
        """
        验证数据库配置完整性
        
        Raises:
            ConfigurationError: 数据库配置无效
        """
        if not self.POSTGRES_URI:
            raise ConfigurationError(
                "使用 PostgreSQL 时必须提供 POSTGRES_URI 环境变量"
            )
        
        # 基本的 URI 格式验证
        if not self.POSTGRES_URI.startswith(('postgresql://', 'postgres://')):
            raise ConfigurationError(
                "POSTGRES_URI 必须以 'postgresql://' 或 'postgres://' 开头"
            )
    
    def _log_configuration(self) -> None:
        """记录配置值（排除敏感信息）"""
        logger = self._get_logger()
        
        # 只在 DEBUG 级别记录配置
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("=== 应用配置 ===")
            logger.debug(f"DEBUG: {self.DEBUG}")
            logger.debug(f"HOST: {self.HOST}")
            logger.debug(f"PORT: {self.PORT}")
            logger.debug("DATABASE: postgresql")
            logger.debug("POSTGRES_URI: [已配置，已隐藏]")
            
            logger.debug(f"MARKET_CACHE_DURATION: {self.MARKET_CACHE_DURATION}")
            logger.debug(f"MARKET_API_URL: {self.MARKET_API_URL}")
            logger.debug(f"MARKET_HISTORY_ENABLED: {self.MARKET_HISTORY_ENABLED}")
            logger.debug(f"MARKET_HISTORY_INTERVAL: {self.MARKET_HISTORY_INTERVAL}")
            logger.debug(f"MARKET_HISTORY_RESOLUTION: {self.MARKET_HISTORY_RESOLUTION}")
            logger.debug(f"MARKET_HISTORY_MAX_POINTS: {self.MARKET_HISTORY_MAX_POINTS}")
            logger.debug(f"MARKET_HISTORY_CACHE_TTL: {self.MARKET_HISTORY_CACHE_TTL}")
            logger.debug(f"DEFAULT_COINS: {', '.join(self.DEFAULT_COINS)}")
            logger.debug(f"AUTO_TRADING: {self.AUTO_TRADING}")
            logger.debug(f"TRADING_MAX_CONCURRENCY: {self.TRADING_MAX_CONCURRENCY}")
            logger.debug(f"MODEL_CYCLE_TIMEOUT: {self.MODEL_CYCLE_TIMEOUT}")
            logger.debug(f"LOG_LEVEL: {self.LOG_LEVEL}")
            logger.debug("===================")
    
