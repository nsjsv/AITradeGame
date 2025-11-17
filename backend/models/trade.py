"""Trade data model."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Trade:
    """Trade data model representing a single trade execution.
    
    Attributes:
        id: Unique identifier for the trade
        model_id: Foreign key reference to the trading model
        coin: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        signal: Trading signal ('buy_to_enter', 'sell_to_enter', 'close_position', 'hold')
        quantity: Amount of the coin traded
        price: Execution price
        leverage: Leverage multiplier used
        side: Position direction ('long' or 'short')
        pnl: Profit and loss from the trade
        fee: Transaction fee paid
        timestamp: Timestamp when the trade was executed
    """
    id: Optional[int]
    model_id: int
    coin: str
    signal: str
    quantity: float
    price: float
    leverage: int
    side: str
    pnl: float
    fee: float
    timestamp: Optional[str] = None
