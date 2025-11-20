"""Shared API response helpers."""

from typing import Any, Dict, Optional


def success_response(data: Any = None, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Standardize successful API responses."""
    response: Dict[str, Any] = {"data": data}
    if meta is not None:
        response["meta"] = meta
    return response


def error_response(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Standardize error API responses.
    
    Args:
        error_type: Error type in UPPER_SNAKE_CASE format (e.g., 'INSUFFICIENT_BALANCE')
        message: Human-readable error description
        details: Optional dictionary with additional error context
    
    Returns:
        Standard error response dictionary with 'error' object
    
    Example:
        >>> error_response('INSUFFICIENT_BALANCE', 'Account balance too low', {'required': 1000, 'available': 500})
        {'error': {'code': 'INSUFFICIENT_BALANCE', 'message': 'Account balance too low', 'details': {'required': 1000, 'available': 500}}}
    """
    error_obj: Dict[str, Any] = {
        "code": error_type,
        "message": message
    }
    if details is not None:
        error_obj["details"] = details
    return {"error": error_obj}
