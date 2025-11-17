"""Provider data model."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Provider:
    """Provider data model representing an API provider configuration.
    
    Attributes:
        id: Unique identifier for the provider
        name: Display name of the provider
        api_url: Base URL for the provider's API
        api_key: Authentication key for the provider
        models: Available models (JSON string or comma-separated)
        created_at: Timestamp when the provider was created
    """
    id: Optional[int]
    name: str
    api_url: str
    api_key: str
    models: str
    created_at: Optional[str] = None
