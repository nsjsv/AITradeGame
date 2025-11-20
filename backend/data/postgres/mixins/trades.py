"""Trade storage mixin."""

from __future__ import annotations

from typing import Dict, List


class TradeRepositoryMixin:
    """Manages trade persistence."""

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
