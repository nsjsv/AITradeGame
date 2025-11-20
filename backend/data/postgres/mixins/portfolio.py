"""Portfolio management mixin."""

from __future__ import annotations

from typing import Dict, List


class PortfolioRepositoryMixin:
    """Position + PnL helpers."""

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

        cursor.execute(
            """
            SELECT
                m.initial_capital,
                COALESCE(SUM(t.pnl), 0) AS realized_pnl,
                COALESCE(SUM(t.fee), 0) AS total_fees
            FROM models AS m
            LEFT JOIN trades AS t ON t.model_id = m.id
            WHERE m.id = %s
            GROUP BY m.id
            """,
            (model_id,),
        )
        summary_row = cursor.fetchone() or {}
        initial_capital = summary_row.get("initial_capital", 0)
        realized_pnl = summary_row.get("realized_pnl", 0)
        total_fees = summary_row.get("total_fees", 0)

        margin_used = sum((p["quantity"] * p["avg_price"]) / p["leverage"] for p in positions)

        unrealized_pnl = 0
        positions_value = 0
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
                positions_value += quantity * current_price
        else:
            for pos in positions:
                pos["current_price"] = None
                pos["pnl"] = 0
                positions_value += pos["quantity"] * pos["avg_price"]

        cash = initial_capital + realized_pnl - margin_used
        total_value = initial_capital + realized_pnl + unrealized_pnl

        conn.close()

        return {
            "model_id": model_id,
            "initial_capital": initial_capital,
            "cash": cash,
            "positions": positions,
            "positions_value": positions_value,
            "margin_used": margin_used,
            "total_value": total_value,
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "total_fees": total_fees,
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
