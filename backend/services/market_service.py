"""市场服务模块

封装市场数据获取和处理逻辑
"""

from typing import Dict, List, Optional
from backend.data.market_data import MarketDataFetcher


class MarketService:
    """市场服务
    
    封装市场数据相关逻辑，提供价格查询和市场状态获取功能
    """
    
    def __init__(self, market_fetcher: MarketDataFetcher, default_coins: List[str] = None):
        """初始化市场服务
        
        Args:
            market_fetcher: 市场数据获取器实例
            default_coins: 默认交易币种列表
        """
        self.market_fetcher = market_fetcher
        self.default_coins = default_coins or ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE']
    
    def get_current_prices(self, coins: Optional[List[str]] = None) -> Dict:
        """获取当前价格
        
        Args:
            coins: 币种列表，如果为 None 则使用默认币种
            
        Returns:
            包含价格信息的字典，格式: {coin: {'price': float, 'change_24h': float, ...}}
        """
        if coins is None:
            coins = self.default_coins
        
        return self.market_fetcher.get_current_prices(coins)
    
    def get_market_state(self, coins: Optional[List[str]] = None) -> Dict:
        """获取市场状态（包含技术指标）
        
        Args:
            coins: 币种列表，如果为 None 则使用默认币种
            
        Returns:
            包含市场状态和技术指标的字典
        """
        if coins is None:
            coins = self.default_coins
        
        prices_data = self.market_fetcher.get_current_prices(coins)
        
        # 构建市场状态
        market_state = {
            'timestamp': prices_data.get('timestamp') if isinstance(prices_data, dict) else None,
            'coins': {}
        }
        
        for coin in coins:
            if coin in prices_data:
                market_state['coins'][coin] = prices_data[coin]
        
        return market_state
