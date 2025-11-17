"""投资组合服务模块

封装投资组合计算和聚合逻辑
"""

from typing import Dict, List
from backend.data.database import DatabaseInterface


class PortfolioService:
    """投资组合服务
    
    封装投资组合计算逻辑，包括单个模型投资组合、聚合投资组合和排行榜计算
    """
    
    def __init__(self, db: DatabaseInterface):
        """初始化投资组合服务
        
        Args:
            db: 数据库接口实例
        """
        self.db = db
    
    def get_portfolio_with_prices(self, model_id: int, current_prices: Dict) -> Dict:
        """获取带价格的投资组合
        
        Args:
            model_id: 模型 ID
            current_prices: 当前价格字典 {coin: price}
            
        Returns:
            包含投资组合详情和账户价值历史的字典
        """
        portfolio = self.db.get_portfolio(model_id, current_prices)
        account_value = self.db.get_account_value_history(model_id, limit=100)
        
        return {
            'portfolio': portfolio,
            'account_value_history': account_value
        }
    
    def get_aggregated_portfolio(self, current_prices: Dict) -> Dict:
        """获取聚合投资组合
        
        聚合所有模型的投资组合数据，计算总体表现
        
        Args:
            current_prices: 当前价格字典 {coin: price}
            
        Returns:
            包含聚合投资组合、图表数据和模型数量的字典
        """
        models = self.db.get_all_models()
        
        # 初始化聚合数据
        total_portfolio = {
            'total_value': 0,
            'cash': 0,
            'positions_value': 0,
            'realized_pnl': 0,
            'unrealized_pnl': 0,
            'initial_capital': 0,
            'positions': []
        }
        
        all_positions = {}
        
        # 聚合所有模型的投资组合
        for model in models:
            portfolio = self.db.get_portfolio(model['id'], current_prices)
            if portfolio:
                total_portfolio['total_value'] += portfolio.get('total_value', 0)
                total_portfolio['cash'] += portfolio.get('cash', 0)
                total_portfolio['positions_value'] += portfolio.get('positions_value', 0)
                total_portfolio['realized_pnl'] += portfolio.get('realized_pnl', 0)
                total_portfolio['unrealized_pnl'] += portfolio.get('unrealized_pnl', 0)
                total_portfolio['initial_capital'] += portfolio.get('initial_capital', 0)
                
                # 按币种和方向聚合持仓
                for pos in portfolio.get('positions', []):
                    key = f"{pos['coin']}_{pos['side']}"
                    if key not in all_positions:
                        all_positions[key] = {
                            'coin': pos['coin'],
                            'side': pos['side'],
                            'quantity': 0,
                            'avg_price': 0,
                            'total_cost': 0,
                            'leverage': pos['leverage'],
                            'current_price': pos['current_price'],
                            'pnl': 0
                        }
                    
                    # 加权平均计算
                    current_pos = all_positions[key]
                    current_cost = current_pos['quantity'] * current_pos['avg_price']
                    new_cost = pos['quantity'] * pos['avg_price']
                    total_quantity = current_pos['quantity'] + pos['quantity']
                    
                    if total_quantity > 0:
                        current_pos['avg_price'] = (current_cost + new_cost) / total_quantity
                        current_pos['quantity'] = total_quantity
                        current_pos['total_cost'] = current_cost + new_cost
                        current_pos['pnl'] = (pos['current_price'] - current_pos['avg_price']) * total_quantity
        
        total_portfolio['positions'] = list(all_positions.values())
        
        # 获取多模型图表数据
        chart_data = self.db.get_multi_model_chart_data(limit=100)
        
        return {
            'portfolio': total_portfolio,
            'chart_data': chart_data,
            'model_count': len(models)
        }
    
    def calculate_leaderboard(self, current_prices: Dict) -> List[Dict]:
        """计算排行榜
        
        根据收益率对所有模型进行排序
        
        Args:
            current_prices: 当前价格字典 {coin: price}
            
        Returns:
            排序后的模型列表，包含账户价值和收益率
        """
        models = self.db.get_all_models()
        leaderboard = []
        
        for model in models:
            portfolio = self.db.get_portfolio(model['id'], current_prices)
            account_value = portfolio.get('total_value', model['initial_capital'])
            returns = ((account_value - model['initial_capital']) / model['initial_capital']) * 100
            
            leaderboard.append({
                'model_id': model['id'],
                'model_name': model['name'],
                'account_value': account_value,
                'returns': returns,
                'initial_capital': model['initial_capital']
            })
        
        # 按收益率降序排序
        leaderboard.sort(key=lambda x: x['returns'], reverse=True)
        
        return leaderboard
