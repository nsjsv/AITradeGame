"""Market Data API endpoints powered by FastAPI."""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend.api.dependencies import ConfigDep, ContainerDep
from backend.api.responses import error_response, success_response
from backend.config import error_types
from backend.config.constants import HISTORY_DEFAULT_LIMIT, HISTORY_MAX_LIMIT

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/prices")
def get_market_prices(container=ContainerDep):
    """Get current market prices for default coins."""
    market_service = container.market_service
    prices = market_service.get_current_prices()
    return success_response(prices)


def _parse_iso_timestamp(value: Optional[str]):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except ValueError as exc:
        raise ValueError(f"Invalid ISO timestamp: {value}") from exc


@router.get("/history")
def get_market_history(
    coin: str = Query(..., description="Target coin symbol"),
    resolution: Optional[int] = None,
    limit: Optional[int] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    container=ContainerDep,
    config=ConfigDep,
):
    """Return historical price candles for a given coin."""
    if not coin:
        raise HTTPException(
            status_code=400,
            detail=error_response(
                error_types.INVALID_REQUEST,
                "coin parameter is required",
                {"parameter": "coin"}
            )
        )

    default_resolution = getattr(config, "MARKET_HISTORY_RESOLUTION", 60)
    max_points = getattr(config, "MARKET_HISTORY_MAX_POINTS", HISTORY_DEFAULT_LIMIT)

    try:
        res_value = int(resolution) if resolution is not None else default_resolution
        limit_value = int(limit) if limit is not None else max_points
        limit_value = max(1, min(limit_value, min(max_points, HISTORY_MAX_LIMIT)))
        start_dt = _parse_iso_timestamp(start) if start else None
        end_dt = _parse_iso_timestamp(end) if end else None
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=error_response(
                error_types.INVALID_VALUE,
                str(exc)
            )
        )

    history_service = container.market_history_service
    data = history_service.fetch_history(
        coin=coin,
        resolution=res_value,
        limit=limit_value,
        start=start_dt,
        end=end_dt,
    )

    return success_response(
        {
            "coin": coin.upper(),
            "resolution": res_value,
            "limit": limit_value,
            "records": data,
        }
    )
