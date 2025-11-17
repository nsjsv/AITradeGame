"""交易服务模块

封装交易引擎管理和交易周期执行逻辑
"""

from typing import Dict
from backend.data.database import DatabaseInterface
from backend.data.market_data import MarketDataFetcher
from backend.core.trading_engine import TradingEngine
from backend.core.ai_trader import AITrader
from backend.config.constants import DEFAULT_TRADE_FEE_RATE


class TradingService:
    """交易服务
    
    管理交易引擎实例，协调交易周期执行
    """
    
    def __init__(self, db: DatabaseInterface, market_fetcher: MarketDataFetcher):
        """初始化交易服务
        
        Args:
            db: 数据库接口实例
            market_fetcher: 市场数据获取器实例
        """
        self.db = db
        self.market_fetcher = market_fetcher
        self.engines = {}  # model_id -> TradingEngine
        self.trade_fee_rate = DEFAULT_TRADE_FEE_RATE
    
    def initialize_engines(self, trade_fee_rate: float) -> None:
        """初始化所有交易引擎
        
        从数据库加载所有模型并创建对应的交易引擎实例
        
        Args:
            trade_fee_rate: 交易费率
        """
        try:
            self.trade_fee_rate = trade_fee_rate
            models = self.db.get_all_models()
            
            if not models:
                print("[WARN] No trading models found")
                return
            
            print(f"\n[INIT] Initializing trading engines...")
            for model in models:
                model_id = model['id']
                model_name = model['name']
                
                try:
                    # 获取 Provider 信息
                    provider = self.db.get_provider(model['provider_id'])
                    if not provider:
                        print(f"  [WARN] Model {model_id} ({model_name}): Provider not found")
                        continue
                    
                    # 创建交易引擎
                    self.engines[model_id] = TradingEngine(
                        model_id=model_id,
                        db=self.db,
                        market_fetcher=self.market_fetcher,
                        ai_trader=AITrader(
                            api_key=provider['api_key'],
                            api_url=provider['api_url'],
                            model_name=model['model_name']
                        ),
                        trade_fee_rate=self.trade_fee_rate
                    )
                    print(f"  [OK] Model {model_id} ({model_name})")
                except Exception as e:
                    print(f"  [ERROR] Model {model_id} ({model_name}): {e}")
                    continue
            
            print(f"[INFO] Initialized {len(self.engines)} engine(s)\n")
            
        except Exception as e:
            print(f"[ERROR] Init engines failed: {e}\n")
    
    def execute_trading_cycle(self, model_id: int) -> Dict:
        """执行交易周期
        
        执行指定模型的一次完整交易周期
        
        Args:
            model_id: 模型 ID
            
        Returns:
            包含执行结果的字典
        """
        engine = self.get_or_create_engine(model_id)
        if not engine:
            return {
                'success': False,
                'error': 'Failed to get or create trading engine'
            }
        
        try:
            result = engine.execute_trading_cycle()
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_or_create_engine(self, model_id: int) -> TradingEngine:
        """获取或创建交易引擎
        
        如果引擎已存在则返回，否则创建新引擎
        
        Args:
            model_id: 模型 ID
            
        Returns:
            交易引擎实例，如果创建失败则返回 None
        """
        # 如果引擎已存在，直接返回
        if model_id in self.engines:
            return self.engines[model_id]
        
        # 创建新引擎
        try:
            model = self.db.get_model(model_id)
            if not model:
                print(f"[ERROR] Model {model_id} not found")
                return None
            
            # 获取 Provider 信息
            provider = self.db.get_provider(model['provider_id'])
            if not provider:
                print(f"[ERROR] Provider not found for model {model_id}")
                return None
            
            # 创建交易引擎（使用默认费率）
            self.engines[model_id] = TradingEngine(
                model_id=model_id,
                db=self.db,
                market_fetcher=self.market_fetcher,
                ai_trader=AITrader(
                    api_key=provider['api_key'],
                    api_url=provider['api_url'],
                    model_name=model['model_name']
                ),
                trade_fee_rate=self.trade_fee_rate
            )
            
            print(f"[INFO] Created trading engine for model {model_id}")
            return self.engines[model_id]
            
        except Exception as e:
            print(f"[ERROR] Failed to create engine for model {model_id}: {e}")
            return None

    def update_trade_fee_rate(self, trade_fee_rate: float) -> None:
        """Update trade fee rate for all managed engines"""
        self.trade_fee_rate = trade_fee_rate

        for engine in self.engines.values():
            engine.trade_fee_rate = trade_fee_rate
