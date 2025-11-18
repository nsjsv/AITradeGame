"""Standalone market history service (HTTP API + collector).

This service is decoupled from the trading backend so that market data
collection/serving can continue even if the trading API restarts.
"""

from __future__ import annotations

import atexit
import logging
from datetime import datetime, timezone
from typing import Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.config.settings import Config
from backend.data.postgres_db import PostgreSQLDatabase
from backend.data.market_data import MarketDataFetcher
from backend.services.market_history import (
    MarketHistoryService,
    MarketHistoryCollector,
)
from backend.config.constants import HISTORY_DEFAULT_LIMIT, HISTORY_MAX_LIMIT


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


def create_app(config: Optional[Config] = None) -> Flask:
    config = config or Config()

    app = Flask(__name__)
    CORS(app)

    # Set up dependencies
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

    @app.route("/health", methods=["GET"])
    def health():
        ts = datetime.now(timezone.utc).isoformat()
        try:
            conn = db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.fetchone()
            finally:
                conn.close()
            return jsonify({"status": "ok", "database": "ok", "timestamp": ts})
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(f"Health check failed: {exc}", exc_info=True)
            return (
                jsonify(
                    {
                        "status": "error",
                        "database": "error",
                        "timestamp": ts,
                        "message": str(exc),
                    }
                ),
                503,
            )

    @app.route("/api/market/prices", methods=["GET"])
    def prices():
        try:
            data = market_fetcher.get_current_prices(config.DEFAULT_COINS)
            return jsonify(data)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(f"Failed to fetch current prices: {exc}", exc_info=True)
            return jsonify({"error": "failed to fetch prices"}), 500

    @app.route("/api/market/history", methods=["GET"])
    def history():
        coin = request.args.get("coin")
        if not coin:
            return jsonify({"error": "coin parameter is required"}), 400

        default_resolution = config.MARKET_HISTORY_RESOLUTION
        max_points = min(config.MARKET_HISTORY_MAX_POINTS, HISTORY_MAX_LIMIT)

        try:
            resolution = int(request.args.get("resolution", default_resolution))
            limit = int(request.args.get("limit", max_points))
            limit = max(1, min(limit, max_points))
            start_dt = _parse_iso(request.args.get("start"))
            end_dt = _parse_iso(request.args.get("end"))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        data = history_service.fetch_history(
            coin=coin,
            resolution=resolution,
            limit=limit,
            start=start_dt,
            end=end_dt,
        )
        return jsonify(
            {"coin": coin.upper(), "resolution": resolution, "limit": limit, "records": data}
        )

    def _cleanup() -> None:
        if collector:
            try:
                collector.stop()
            except Exception:
                logger.warning("Failed to stop history collector", exc_info=True)

    atexit.register(_cleanup)

    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cfg = Config()
    app = create_app(cfg)
    app.run(host="0.0.0.0", port=5100)
