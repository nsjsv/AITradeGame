"""Market Data API endpoints

This module handles all market data-related API routes including:
- GET /api/market/prices - Get current market prices
- GET /api/market/history - Get historical market data
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify, g, request, current_app

from backend.config.constants import (
    HISTORY_DEFAULT_LIMIT,
    HISTORY_MAX_LIMIT,
)

logger = logging.getLogger(__name__)
market_bp = Blueprint('market', __name__, url_prefix='/api/market')


@market_bp.route('/prices', methods=['GET'])
def get_market_prices():
    """Get current market prices for default coins"""
    market_service = g.container.market_service
    
    # Get current prices for default coins
    prices = market_service.get_current_prices()
    
    return jsonify(prices)


def _parse_iso_timestamp(value: str):
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


@market_bp.route('/history', methods=['GET'])
def get_market_history():
    """Return historical price candles for a given coin."""
    coin = request.args.get('coin')
    if not coin:
        return jsonify({'error': 'coin parameter is required'}), 400
    
    app_config = current_app.config.get('app_config')
    default_resolution = getattr(app_config, 'MARKET_HISTORY_RESOLUTION', 60)
    max_points = getattr(app_config, 'MARKET_HISTORY_MAX_POINTS', HISTORY_DEFAULT_LIMIT)
    
    try:
        resolution = int(request.args.get('resolution', default_resolution))
        limit = int(request.args.get('limit', max_points))
        limit = max(1, min(limit, min(max_points, HISTORY_MAX_LIMIT)))
        start_param = request.args.get('start')
        end_param = request.args.get('end')
        start_dt = _parse_iso_timestamp(start_param) if start_param else None
        end_dt = _parse_iso_timestamp(end_param) if end_param else None
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    
    history_service = g.container.market_history_service
    data = history_service.fetch_history(
        coin=coin,
        resolution=resolution,
        limit=limit,
        start=start_dt,
        end=end_dt,
    )
    
    return jsonify({
        'coin': coin.upper(),
        'resolution': resolution,
        'limit': limit,
        'records': data
    })
