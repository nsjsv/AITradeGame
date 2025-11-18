"""
Database interface module - Abstract base class for database operations.

The project now relies exclusively on PostgreSQL for persistence, but this
interface keeps higher layers decoupled from the concrete database backend.
Any future storage engine must implement this interface so the services can
remain database-agnostic.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional


class DatabaseInterface(ABC):
    """Abstract database interface for database-agnostic operations"""
    
    @abstractmethod
    def get_connection(self):
        """Get database connection"""
        pass
    
    @abstractmethod
    def init_db(self) -> None:
        """Initialize database tables"""
        pass
    
    # ============ Provider Management ============
    
    @abstractmethod
    def add_provider(self, name: str, api_url: str, api_key: str, models: str = '') -> int:
        """Add new API provider"""
        pass
    
    @abstractmethod
    def get_provider(self, provider_id: int) -> Optional[Dict]:
        """Get provider information"""
        pass
    
    @abstractmethod
    def get_all_providers(self) -> List[Dict]:
        """Get all API providers"""
        pass
    
    @abstractmethod
    def delete_provider(self, provider_id: int) -> None:
        """Delete provider"""
        pass
    
    @abstractmethod
    def update_provider(self, provider_id: int, name: str, api_url: str, 
                       api_key: str, models: str) -> None:
        """Update provider information"""
        pass
    
    # ============ Model Management ============
    
    @abstractmethod
    def add_model(self, name: str, provider_id: int, model_name: str, 
                 initial_capital: float = 10000) -> int:
        """Add new trading model"""
        pass
    
    @abstractmethod
    def get_model(self, model_id: int) -> Optional[Dict]:
        """Get model information"""
        pass
    
    @abstractmethod
    def get_all_models(self) -> List[Dict]:
        """Get all trading models"""
        pass
    
    @abstractmethod
    def delete_model(self, model_id: int) -> None:
        """Delete model and related data"""
        pass
    
    # ============ Portfolio Management ============
    
    @abstractmethod
    def update_position(self, model_id: int, coin: str, quantity: float, 
                       avg_price: float, leverage: int = 1, side: str = 'long') -> None:
        """Update position"""
        pass
    
    @abstractmethod
    def get_portfolio(self, model_id: int, current_prices: Dict = None) -> Dict:
        """Get portfolio with positions and P&L"""
        pass
    
    @abstractmethod
    def close_position(self, model_id: int, coin: str, side: str = 'long') -> None:
        """Close position"""
        pass
    
    # ============ Trade Records ============
    
    @abstractmethod
    def add_trade(self, model_id: int, coin: str, signal: str, quantity: float,
                 price: float, leverage: int = 1, side: str = 'long', 
                 pnl: float = 0, fee: float = 0) -> None:
        """Add trade record with fee"""
        pass
    
    @abstractmethod
    def get_trades(self, model_id: int, limit: int = 50) -> List[Dict]:
        """Get trade history"""
        pass
    
    # ============ Conversation History ============
    
    @abstractmethod
    def add_conversation(self, model_id: int, user_prompt: str, 
                        ai_response: str, cot_trace: str = '') -> None:
        """Add conversation record"""
        pass
    
    @abstractmethod
    def get_conversations(self, model_id: int, limit: int = 20) -> List[Dict]:
        """Get conversation history"""
        pass
    
    # ============ Account Value History ============
    
    @abstractmethod
    def record_account_value(self, model_id: int, total_value: float, 
                            cash: float, positions_value: float) -> None:
        """Record account value snapshot"""
        pass
    
    @abstractmethod
    def get_account_value_history(self, model_id: int, limit: int = 100) -> List[Dict]:
        """Get account value history"""
        pass
    
    @abstractmethod
    def get_aggregated_account_value_history(self, limit: int = 100) -> List[Dict]:
        """Get aggregated account value history across all models"""
        pass
    
    @abstractmethod
    def get_multi_model_chart_data(self, limit: int = 100) -> List[Dict]:
        """Get chart data for all models to display in multi-line chart"""
        pass

    # ============ Market History ============
    
    @abstractmethod
    def record_market_prices(self, rows: List[Dict]) -> None:
        """Persist market prices"""
        pass
    
    @abstractmethod
    def get_market_history(self, coin: str, resolution: int, limit: int = 500,
                          start: Optional[datetime] = None,
                          end: Optional[datetime] = None) -> List[Dict]:
        """Fetch market history data"""
        pass
    
    # ============ Settings Management ============
    
    @abstractmethod
    def get_settings(self) -> Dict:
        """Get system settings"""
        pass
    
    @abstractmethod
    def update_settings(self, trading_frequency_minutes: int,
                       trading_fee_rate: float,
                       market_refresh_interval: int,
                       portfolio_refresh_interval: int) -> bool:
        """Update system settings"""
        pass
