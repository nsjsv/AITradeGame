"""Account value analytics mixin."""

from __future__ import annotations

from typing import Dict, List


class AccountValueRepositoryMixin:
    """Handles account value snapshots and aggregates."""

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
