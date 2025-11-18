"""Trade and Portfolio API endpoints

This module handles all trade and portfolio-related API routes including:
- GET /api/models/<id>/portfolio - Get model portfolio
- GET /api/models/<id>/trades - Get model trades
- GET /api/models/<id>/conversations - Get model conversations
- GET /api/aggregated/portfolio - Get aggregated portfolio across all models
- GET /api/models/chart-data - Get chart data for all models
- GET /api/leaderboard - Get model leaderboard
"""

import logging
from flask import Blueprint, request, jsonify, g

logger = logging.getLogger(__name__)
trades_bp = Blueprint('trades', __name__)


@trades_bp.route('/api/models/<int:model_id>/portfolio', methods=['GET'])
def get_portfolio(model_id):
    """Get portfolio for specific model"""
    db = g.container.db
    market_service = g.container.market_service
    
    # Get current prices
    prices_data = market_service.get_current_prices()
    current_prices = {coin: prices_data[coin]['price'] for coin in prices_data}
    
    # Get portfolio with prices
    portfolio = db.get_portfolio(model_id, current_prices)
    account_value = db.get_account_value_history(model_id, limit=100)
    
    return jsonify({
        'portfolio': portfolio,
        'account_value_history': account_value
    })


@trades_bp.route('/api/models/<int:model_id>/trades', methods=['GET'])
def get_trades(model_id):
    """Get trades for specific model"""
    db = g.container.db
    limit = request.args.get('limit', 50, type=int)
    trades = db.get_trades(model_id, limit=limit)
    return jsonify(trades)


@trades_bp.route('/api/models/<int:model_id>/conversations', methods=['GET'])
def get_conversations(model_id):
    """Get conversations for specific model"""
    db = g.container.db
    limit = request.args.get('limit', 20, type=int)
    conversations = db.get_conversations(model_id, limit=limit)
    return jsonify(conversations)


@trades_bp.route('/api/aggregated/portfolio', methods=['GET'])
def get_aggregated_portfolio():
    """Get aggregated portfolio data across all models"""
    db = g.container.db
    portfolio_service = g.container.portfolio_service
    market_service = g.container.market_service
    
    # Get current prices
    prices_data = market_service.get_current_prices()
    current_prices = {coin: prices_data[coin]['price'] for coin in prices_data}
    
    # Get aggregated portfolio
    aggregated = portfolio_service.get_aggregated_portfolio(current_prices)
    
    return jsonify(aggregated)


@trades_bp.route('/api/models/chart-data', methods=['GET'])
def get_models_chart_data():
    """Get chart data for all models"""
    db = g.container.db
    limit = request.args.get('limit', 100, type=int)
    chart_data = db.get_multi_model_chart_data(limit=limit)
    return jsonify(chart_data)


@trades_bp.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get model leaderboard sorted by returns"""
    portfolio_service = g.container.portfolio_service
    market_service = g.container.market_service
    
    # Get current prices
    prices_data = market_service.get_current_prices()
    current_prices = {coin: prices_data[coin]['price'] for coin in prices_data}
    
    # Calculate leaderboard
    leaderboard = portfolio_service.calculate_leaderboard(current_prices)
    
    return jsonify(leaderboard)
