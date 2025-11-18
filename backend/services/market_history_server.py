"""Standalone market history service.

This service runs independently from the main backend to keep market data
collection and history queries alive even if the trading API is restarted.
"""

from __future__ import annotations

import atexit
import logging
import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.config.settings import Config
from backend.data.market_data import MarketDataFetcher
from backend.data.postgres_db import PostgreSQLDatabase
from backend.services.market_history import (
    MarketHistoryCollector,
    MarketHistoryService,
)

logger = logging.getLogger(__name__)


def create_app(config: Config) -> Flask:
    app = Flask(__name__)
    CORS(app)

    db = PostgreSQLDatabase(config.POSTGRES_URI)
    market_fetcher = MarketDataFetcher(
        api_url=config.MARKET_API_URL,
        cache_duration=config.MARKET_CACHE_DURATION,
    )
    history_service = MarketHistoryService(
        db=db,
        cache_ttl=config.MARKET_HISTORY_CACHE_TTL,
    )

    collector = None
    if config.MARKET_HISTORY_ENABLED:
        collector = MarketHistoryCollector(
            db=db,
            market_fetcher=market_fetcher,
            coins=config.DEFAULT_COINS,
            interval=config.MARKET_HISTORY_INTERVAL,
            resolution=config.MARKET_HISTORY_RESOLUTION,
        )
        collector.start()
        logger.info(
            "Market history collector running (interval=%ss, resolution=%ss)",
            config.MARKET_HISTORY_INTERVAL,
            config.MARKET_HISTORY_RESOLUTION,
        )
    else:
        logger.info("Market history collector disabled via config")

    @atexit.register
    def _cleanup():
        if collector:
            try:
                collector.stop()
            except Exception as exc:  # pragma: no cover - shutdown path
                logger.error("Failed to stop collector: %s", exc, exc_info=True)

    @app.route("/api/health", methods=["GET"])
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
        except Exception as exc:
            logger.error("Health check failed: %s", exc)
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
    def get_prices():
        coins_param = request.args.get("coins")
        coins = (
            [s.strip().upper() for s in coins_param.split(",") if s.strip()]
            if coins_param
            else config.DEFAULT_COINS
        )
        prices = market_fetcher.get_current_prices(coins)
        return jsonify(prices)

    @app.route("/api/market/history", methods=["GET"])
    def get_history():
        coin = request.args.get("coin")
        if not coin:
            return jsonify({"error": "coin parameter is required"}), 400
        try:
            resolution = int(
                request.args.get("resolution", config.MARKET_HISTORY_RESOLUTION)
            )
            limit_raw = int(
                request.args.get("limit", config.MARKET_HISTORY_MAX_POINTS)
            )
            limit = max(
                1,
                min(
                    limit_raw,
                    config.MARKET_HISTORY_MAX_POINTS,
                ),
            )
            start = request.args.get("start")
            end = request.args.get("end")
            start_dt = datetime.fromisoformat(start) if start else None
            end_dt = datetime.fromisoformat(end) if end else None
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        records = history_service.fetch_history(
            coin=coin,
            resolution=resolution,
            limit=limit,
            start=start_dt,
            end=end_dt,
        )
        return jsonify(
            {
                "coin": coin.upper(),
                "resolution": resolution,
                "limit": limit,
                "records": records,
            }
        )

    return app


def main():
    config = Config()
    app = create_app(config)
    host = os.getenv("COLLECTOR_HOST", "0.0.0.0")
    port = int(os.getenv("COLLECTOR_PORT", os.getenv("PORT", "5100")))
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
