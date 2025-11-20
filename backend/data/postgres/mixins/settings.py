"""Settings management mixin."""

from __future__ import annotations

from typing import Dict

from backend.config.constants import (
    DEFAULT_MARKET_REFRESH_INTERVAL,
    DEFAULT_PORTFOLIO_REFRESH_INTERVAL,
    DEFAULT_TRADE_FEE_RATE,
    DEFAULT_TRADING_FREQUENCY_MINUTES,
)


class SettingsRepositoryMixin:
    """Reads and updates runtime settings."""

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
