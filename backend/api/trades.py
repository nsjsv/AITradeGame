"""Trade and Portfolio API endpoints."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Query

from backend.api.dependencies import ContainerDep
from backend.api.responses import success_response
from backend.config import error_types
from backend.utils.errors import NotFoundError, ValidationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["trades"])


@router.get("/models/{model_id}/portfolio")
def get_portfolio(model_id: int, container=ContainerDep):
    """Get portfolio for specific model."""
    db = container.db
    market_service = container.market_service

    # Verify model exists
    model = db.get_model(model_id)
    if not model:
        raise NotFoundError(
            f"模型 ID {model_id} 不存在",
            details={"model_id": model_id}
        )

    prices_data = market_service.get_current_prices()
    current_prices = {coin: prices_data[coin]["price"] for coin in prices_data}

    portfolio = db.get_portfolio(model_id, current_prices)
    account_value = db.get_account_value_history(model_id, limit=100)

    return success_response(
        {"portfolio": portfolio, "account_value_history": account_value}
    )


@router.get("/models/{model_id}/trades")
def get_trades(model_id: int, limit: int = Query(50, ge=1), container=ContainerDep):
    """Get trades for specific model."""
    db = container.db
    
    # Verify model exists
    model = db.get_model(model_id)
    if not model:
        raise NotFoundError(
            f"模型 ID {model_id} 不存在",
            details={"model_id": model_id}
        )
    
    trades = db.get_trades(model_id, limit=limit)
    return success_response(trades)


@router.get("/models/{model_id}/conversations")
def get_conversations(
    model_id: int, limit: int = Query(20, ge=1), container=ContainerDep
):
    """Get conversations for specific model."""
    db = container.db
    
    # Verify model exists
    model = db.get_model(model_id)
    if not model:
        raise NotFoundError(
            f"模型 ID {model_id} 不存在",
            details={"model_id": model_id}
        )
    
    conversations = db.get_conversations(model_id, limit=limit)
    return success_response(conversations)


@router.get("/aggregated/portfolio")
def get_aggregated_portfolio(container=ContainerDep):
    """Get aggregated portfolio data across all models."""
    portfolio_service = container.portfolio_service
    market_service = container.market_service

    prices_data = market_service.get_current_prices()
    current_prices = {coin: prices_data[coin]["price"] for coin in prices_data}

    aggregated = portfolio_service.get_aggregated_portfolio(current_prices)
    return success_response(aggregated)


@router.get("/models/chart-data")
def get_models_chart_data(limit: int = Query(100, ge=1), container=ContainerDep):
    """Get chart data for all models."""
    db = container.db
    chart_data = db.get_multi_model_chart_data(limit=limit)
    return success_response(chart_data)


@router.get("/leaderboard")
def get_leaderboard(container=ContainerDep):
    """Get model leaderboard sorted by returns."""
    portfolio_service = container.portfolio_service
    market_service = container.market_service

    prices_data = market_service.get_current_prices()
    current_prices = {coin: prices_data[coin]["price"] for coin in prices_data}

    leaderboard = portfolio_service.calculate_leaderboard(current_prices)
    return success_response(leaderboard)
