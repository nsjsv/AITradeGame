"""Validation utility functions"""
from backend.config.constants import MIN_LEVERAGE, MAX_LEVERAGE


def validate_quantity(quantity: float) -> bool:
    """
    Validate trading quantity
    
    Args:
        quantity: Quantity to validate
        
    Returns:
        True if quantity is valid (positive), False otherwise
    """
    return quantity > 0


def validate_leverage(leverage: int) -> bool:
    """
    Validate leverage value
    
    Args:
        leverage: Leverage multiplier to validate
        
    Returns:
        True if leverage is within valid range, False otherwise
    """
    return MIN_LEVERAGE <= leverage <= MAX_LEVERAGE


def validate_price(price: float) -> bool:
    """
    Validate price value
    
    Args:
        price: Price to validate
        
    Returns:
        True if price is valid (positive), False otherwise
    """
    return price > 0


def validate_fee_rate(fee_rate: float) -> bool:
    """
    Validate trading fee rate
    
    Args:
        fee_rate: Fee rate to validate (e.g., 0.001 for 0.1%)
        
    Returns:
        True if fee rate is valid (between 0 and 1), False otherwise
    """
    return 0 <= fee_rate < 1


def validate_coin_symbol(symbol: str) -> bool:
    """
    Validate coin symbol format
    
    Args:
        symbol: Coin symbol to validate
        
    Returns:
        True if symbol is valid (non-empty uppercase string), False otherwise
    """
    return bool(symbol) and symbol.isupper() and symbol.isalpha()
