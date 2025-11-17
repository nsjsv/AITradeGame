"""Formatting utility functions"""


def format_price(price: float) -> str:
    """
    Format price as currency string
    
    Args:
        price: Price value to format
        
    Returns:
        Formatted price string with $ symbol and 2 decimal places
    """
    return f"${price:.2f}"


def format_percentage(value: float) -> str:
    """
    Format value as percentage string
    
    Args:
        value: Percentage value to format
        
    Returns:
        Formatted percentage string with + or - sign and 2 decimal places
    """
    return f"{value:+.2f}%"


def format_quantity(quantity: float, decimals: int = 8) -> str:
    """
    Format quantity with specified decimal places
    
    Args:
        quantity: Quantity value to format
        decimals: Number of decimal places (default: 8)
        
    Returns:
        Formatted quantity string
    """
    return f"{quantity:.{decimals}f}".rstrip('0').rstrip('.')


def format_leverage(leverage: int) -> str:
    """
    Format leverage value
    
    Args:
        leverage: Leverage multiplier
        
    Returns:
        Formatted leverage string (e.g., "10x")
    """
    return f"{leverage}x"
