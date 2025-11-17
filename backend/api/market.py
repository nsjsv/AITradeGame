"""Market Data API endpoints

This module handles all market data-related API routes including:
- GET /api/market/prices - Get current market prices
"""

from flask import Blueprint, jsonify, current_app

market_bp = Blueprint('market', __name__, url_prefix='/api/market')


@market_bp.route('/prices', methods=['GET'])
def get_market_prices():
    """Get current market prices for default coins"""
    market_service = current_app.config['market_service']
    
    # Get current prices for default coins
    prices = market_service.get_current_prices()
    
    return jsonify(prices)
