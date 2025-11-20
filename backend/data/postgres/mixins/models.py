"""Model management mixin for PostgreSQL database."""

from __future__ import annotations

from typing import Dict, List, Optional


class ModelRepositoryMixin:
    """CRUD helpers for trading models."""

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
