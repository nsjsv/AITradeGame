"""Trading Model data model."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class TradingModel:
    """Trading Model data model representing an AI trading agent instance.
    
    Attributes:
        id: Unique identifier for the trading model
        name: Display name of the trading model
        provider_id: Foreign key reference to the provider
        model_name: Name of the AI model to use
        initial_capital: Starting capital amount
        created_at: Timestamp when the model was created
    """
    id: Optional[int]
    name: str
    provider_id: int
    model_name: str
    initial_capital: float
    created_at: Optional[str] = None
