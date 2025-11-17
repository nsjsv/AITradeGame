"""Application configuration settings"""
import os


class Config:
    """Application configuration loaded from environment variables"""
    
    # Flask configuration
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))
    
    # Database configuration
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
    SQLITE_PATH = os.getenv('SQLITE_PATH', 'AITradeGame.db')
    POSTGRES_URI = os.getenv('POSTGRES_URI', '')
    
    # Market data configuration
    MARKET_CACHE_DURATION = int(os.getenv('MARKET_CACHE_DURATION', '5'))
    MARKET_API_URL = os.getenv('MARKET_API_URL', 'https://api.coingecko.com/api/v3')
    
    # Trading coins configuration
    _coins_str = os.getenv('TRADING_COINS', 'BTC,ETH,SOL,BNB,XRP,DOGE')
    DEFAULT_COINS = [coin.strip() for coin in _coins_str.split(',') if coin.strip()]
    
    # Auto trading
    AUTO_TRADING = os.getenv('AUTO_TRADING', 'True') == 'True'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
