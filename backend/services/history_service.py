"""Standalone market history service (HTTP API + collector)."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.api.responses import error_response, success_response
from backend.config import error_types
from backend.config.constants import HISTORY_MAX_LIMIT
from backend.config.settings import Config
from backend.data.market_data import MarketDataFetcher
from backend.data.postgres_db import PostgreSQLDatabase
from backend.services.market_history import (
    MarketHistoryCollector,
    MarketHistoryService,
)
from backend.utils.errors import register_error_handlers

logger = logging.getLogger(__name__)


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Invalid ISO timestamp: {value}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt


def create_app(config: Optional[Config] = None) -> FastAPI:
    """Create FastAPI app for history service."""
    config = config or Config()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db = PostgreSQLDatabase(config.POSTGRES_URI)
        db.init_db()

        market_fetcher = MarketDataFetcher(
            api_url=config.MARKET_API_URL,
            cache_duration=config.MARKET_CACHE_DURATION,
        )

        history_service = MarketHistoryService(
            db=db,
            cache_ttl=config.MARKET_HISTORY_CACHE_TTL,
        )
        collector: Optional[MarketHistoryCollector] = None
        if config.MARKET_HISTORY_ENABLED:
            collector = MarketHistoryCollector(
                db=db,
                market_fetcher=market_fetcher,
                coins=config.DEFAULT_COINS,
                interval=config.MARKET_HISTORY_INTERVAL,
                resolution=config.MARKET_HISTORY_RESOLUTION,
            )
            collector.start()

        app.state.db = db
        app.state.market_fetcher = market_fetcher
        app.state.history_service = history_service
        app.state.collector = collector

        try:
            yield
        finally:
            collector_ref: Optional[MarketHistoryCollector] = getattr(app.state, "collector", None)
            if collector_ref:
                try:
                    collector_ref.stop()
                except Exception:
                    logger.warning("Failed to stop history collector", exc_info=True)

            if hasattr(db, "close"):
                try:
                    db.close()
                except Exception:
                    logger.warning("Failed to close database", exc_info=True)

    app = FastAPI(title="AITradeGame History Service", lifespan=lifespan)
    register_error_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health(request: Request):
        ts = datetime.now(timezone.utc).isoformat()
        db: PostgreSQLDatabase = request.app.state.db
        try:
            conn = db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.fetchone()
            finally:
                conn.close()
            return success_response({"status": "ok", "database": "ok", "timestamp": ts})
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Health check failed: %s", exc, exc_info=True)
            raise HTTPException(
                status_code=503,
                detail=error_response(
                    error_types.DATABASE_UNAVAILABLE,
                    str(exc),
                    {"timestamp": ts},
                ),
            ) from exc

    @app.get("/api/market/prices")
    def prices(request: Request):
        market_fetcher: MarketDataFetcher = request.app.state.market_fetcher
        try:
            data = market_fetcher.get_current_prices(config.DEFAULT_COINS)
            return success_response(data)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to fetch current prices: %s", exc, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=error_response(
                    error_types.EXTERNAL_SERVICE_ERROR,
                    "failed to fetch prices",
                    {"error": str(exc)},
                ),
            ) from exc

    @app.get("/api/market/history")
    def history(
        request: Request,
        coin: str = Query(...),
        resolution: Optional[int] = None,
        limit: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ):
        if not coin:
            raise HTTPException(
                status_code=400,
                detail=error_response(
                    error_types.INVALID_REQUEST,
                    "coin parameter is required",
                    {"parameter": "coin"},
                ),
            )

        default_resolution = config.MARKET_HISTORY_RESOLUTION
        max_points = min(config.MARKET_HISTORY_MAX_POINTS, HISTORY_MAX_LIMIT)

        try:
            resolution_value = int(resolution) if resolution is not None else default_resolution
            limit_raw = int(limit) if limit is not None else max_points
            limit_value = max(1, min(limit_raw, max_points))
            start_dt = _parse_iso(start)
            end_dt = _parse_iso(end)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=error_response(
                    error_types.INVALID_VALUE,
                    str(exc),
                ),
            ) from exc

        history_service: MarketHistoryService = request.app.state.history_service
        data = history_service.fetch_history(
            coin=coin,
            resolution=resolution_value,
            limit=limit_value,
            start=start_dt,
            end=end_dt,
        )
        return success_response(
            {
                "coin": coin.upper(),
                "resolution": resolution_value,
                "limit": limit_value,
                "records": data,
            }
        )

    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cfg = Config()
    history_app = create_app(cfg)
    uvicorn.run(history_app, host="0.0.0.0", port=5100)
