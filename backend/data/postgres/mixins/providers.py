"""Provider management mixin for PostgreSQL database."""

from __future__ import annotations

from typing import Dict, List, Optional

from backend.utils.encryption import decrypt_api_key, encrypt_api_key


class ProviderRepositoryMixin:
    """Encapsulates CRUD operations for API providers."""

    def add_provider(self, name: str, api_url: str, api_key: str, models: str = "") -> int:
        encrypted_key = encrypt_api_key(api_key)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO providers (name, api_url, api_key, models)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (name, api_url, encrypted_key, models),
        )
        provider_id = cursor.fetchone()["id"]
        conn.commit()
        conn.close()
        self._logger.info("Added provider '%s' with encrypted API key", name)
        return provider_id

    def get_provider(self, provider_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM providers WHERE id = %s", (provider_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            provider = dict(row)
            provider["api_key"] = decrypt_api_key(provider["api_key"])
            return provider
        return None

    def get_all_providers(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM providers ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        providers: List[Dict] = []
        for row in rows:
            provider = dict(row)
            encrypted_key = provider["api_key"]
            try:
                decrypted = decrypt_api_key(encrypted_key)
                provider["api_key"] = decrypted[:8] + "..." if len(decrypted) > 8 else "***"
            except Exception:
                provider["api_key"] = "***"
            providers.append(provider)
        return providers

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
        encrypted_key = encrypt_api_key(api_key)
        cursor.execute(
            """
            UPDATE providers
            SET name = %s, api_url = %s, api_key = %s, models = %s
            WHERE id = %s
            """,
            (name, api_url, encrypted_key, models, provider_id),
        )
        conn.commit()
        conn.close()
