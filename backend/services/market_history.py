"""Market history services and background collectors."""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Protocol

from backend.data.database import DatabaseInterface
from backend.data.market_data import MarketDataFetcher


class HistoryCacheProtocol(Protocol):
    """Interface for pluggable cache implementations."""

    def get(self, key: str) -> Optional[List[Dict]]:
        ...

    def set(self, key: str, value: List[Dict], ttl: int) -> None:
        ...


class NullHistoryCache:
    """No-op cache used until Redis or another cache is plugged in."""

    def get(self, key: str) -> Optional[List[Dict]]:
        return None

    def set(self, key: str, value: List[Dict], ttl: int) -> None:
        return None


class MarketHistoryService:
    """High-level facade for querying historical prices."""

    def __init__(
        self,
        db: DatabaseInterface,
        cache: Optional[HistoryCacheProtocol] = None,
        cache_ttl: int = 60,
    ):
        self.db = db
        self.cache = cache or NullHistoryCache()
        self.cache_ttl = cache_ttl
        self._logger = logging.getLogger(__name__)

    def _build_cache_key(
        self,
        coin: str,
        resolution: int,
        limit: int,
        start: Optional[datetime],
        end: Optional[datetime],
    ) -> str:
        start_token = start.isoformat() if start else "none"
        end_token = end.isoformat() if end else "none"
        return f"{coin}:{resolution}:{limit}:{start_token}:{end_token}"

    def fetch_history(
        self,
        coin: str,
        resolution: int,
        limit: int,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict]:
        cache_key = self._build_cache_key(coin, resolution, limit, start, end)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        data = self.db.get_market_history(coin, resolution, limit, start, end)
        self.cache.set(cache_key, data, self.cache_ttl)
        return data


class MarketHistoryCollector:
    """Background collector that persists periodic market snapshots."""

    def __init__(
        self,
        db: DatabaseInterface,
        market_fetcher: MarketDataFetcher,
        coins: List[str],
        interval: int,
        resolution: int,
    ):
        self.db = db
        self.market_fetcher = market_fetcher
        self.coins = coins
        self.interval = max(1, interval)
        self.resolution = max(1, resolution)
        self._thread: Optional[threading.Thread] = None
        self._stop_event: Optional[threading.Event] = None
        self._logger = logging.getLogger(__name__)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True, name="market-history-collector")
        self._thread.start()
        self._logger.info(
            "Market history collector started (interval=%ss, resolution=%ss)",
            self.interval,
            self.resolution,
        )

    def stop(self) -> None:
        if self._stop_event:
            self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
            self._logger.info("Market history collector stopped")
        self._stop_event = None

    def _run(self) -> None:
        event = self._stop_event
        if event is None:
            return
        next_run = time.time()
        while not event.is_set():
            try:
                self._collect_snapshot()
            except Exception as exc:  # pragma: no cover - defensive logging
                self._logger.error(f"Market history collection failed: {exc}", exc_info=True)
            next_run += self.interval
            sleep_for = max(0, next_run - time.time())
            event.wait(sleep_for)

    def _collect_snapshot(self) -> None:
        snapshot = self.market_fetcher.get_current_prices(self.coins)
        if not snapshot:
            return
        timestamp = datetime.now(timezone.utc)
        rows: List[Dict] = []
        for coin in self.coins:
            payload = snapshot.get(coin)
            if not payload:
                continue
            price = float(payload.get("price", 0) or 0)
            rows.append(
                {
                    "coin": coin,
                    "resolution": self.resolution,
                    "timestamp": timestamp,
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": float(payload.get("volume", 0) or 0),
                    "source": payload.get("source", "binance"),
                }
            )
        if not rows:
            return
        self.db.record_market_prices(rows)
        self._logger.debug(
            "Persisted %d market snapshots at %s", len(rows), timestamp.isoformat()
        )
