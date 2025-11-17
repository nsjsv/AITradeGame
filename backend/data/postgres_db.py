"""PostgreSQL database implementation"""

from __future__ import annotations

from typing import Dict, List, Optional

import psycopg
from psycopg.rows import dict_row

from backend.config.constants import (
    DEFAULT_MARKET_REFRESH_INTERVAL,
    DEFAULT_PORTFOLIO_REFRESH_INTERVAL,
    DEFAULT_TRADE_FEE_RATE,
    DEFAULT_TRADING_FREQUENCY_MINUTES,
)
from backend.data.database import DatabaseInterface


class PostgreSQLDatabase(DatabaseInterface):
    """PostgreSQL implementation of DatabaseInterface."""

    def __init__(self, dsn: str):
        if not dsn:
            raise ValueError("POSTGRES_URI is required when using PostgreSQL database")
        self.dsn = dsn

    def get_connection(self):
        """Create a new database connection."""
        return psycopg.connect(self.dsn, row_factory=dict_row)

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

        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Provider management
    # ------------------------------------------------------------------

    def add_provider(self, name: str, api_url: str, api_key: str, models: str = "") -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO providers (name, api_url, api_key, models)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (name, api_url, api_key, models),
        )
        provider_id = cursor.fetchone()["id"]
        conn.commit()
        conn.close()
        return provider_id

    def get_provider(self, provider_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM providers WHERE id = %s", (provider_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_providers(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM providers ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_provider(self, provider_id: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM providers WHERE id = %s", (provider_id,))
        conn.commit()
        conn.close()

    def update_provider(
        self,
        provider_id: int,
        name: str,
        api_url: str,
        api_key: str,
        models: str,
    ) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE providers
            SET name = %s, api_url = %s, api_key = %s, models = %s
            WHERE id = %s
            """,
            (name, api_url, api_key, models, provider_id),
        )
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Model management
    # ------------------------------------------------------------------

    def add_model(
        self, name: str, provider_id: int, model_name: str, initial_capital: float = 10000
    ) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO models (name, provider_id, model_name, initial_capital)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (name, provider_id, model_name, initial_capital),
        )
        model_id = cursor.fetchone()["id"]
        conn.commit()
        conn.close()
        return model_id

    def get_model(self, model_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT m.*, p.api_key, p.api_url
            FROM models m
            LEFT JOIN providers p ON m.provider_id = p.id
            WHERE m.id = %s
            """,
            (model_id,),
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_models(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT m.*, p.name AS provider_name
            FROM models m
            LEFT JOIN providers p ON m.provider_id = p.id
            ORDER BY m.created_at DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_model(self, model_id: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM portfolios WHERE model_id = %s", (model_id,))
        cursor.execute("DELETE FROM trades WHERE model_id = %s", (model_id,))
        cursor.execute("DELETE FROM conversations WHERE model_id = %s", (model_id,))
        cursor.execute("DELETE FROM account_values WHERE model_id = %s", (model_id,))
        cursor.execute("DELETE FROM models WHERE id = %s", (model_id,))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Portfolio management
    # ------------------------------------------------------------------

    def update_position(
        self,
        model_id: int,
        coin: str,
        quantity: float,
        avg_price: float,
        leverage: int = 1,
        side: str = "long",
    ) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO portfolios (model_id, coin, quantity, avg_price, leverage, side, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (model_id, coin, side) DO UPDATE SET
                quantity = EXCLUDED.quantity,
                avg_price = EXCLUDED.avg_price,
                leverage = EXCLUDED.leverage,
                updated_at = CURRENT_TIMESTAMP
            """,
            (model_id, coin, quantity, avg_price, leverage, side),
        )
        conn.commit()
        conn.close()

    def get_portfolio(self, model_id: int, current_prices: Dict = None) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM portfolios WHERE model_id = %s AND quantity > 0",
            (model_id,),
        )
        positions = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT initial_capital FROM models WHERE id = %s", (model_id,))
        capital_row = cursor.fetchone()
        initial_capital = capital_row["initial_capital"] if capital_row else 0

        cursor.execute(
            "SELECT COALESCE(SUM(pnl), 0) AS total_pnl FROM trades WHERE model_id = %s",
            (model_id,),
        )
        realized_pnl = cursor.fetchone()["total_pnl"]

        margin_used = sum((p["quantity"] * p["avg_price"]) / p["leverage"] for p in positions)

        unrealized_pnl = 0
        if current_prices:
            for pos in positions:
                coin = pos["coin"]
                current_price = current_prices.get(coin)
                if current_price is None:
                    pos["current_price"] = None
                    pos["pnl"] = 0
                    continue

                entry_price = pos["avg_price"]
                quantity = pos["quantity"]
                pos["current_price"] = current_price

                if pos["side"] == "long":
                    pos_pnl = (current_price - entry_price) * quantity
                else:
                    pos_pnl = (entry_price - current_price) * quantity

                pos["pnl"] = pos_pnl
                unrealized_pnl += pos_pnl
        else:
            for pos in positions:
                pos["current_price"] = None
                pos["pnl"] = 0

        cash = initial_capital + realized_pnl - margin_used
        positions_value = sum(p["quantity"] * p["avg_price"] for p in positions)
        total_value = initial_capital + realized_pnl + unrealized_pnl

        conn.close()

        return {
            "model_id": model_id,
            "cash": cash,
            "positions": positions,
            "positions_value": positions_value,
            "margin_used": margin_used,
            "total_value": total_value,
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
        }

    def close_position(self, model_id: int, coin: str, side: str = "long") -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM portfolios WHERE model_id = %s AND coin = %s AND side = %s",
            (model_id, coin, side),
        )
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Trade records
    # ------------------------------------------------------------------

    def add_trade(
        self,
        model_id: int,
        coin: str,
        signal: str,
        quantity: float,
        price: float,
        leverage: int = 1,
        side: str = "long",
        pnl: float = 0,
        fee: float = 0,
    ) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO trades (model_id, coin, signal, quantity, price, leverage, side, pnl, fee)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (model_id, coin, signal, quantity, price, leverage, side, pnl, fee),
        )
        conn.commit()
        conn.close()

    def get_trades(self, model_id: int, limit: int = 50) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM trades
            WHERE model_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (model_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Conversation history
    # ------------------------------------------------------------------

    def add_conversation(
        self, model_id: int, user_prompt: str, ai_response: str, cot_trace: str = ""
    ) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO conversations (model_id, user_prompt, ai_response, cot_trace)
            VALUES (%s, %s, %s, %s)
            """,
            (model_id, user_prompt, ai_response, cot_trace),
        )
        conn.commit()
        conn.close()

    def get_conversations(self, model_id: int, limit: int = 20) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM conversations
            WHERE model_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (model_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Account value history
    # ------------------------------------------------------------------

    def record_account_value(
        self, model_id: int, total_value: float, cash: float, positions_value: float
    ) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO account_values (model_id, total_value, cash, positions_value)
            VALUES (%s, %s, %s, %s)
            """,
            (model_id, total_value, cash, positions_value),
        )
        conn.commit()
        conn.close()

    def get_account_value_history(self, model_id: int, limit: int = 100) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM account_values
            WHERE model_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (model_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_aggregated_account_value_history(self, limit: int = 100) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            WITH ranked AS (
                SELECT
                    timestamp,
                    total_value,
                    cash,
                    positions_value,
                    model_id,
                    ROW_NUMBER() OVER (
                        PARTITION BY model_id, DATE(timestamp)
                        ORDER BY timestamp DESC
                    ) AS rn
                FROM account_values
            )
            SELECT
                date_trunc('hour', timestamp) AS bucket,
                SUM(total_value) AS total_value,
                SUM(cash) AS cash,
                SUM(positions_value) AS positions_value,
                COUNT(DISTINCT model_id) AS model_count
            FROM ranked
            WHERE rn <= 10
            GROUP BY bucket
            ORDER BY bucket DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "timestamp": row["bucket"].isoformat() if row["bucket"] else None,
                "total_value": row["total_value"],
                "cash": row["cash"],
                "positions_value": row["positions_value"],
                "model_count": row["model_count"],
            }
            for row in rows
        ]

    def get_multi_model_chart_data(self, limit: int = 100) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM models")
        models = cursor.fetchall()

        chart_data: List[Dict] = []
        for model in models:
            cursor.execute(
                """
                SELECT timestamp, total_value
                FROM account_values
                WHERE model_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (model["id"], limit),
            )
            history = cursor.fetchall()
            if not history:
                continue
            chart_data.append(
                {
                    "model_id": model["id"],
                    "model_name": model["name"],
                    "data": [
                        {"timestamp": row["timestamp"].isoformat(), "value": row["total_value"]}
                        for row in history
                    ],
                }
            )

        conn.close()
        return chart_data

    # ------------------------------------------------------------------
    # Settings management
    # ------------------------------------------------------------------

    def get_settings(self) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT trading_frequency_minutes,
                   trading_fee_rate,
                   market_refresh_interval,
                   portfolio_refresh_interval
            FROM settings
            ORDER BY id DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return {
            "trading_frequency_minutes": DEFAULT_TRADING_FREQUENCY_MINUTES,
            "trading_fee_rate": DEFAULT_TRADE_FEE_RATE,
            "market_refresh_interval": DEFAULT_MARKET_REFRESH_INTERVAL,
            "portfolio_refresh_interval": DEFAULT_PORTFOLIO_REFRESH_INTERVAL,
        }

    def update_settings(
        self,
        trading_frequency_minutes: int,
        trading_fee_rate: float,
        market_refresh_interval: int,
        portfolio_refresh_interval: int,
    ) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE settings
                SET trading_frequency_minutes = %s,
                    trading_fee_rate = %s,
                    market_refresh_interval = %s,
                    portfolio_refresh_interval = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = (
                    SELECT id FROM settings ORDER BY id DESC LIMIT 1
                )
                """,
                (
                    trading_frequency_minutes,
                    trading_fee_rate,
                    market_refresh_interval,
                    portfolio_refresh_interval,
                ),
            )
            conn.commit()
            success = cursor.rowcount > 0
        except Exception:
            conn.rollback()
            success = False
        finally:
            conn.close()
        return success
