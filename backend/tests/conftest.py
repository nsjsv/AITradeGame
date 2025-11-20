"""Pytest configuration and fixtures."""

import os

import pytest
from fastapi.testclient import TestClient
from psycopg import conninfo, sql

from backend.config.settings import Config
from main import create_app

TEST_DB_URI = os.getenv(
    "TEST_POSTGRES_URI",
    "postgresql://aitrade:aitrade@localhost:5432/aitrade_test",
)


def _validate_test_uri(uri: str) -> None:
    """Ensure the test database URI is safe to clean between tests."""
    info = conninfo.conninfo_to_dict(uri)
    dbname = (info.get("dbname") or "").lower()
    if not dbname or "test" not in dbname:
        raise RuntimeError(
            "TEST_POSTGRES_URI must point to a database whose name contains 'test' "
            "to avoid wiping production data during tests."
        )


def _reset_database(database) -> None:
    """Truncate all public tables to keep tests isolated."""
    conn = database.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
        """
        )
        tables = [row["tablename"] for row in cursor.fetchall()]
        if tables:
            table_list = sql.SQL(", ").join(
                sql.Identifier("public", table) for table in tables
            )
            cursor.execute(
                sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE").format(
                    table_list
                )
            )
        conn.commit()
    finally:
        conn.close()


@pytest.fixture
def test_config() -> Config:
    """Create test configuration bound to a PostgreSQL database."""
    _validate_test_uri(TEST_DB_URI)
    config = Config()
    config.DEBUG = True
    config.TESTING = True  # type: ignore[attr-defined]
    config.POSTGRES_URI = TEST_DB_URI
    config.AUTO_TRADING = False
    config.MARKET_HISTORY_ENABLED = False
    return config


@pytest.fixture
def app(test_config: Config):
    """Create FastAPI app for testing."""
    return create_app(test_config)


@pytest.fixture
def client(app):
    """Create test client with isolated database state."""
    with TestClient(app) as client:
        container = app.state.container
        container.db.init_db()
        _reset_database(container.db)
        yield client
        _reset_database(container.db)


@pytest.fixture
def db(client):
    """Get database instance from running app."""
    return client.app.state.container.db
