"""服务容器模块

提供依赖注入容器，管理应用程序服务的生命周期。
"""

import logging
from typing import Optional

from backend.config.settings import Config
from backend.config.constants import (
    LOG_MSG_SERVICES_INIT,
    LOG_MSG_SERVICES_READY,
)
from backend.data.database import DatabaseInterface
from backend.data.market_data import MarketDataFetcher
from backend.services.trading_service import TradingService
from backend.services.portfolio_service import PortfolioService
from backend.services.market_service import MarketService
from backend.services.market_history import MarketHistoryService, MarketHistoryCollector

try:
    from backend.data.postgres_db import PostgreSQLDatabase
except ImportError:  # pragma: no cover - optional dependency
    PostgreSQLDatabase = None  # type: ignore[assignment]


class ServiceContainer:
    """服务容器，管理应用程序服务的生命周期
    
    该类负责初始化和管理所有应用程序服务，包括数据库、市场数据获取器
    和各种业务服务。它提供统一的服务访问接口，并确保资源的正确清理。
    
    Attributes:
        config: 应用配置对象
        _db: 数据库接口实例
        _market_fetcher: 市场数据获取器实例
        _trading_service: 交易服务实例
        _portfolio_service: 投资组合服务实例
        _market_service: 市场服务实例
        _logger: 日志记录器
        _initialized: 初始化状态标志
    """
    
    def __init__(self, config: Config):
        """初始化服务容器
        
        Args:
            config: 应用配置对象
        """
        self.config = config
        self._db: Optional[DatabaseInterface] = None
        self._market_fetcher: Optional[MarketDataFetcher] = None
        self._trading_service: Optional[TradingService] = None
        self._portfolio_service: Optional[PortfolioService] = None
        self._market_service: Optional[MarketService] = None
        self._history_service: Optional[MarketHistoryService] = None
        self._history_collector: Optional[MarketHistoryCollector] = None
        self._logger = logging.getLogger(__name__)
        self._initialized = False
    
    def initialize(self) -> None:
        """初始化所有服务
        
        按照依赖顺序初始化所有服务：
        1. 数据库
        2. 市场数据获取器
        3. 业务服务（交易、投资组合、市场）
        
        Raises:
            RuntimeError: 如果初始化失败或已经初始化过
        """
        if self._initialized:
            self._logger.warning("服务容器已经初始化，跳过重复初始化")
            return
        
        self._logger.info(LOG_MSG_SERVICES_INIT)
        
        try:
            # 1. 初始化数据库
            self._initialize_database()
            
            # 2. 初始化市场数据获取器
            self._initialize_market_fetcher()
            
            # 3. 初始化业务服务
            self._initialize_services()

            # 4. 初始化市场历史支持
            self._initialize_history_support()
            
            self._initialized = True
            self._logger.info(LOG_MSG_SERVICES_READY)
            
        except Exception as e:
            self._logger.error(f"服务初始化失败: {e}", exc_info=True)
            # 清理已初始化的资源
            self.cleanup()
            raise RuntimeError(f"服务容器初始化失败: {e}") from e
    
    def _initialize_database(self) -> None:
        """初始化数据库（当前仅支持 PostgreSQL）"""
        self._logger.debug("初始化数据库，类型: postgresql")
        
        if PostgreSQLDatabase is None:
            raise RuntimeError("PostgreSQL 支持需要安装 psycopg 依赖")
        if not self.config.POSTGRES_URI:
            raise RuntimeError("使用 PostgreSQL 时必须设置 POSTGRES_URI")
        self._db = PostgreSQLDatabase(self.config.POSTGRES_URI)
        
        # 初始化数据库表结构
        self._db.init_db()
        self._logger.info("数据库初始化完成，使用 postgresql")
    
    def _initialize_market_fetcher(self) -> None:
        """初始化市场数据获取器"""
        self._logger.debug("初始化市场数据获取器")
        
        self._market_fetcher = MarketDataFetcher(
            api_url=self.config.MARKET_API_URL,
            cache_duration=self.config.MARKET_CACHE_DURATION
        )
        
        self._logger.debug("市场数据获取器初始化完成")
    
    def _initialize_services(self) -> None:
        """初始化业务服务
        
        初始化交易服务、投资组合服务和市场服务
        """
        self._logger.debug("初始化业务服务")
        
        # 交易服务
        self._trading_service = TradingService(
            db=self._db,
            market_fetcher=self._market_fetcher
        )
        
        # 投资组合服务
        self._portfolio_service = PortfolioService(db=self._db)
        
        # 市场服务
        self._market_service = MarketService(
            market_fetcher=self._market_fetcher,
            default_coins=self.config.DEFAULT_COINS
        )
        
        self._logger.debug("业务服务初始化完成")

    def _initialize_history_support(self) -> None:
        """Initialize market history services and collectors."""
        self._history_service = MarketHistoryService(
            db=self._db,
            cache_ttl=self.config.MARKET_HISTORY_CACHE_TTL,
        )
        if self.config.MARKET_HISTORY_ENABLED:
            self._history_collector = MarketHistoryCollector(
                db=self._db,
                market_fetcher=self._market_fetcher,
                coins=self.config.DEFAULT_COINS,
                interval=self.config.MARKET_HISTORY_INTERVAL,
                resolution=self.config.MARKET_HISTORY_RESOLUTION,
            )
            self._history_collector.start()
    
    def cleanup(self) -> None:
        """清理所有服务资源
        
        按照与初始化相反的顺序清理资源，确保依赖关系正确处理。
        该方法是幂等的，可以安全地多次调用。
        """
        if not self._initialized:
            self._logger.debug("服务容器未初始化，无需清理")
            return
        
        self._logger.info("正在清理服务资源...")
        
        # 清理服务（按照与初始化相反的顺序）
        if self._history_collector is not None:
            try:
                self._history_collector.stop()
            except Exception as e:
                self._logger.error(f"停止市场历史采集器失败: {e}", exc_info=True)
            finally:
                self._history_collector = None
        self._history_service = None
        self._market_service = None
        self._portfolio_service = None
        self._trading_service = None
        self._market_fetcher = None
        
        # 清理数据库连接
        if self._db is not None:
            try:
                self._db.close()
                self._logger.debug("数据库连接已关闭")
            except Exception as e:
                self._logger.error(f"关闭数据库连接时出错: {e}", exc_info=True)
            finally:
                self._db = None
        
        self._initialized = False
        self._logger.info("服务资源清理完成")
    
    @property
    def db(self) -> DatabaseInterface:
        """获取数据库实例
        
        Returns:
            数据库接口实例
            
        Raises:
            RuntimeError: 如果服务容器未初始化
        """
        if not self._initialized or self._db is None:
            raise RuntimeError("服务容器未初始化，请先调用 initialize()")
        return self._db
    
    @property
    def trading_service(self) -> TradingService:
        """获取交易服务实例
        
        Returns:
            交易服务实例
            
        Raises:
            RuntimeError: 如果服务容器未初始化
        """
        if not self._initialized or self._trading_service is None:
            raise RuntimeError("服务容器未初始化，请先调用 initialize()")
        return self._trading_service
    
    @property
    def portfolio_service(self) -> PortfolioService:
        """获取投资组合服务实例
        
        Returns:
            投资组合服务实例
            
        Raises:
            RuntimeError: 如果服务容器未初始化
        """
        if not self._initialized or self._portfolio_service is None:
            raise RuntimeError("服务容器未初始化，请先调用 initialize()")
        return self._portfolio_service

    @property
    def market_history_service(self) -> MarketHistoryService:
        """Get market history service instance."""
        if not self._initialized or self._history_service is None:
            raise RuntimeError("服务容器未初始化，请先调用 initialize()")
        return self._history_service
    
    @property
    def market_service(self) -> MarketService:
        """获取市场服务实例
        
        Returns:
            市场服务实例
            
        Raises:
            RuntimeError: 如果服务容器未初始化
        """
        if not self._initialized or self._market_service is None:
            raise RuntimeError("服务容器未初始化，请先调用 initialize()")
        return self._market_service
    
    @property
    def market_fetcher(self) -> MarketDataFetcher:
        """获取市场数据获取器实例
        
        Returns:
            市场数据获取器实例
            
        Raises:
            RuntimeError: 如果服务容器未初始化
        """
        if not self._initialized or self._market_fetcher is None:
            raise RuntimeError("服务容器未初始化，请先调用 initialize()")
        return self._market_fetcher
