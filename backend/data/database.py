"""
Database interface module - Abstract base class for database operations

PostgreSQL Migration Guide:
===========================

This interface is designed to be database-agnostic, allowing easy migration from SQLite to PostgreSQL.

Migration Steps:
1. Create a new file: backend/data/postgres_db.py
2. Implement PostgreSQLDatabase class that inherits from DatabaseInterface
3. Use psycopg2 or SQLAlchemy for PostgreSQL operations
4. Update main.py to select database implementation based on DATABASE_TYPE config:
   
   if config.DATABASE_TYPE == 'postgresql':
       from backend.data.postgres_db import PostgreSQLDatabase
       db = PostgreSQLDatabase(config.POSTGRES_URI)
   else:
       from backend.data.sqlite_db import SQLiteDatabase
       db = SQLiteDatabase(config.SQLITE_PATH)

5. Create PostgreSQL schema matching the SQLite structure:
   - providers table
   - trading_models table
   - portfolio table
   - trades table
   - conversations table
   - account_value_history table
   - settings table

6. Data Migration:
   - Export data from SQLite using sqlite_db.py methods
   - Transform data if needed (e.g., JSON fields, timestamps)
   - Import data into PostgreSQL using postgres_db.py methods
   - Verify data integrity

7. Key Differences to Handle:
   - SQLite uses INTEGER PRIMARY KEY AUTOINCREMENT, PostgreSQL uses SERIAL or IDENTITY
   - SQLite uses TEXT for JSON, PostgreSQL has native JSON/JSONB types
   - SQLite uses REAL for floats, PostgreSQL uses NUMERIC or DOUBLE PRECISION
   - Date/time handling: SQLite uses TEXT, PostgreSQL has TIMESTAMP types
   - Connection pooling: Use psycopg2.pool or SQLAlchemy connection pool
   - Transaction management: PostgreSQL requires explicit COMMIT/ROLLBACK

8. Testing:
   - Run all existing tests against PostgreSQL implementation
   - Verify all CRUD operations work correctly
   - Test concurrent access and connection pooling
   - Benchmark performance compared to SQLite

Example PostgreSQL Implementation:
-----------------------------------
```python
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

class PostgreSQLDatabase(DatabaseInterface):
    def __init__(self, postgres_uri: str):
        self.pool = SimpleConnectionPool(1, 20, postgres_uri)
    
    def get_connection(self):
        return self.pool.getconn()
    
    def release_connection(self, conn):
        self.pool.putconn(conn)
    
    def init_db(self):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Create tables with PostgreSQL syntax
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS providers (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        api_url TEXT NOT NULL,
                        api_key TEXT NOT NULL,
                        models TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                # ... other tables
            conn.commit()
        finally:
            self.release_connection(conn)
```
"""
from abc import ABC, abstractmethod
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
    
    # ============ Settings Management ============
    
    @abstractmethod
    def get_settings(self) -> Dict:
        """Get system settings"""
        pass
    
    @abstractmethod
    def update_settings(self, trading_frequency_minutes: int, 
                       trading_fee_rate: float) -> bool:
        """Update system settings"""
        pass
