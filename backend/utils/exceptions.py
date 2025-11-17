"""Custom exception classes"""


class AppException(Exception):
    """Base application exception"""
    
    def __init__(self, message: str, code: str = 'APP_ERROR'):
        """
        Initialize application exception
        
        Args:
            message: Error message
            code: Error code for identification
        """
        self.message = message
        self.code = code
        super().__init__(self.message)


class DatabaseException(AppException):
    """Database operation exception"""
    
    def __init__(self, message: str, code: str = 'DATABASE_ERROR'):
        super().__init__(message, code)


class TradingException(AppException):
    """Trading operation exception"""
    
    def __init__(self, message: str, code: str = 'TRADING_ERROR'):
        super().__init__(message, code)


class MarketDataException(AppException):
    """Market data fetching exception"""
    
    def __init__(self, message: str, code: str = 'MARKET_DATA_ERROR'):
        super().__init__(message, code)


class ValidationException(AppException):
    """Input validation exception"""
    
    def __init__(self, message: str, code: str = 'VALIDATION_ERROR'):
        super().__init__(message, code)


class ConfigurationException(AppException):
    """Configuration error exception"""
    
    def __init__(self, message: str, code: str = 'CONFIG_ERROR'):
        super().__init__(message, code)
