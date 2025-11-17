"""Portfolio data model."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Portfolio:
    """Portfolio data model representing a position in a trading model.
    
    Attributes:
        id: Unique identifier for the portfolio entry
        model_id: Foreign key reference to the trading model
        coin: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        quantity: Amount of the coin held
        avg_price: Average purchase price
        leverage: Leverage multiplier (1-20)
        side: Position direction ('long' or 'short')
        updated_at: Timestamp when the portfolio was last updated
    """
    id: Optional[int]
    model_id: int
    coin: str
    quantity: float
    avg_price: float
    leverage: int
    side: str
    updated_at: Optional[str] = None
