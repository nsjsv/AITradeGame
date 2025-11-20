"""Market history storage mixin."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional


class MarketHistoryRepositoryMixin:
    """Persists OHLCV candles for market history service."""

    def record_market_prices(self, rows: List[Dict]) -> None:
        if not rows:
            return
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            partitions = set()
            normalized_rows = []
            for row in rows:
                ts = self._normalize_timestamp(row["timestamp"])
                partitions.add(self._partition_anchor(ts))
                normalized_rows.append(
                    (
                        row["coin"].upper(),
                        int(row["resolution"]),
                        ts,
                        row.get("open"),
                        row.get("high"),
                        row.get("low"),
                        row.get("close"),
                        float(row.get("volume", 0) or 0),
                        row.get("source", "binance"),
                    )
                )
            for anchor in partitions:
                self._ensure_market_prices_partition(cursor, anchor)
            cursor.executemany(
                """
                INSERT INTO market_prices (
                    coin, resolution, ts, open, high, low, close, volume, source
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (coin, resolution, ts) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume,
                    source = EXCLUDED.source,
                    created_at = CURRENT_TIMESTAMP
                """,
                normalized_rows,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_market_history(
        self,
        coin: str,
        resolution: int,
        limit: int = 500,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            clauses = ["WHERE coin = %s", "AND resolution = %s"]
            params: List = [coin.upper(), int(resolution)]
            if start:
                clauses.append("AND ts >= %s")
                params.append(self._normalize_timestamp(start))
            if end:
                clauses.append("AND ts <= %s")
                params.append(self._normalize_timestamp(end))
            clauses.append("ORDER BY ts DESC LIMIT %s")
            params.append(limit)
            query = " ".join(
                [
                    "SELECT coin, resolution, ts, open, high, low, close, volume, source",
                    "FROM market_prices",
                    *clauses,
                ]
            )
            cursor.execute(query, params)
            rows = cursor.fetchall()
            history: List[Dict] = [
                {
                    "coin": row["coin"],
                    "resolution": row["resolution"],
                    "timestamp": row["ts"].isoformat(),
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"],
                    "source": row["source"],
                }
                for row in rows
            ]
            history.reverse()
            return history
        finally:
            conn.close()
