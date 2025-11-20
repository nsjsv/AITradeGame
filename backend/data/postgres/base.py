"""Base utilities for PostgreSQL database implementation."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Set

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from backend.config.constants import (
    DEFAULT_MARKET_REFRESH_INTERVAL,
    DEFAULT_PORTFOLIO_REFRESH_INTERVAL,
    DEFAULT_TRADE_FEE_RATE,
    DEFAULT_TRADING_FREQUENCY_MINUTES,
)
from backend.data.database import DatabaseInterface


class PostgresBase(DatabaseInterface):
    """Provides shared connection + schema helpers for PostgreSQL backends."""

    _DEFAULT_INSTRUMENTS = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "DOGE": "dogecoin",
    }

    def __init__(self, dsn: str):
        if not dsn:
            raise ValueError("POSTGRES_URI is required when using PostgreSQL database")
        self.dsn = dsn
        self._logger = logging.getLogger(__name__)
        self._closed = False
        self._known_partitions: Set[str] = set()

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def get_connection(self):
        """Create a new database connection."""
        if self._closed:
            raise RuntimeError("Database connections are closed")
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def close(self) -> None:
        """Mark the database as closed to prevent further connections."""
        self._closed = True
        self._logger.debug("PostgreSQLDatabase has been closed")

    # ------------------------------------------------------------------
    # Schema management
    # ------------------------------------------------------------------

    def init_db(self) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS providers (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                api_url TEXT NOT NULL,
                api_key TEXT NOT NULL,
                models TEXT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS models (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                provider_id INTEGER REFERENCES providers(id),
                model_name TEXT NOT NULL,
                initial_capital DOUBLE PRECISION DEFAULT 10000,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolios (
                id SERIAL PRIMARY KEY,
                model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
                coin TEXT NOT NULL,
                quantity DOUBLE PRECISION NOT NULL,
                avg_price DOUBLE PRECISION NOT NULL,
                leverage INTEGER DEFAULT 1,
                side TEXT DEFAULT 'long',
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(model_id, coin, side)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
                coin TEXT NOT NULL,
                signal TEXT NOT NULL,
                quantity DOUBLE PRECISION NOT NULL,
                price DOUBLE PRECISION NOT NULL,
                leverage INTEGER DEFAULT 1,
                side TEXT DEFAULT 'long',
                pnl DOUBLE PRECISION DEFAULT 0,
                fee DOUBLE PRECISION DEFAULT 0,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
                user_prompt TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                cot_trace TEXT,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS account_values (
                id SERIAL PRIMARY KEY,
                model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
                total_value DOUBLE PRECISION NOT NULL,
                cash DOUBLE PRECISION NOT NULL,
                positions_value DOUBLE PRECISION NOT NULL,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS settings (
                id SERIAL PRIMARY KEY,
                trading_frequency_minutes INTEGER DEFAULT {DEFAULT_TRADING_FREQUENCY_MINUTES},
                trading_fee_rate DOUBLE PRECISION DEFAULT {DEFAULT_TRADE_FEE_RATE},
                market_refresh_interval INTEGER DEFAULT {DEFAULT_MARKET_REFRESH_INTERVAL},
                portfolio_refresh_interval INTEGER DEFAULT {DEFAULT_PORTFOLIO_REFRESH_INTERVAL},
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            f"""
            ALTER TABLE settings
            ADD COLUMN IF NOT EXISTS market_refresh_interval INTEGER DEFAULT {DEFAULT_MARKET_REFRESH_INTERVAL}
            """
        )
        cursor.execute(
            f"""
            ALTER TABLE settings
            ADD COLUMN IF NOT EXISTS portfolio_refresh_interval INTEGER DEFAULT {DEFAULT_PORTFOLIO_REFRESH_INTERVAL}
            """
        )

        cursor.execute("SELECT COUNT(*) AS total FROM settings")
        count_row = cursor.fetchone()
        if not count_row or count_row["total"] == 0:
            cursor.execute(
                """
                INSERT INTO settings (
                    trading_frequency_minutes,
                    trading_fee_rate,
                    market_refresh_interval,
                    portfolio_refresh_interval
                ) VALUES (%s, %s, %s, %s)
                """,
                (
                    DEFAULT_TRADING_FREQUENCY_MINUTES,
                    DEFAULT_TRADE_FEE_RATE,
                    DEFAULT_MARKET_REFRESH_INTERVAL,
                    DEFAULT_PORTFOLIO_REFRESH_INTERVAL,
                ),
            )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS market_instruments (
                id SERIAL PRIMARY KEY,
                symbol TEXT NOT NULL UNIQUE,
                source_symbol TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS market_prices (
                coin TEXT NOT NULL,
                resolution INTEGER NOT NULL,
                ts TIMESTAMPTZ NOT NULL,
                open DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                close DOUBLE PRECISION,
                volume DOUBLE PRECISION DEFAULT 0,
                source TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (coin, resolution, ts)
            ) PARTITION BY RANGE (ts)
            """
        )

        cursor.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_indexes WHERE indexname = 'idx_market_prices_brin_ts'
                ) THEN
                    CREATE INDEX idx_market_prices_brin_ts
                    ON market_prices USING BRIN (ts);
                END IF;
            END $$;
            """
        )

        self._seed_market_instruments(cursor)
        self._ensure_market_prices_partition(cursor, datetime.now(timezone.utc))

        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Helpers shared by mixins
    # ------------------------------------------------------------------

    def _seed_market_instruments(self, cursor) -> None:
        for symbol, source_symbol in self._DEFAULT_INSTRUMENTS.items():
            cursor.execute(
                """
                INSERT INTO market_instruments (symbol, source_symbol)
                VALUES (%s, %s)
                ON CONFLICT (symbol) DO UPDATE SET
                    source_symbol = EXCLUDED.source_symbol,
                    is_active = TRUE
                """,
                (symbol, source_symbol),
            )

    def _normalize_timestamp(self, ts: datetime) -> datetime:
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc)

    def _partition_anchor(self, ts: datetime) -> datetime:
        normalized = self._normalize_timestamp(ts)
        return normalized.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def _next_partition_anchor(self, anchor: datetime) -> datetime:
        if anchor.month == 12:
            return anchor.replace(year=anchor.year + 1, month=1)
        return anchor.replace(month=anchor.month + 1)

    def _ensure_partition_for_anchor(self, cursor, anchor: datetime) -> None:
        partition_name = f"market_prices_{anchor.year}_{anchor.month:02d}"
        if partition_name in self._known_partitions:
            return
        cursor.execute("SELECT to_regclass(%s) AS relname", (partition_name,))
        result = cursor.fetchone()
        if result and result.get("relname"):
            self._known_partitions.add(partition_name)
            return
        if anchor.month == 12:
            partition_end = anchor.replace(year=anchor.year + 1, month=1)
        else:
            partition_end = anchor.replace(month=anchor.month + 1)
        cursor.execute(
            sql.SQL(
                "CREATE TABLE {} PARTITION OF market_prices "
                "FOR VALUES FROM ({}) TO ({})"
            ).format(
                sql.Identifier(partition_name),
                sql.Literal(anchor),
                sql.Literal(partition_end),
            )
        )
        cursor.execute(
            sql.SQL(
                "CREATE INDEX IF NOT EXISTS {} ON {} (coin, resolution, ts DESC)"
            ).format(
                sql.Identifier(f"{partition_name}_coin_res_ts_idx"),
                sql.Identifier(partition_name),
            )
        )
        self._known_partitions.add(partition_name)

    def _ensure_market_prices_partition(self, cursor, ts: datetime) -> None:
        anchor = self._partition_anchor(ts)
        self._ensure_partition_for_anchor(cursor, anchor)
        # Always prepare the next partition ahead of time to avoid inserts blocking later.
        self._ensure_partition_for_anchor(cursor, self._next_partition_anchor(anchor))
