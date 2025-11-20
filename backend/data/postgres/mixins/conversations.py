"""Conversation history mixin."""

from __future__ import annotations

from typing import Dict, List


class ConversationRepositoryMixin:
    """Stores AI conversation history."""

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
