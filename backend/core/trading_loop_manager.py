"""交易循环管理器模块

管理自动交易循环的生命周期，包括启动、停止和优雅关闭
"""

import threading
import time
import logging
from datetime import datetime
from typing import Optional

from backend.data.database import DatabaseInterface
from backend.services.trading_service import TradingService
from backend.config.constants import (
    TIMEOUT_GRACEFUL_SHUTDOWN,
    RETRY_INITIAL_DELAY,
    RETRY_MAX_DELAY,
    RETRY_BACKOFF_FACTOR,
    TRADING_LOOP_IDLE_SLEEP,
    DEFAULT_TRADING_FREQUENCY_MINUTES,
    LOG_MSG_TRADING_LOOP_START,
    LOG_MSG_TRADING_LOOP_STOP,
    LOG_MSG_CYCLE_START,
    LOG_MSG_CYCLE_COMPLETE,
    LOG_MSG_MODEL_EXEC,
    LOG_MSG_MODEL_SUCCESS,
    LOG_MSG_MODEL_FAILED,
    LOG_MSG_TRADE_EXECUTED,
    ERROR_MSG_TRADING_LOOP_ERROR,
)


class TradingLoopManager:
    """管理自动交易循环的生命周期
    
    使用 threading.Event 实现优雅关闭，支持指数退避重试机制
    """
    
    def __init__(self, trading_service: TradingService, db: DatabaseInterface):
        """初始化交易循环管理器
        
        Args:
            trading_service: 交易服务实例
            db: 数据库接口实例
        """
        self.trading_service = trading_service
        self.db = db
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._logger = logging.getLogger(__name__)
        self._retry_delay = RETRY_INITIAL_DELAY
    
    def start(self) -> None:
        """启动交易循环
        
        在后台线程中启动交易循环。如果循环已在运行，则不执行任何操作。
        """
        if self.is_running():
            self._logger.warning("交易循环已在运行")
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            name="TradingLoopThread",
            daemon=True
        )
        self._thread.start()
        self._logger.info(LOG_MSG_TRADING_LOOP_START)
    
    def stop(self, timeout: float = TIMEOUT_GRACEFUL_SHUTDOWN) -> bool:
        """停止交易循环
        
        发送停止信号并等待循环优雅退出
        
        Args:
            timeout: 等待停止的超时时间（秒）
            
        Returns:
            True 如果成功停止，False 如果超时
        """
        if not self.is_running():
            self._logger.warning("交易循环未运行")
            return True
        
        self._logger.info("正在停止交易循环...")
        self._stop_event.set()
        
        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                self._logger.error(f"交易循环未在 {timeout} 秒内停止")
                return False
        
        self._logger.info(LOG_MSG_TRADING_LOOP_STOP)
        return True
    
    def is_running(self) -> bool:
        """检查交易循环是否正在运行
        
        Returns:
            True 如果循环正在运行，否则 False
        """
        return self._thread is not None and self._thread.is_alive()
    
    def _run_loop(self) -> None:
        """交易循环的主逻辑（私有方法）
        
        持续运行直到收到停止信号。使用 Event.wait() 替代 time.sleep()
        以实现更快的响应停止信号。
        """
        self._logger.info("交易循环线程已启动")
        
        while not self._stop_event.is_set():
            try:
                # 检查是否有活动的交易引擎
                if not self.trading_service.engines:
                    self._logger.debug(f"无活动模型，睡眠 {TRADING_LOOP_IDLE_SLEEP} 秒")
                    if self._stop_event.wait(timeout=TRADING_LOOP_IDLE_SLEEP):
                        break
                    continue
                
                # 执行交易周期
                self._execute_cycle()
                
                # 成功执行后重置重试延迟
                self._reset_retry_delay()
                
                # 获取交易间隔并睡眠
                settings = self.db.get_settings()
                interval_minutes = max(
                    settings.get('trading_frequency_minutes', DEFAULT_TRADING_FREQUENCY_MINUTES),
                    1
                )
                sleep_seconds = interval_minutes * 60
                
                self._logger.info(f"等待 {sleep_seconds} 秒进行下一个周期")
                
                # 使用 Event.wait() 以便能快速响应停止信号
                if self._stop_event.wait(timeout=sleep_seconds):
                    break
                
            except Exception as e:
                self._logger.error(
                    f"{ERROR_MSG_TRADING_LOOP_ERROR}: {e}",
                    exc_info=True
                )
                
                # 计算退避延迟
                backoff_delay = self._calculate_backoff_delay()
                self._logger.warning(f"将在 {backoff_delay} 秒后重试")
                
                # 使用退避延迟等待
                if self._stop_event.wait(timeout=backoff_delay):
                    break
        
        self._logger.info("交易循环线程已退出")
    
    def _execute_cycle(self) -> None:
        """执行单个交易周期（私有方法）
        
        遍历所有活动的交易引擎并执行交易周期
        """
        self._logger.info("=" * 60)
        self._logger.info(f"{LOG_MSG_CYCLE_START} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._logger.info(f"活动模型数: {len(self.trading_service.engines)}")
        self._logger.info("=" * 60)
        
        # 执行每个模型的交易周期
        for model_id, engine in list(self.trading_service.engines.items()):
            # 检查是否收到停止信号
            if self._stop_event.is_set():
                self._logger.info("收到停止信号，中断交易周期")
                break
            
            try:
                self._logger.info(LOG_MSG_MODEL_EXEC.format(model_id=model_id))
                result = engine.execute_trading_cycle()
                
                if result.get('success'):
                    self._logger.info(LOG_MSG_MODEL_SUCCESS.format(model_id=model_id))
                    
                    # 记录交易执行结果
                    if result.get('executions'):
                        for exec_result in result['executions']:
                            signal = exec_result.get('signal', 'unknown')
                            coin = exec_result.get('coin', 'unknown')
                            msg = exec_result.get('message', '')
                            
                            if signal != 'hold':
                                self._logger.info(
                                    LOG_MSG_TRADE_EXECUTED.format(
                                        coin=coin,
                                        message=msg
                                    )
                                )
                else:
                    error = result.get('error', 'Unknown error')
                    self._logger.warning(
                        LOG_MSG_MODEL_FAILED.format(
                            model_id=model_id,
                            error=error
                        )
                    )
                    
            except Exception as e:
                self._logger.error(
                    LOG_MSG_MODEL_FAILED.format(
                        model_id=model_id,
                        error=str(e)
                    ),
                    exc_info=True
                )
                continue
        
        self._logger.info("=" * 60)
        self._logger.info(LOG_MSG_CYCLE_COMPLETE)
        self._logger.info("=" * 60)
    
    def _calculate_backoff_delay(self) -> float:
        """计算指数退避延迟（私有方法）
        
        使用指数退避算法计算下次重试的延迟时间
        
        Returns:
            延迟时间（秒），最大不超过 RETRY_MAX_DELAY
        """
        delay = min(self._retry_delay, RETRY_MAX_DELAY)
        self._retry_delay *= RETRY_BACKOFF_FACTOR
        return delay
    
    def _reset_retry_delay(self) -> None:
        """重置重试延迟（私有方法）
        
        在成功执行周期后重置重试延迟到初始值
        """
        self._retry_delay = RETRY_INITIAL_DELAY
