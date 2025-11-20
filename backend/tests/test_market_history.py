"""Tests for market history persistence and API."""

from datetime import datetime, timedelta, timezone


class TestMarketAPI:
    """Test market API endpoints"""

    def test_get_market_prices_success(self, client):
        """Test getting market prices - success scenario with HTTP 200 and data field"""
        response = client.get("/api/market/prices")
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        # Data should be a dictionary of coin prices
        assert isinstance(payload["data"], dict)

    def test_market_history_success(self, client, db):
        """Test getting market history - success scenario with HTTP 200 and data field"""
        base_ts = datetime.now(timezone.utc).replace(microsecond=0, second=0)
        rows = [
            {
                "coin": "BTC",
                "resolution": 60,
                "timestamp": base_ts - timedelta(minutes=2),
                "open": 50000.0,
                "high": 50050.0,
                "low": 49900.0,
                "close": 50010.0,
                "volume": 12.3,
                "source": "test",
            },
            {
                "coin": "BTC",
                "resolution": 60,
                "timestamp": base_ts - timedelta(minutes=1),
                "open": 50010.0,
                "high": 50100.0,
                "low": 50000.0,
                "close": 50080.0,
                "volume": 8.1,
                "source": "test",
            },
        ]
        db.record_market_prices(rows)

        response = client.get("/api/market/history?coin=BTC&resolution=60&limit=10")
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert data["coin"] == "BTC"
        assert data["resolution"] == 60
        assert len(data["records"]) == 2
        assert data["records"][0]["close"] == rows[0]["close"]
        assert data["records"][1]["close"] == rows[1]["close"]

    def test_market_history_missing_coin(self, client):
        """Test getting market history without coin parameter - client error with HTTP 400 and standard error object"""
        response = client.get("/api/market/history")
        assert response.status_code == 422  # FastAPI validation error for missing required query param

    def test_market_history_invalid_timestamp(self, client):
        """Test getting market history with invalid timestamp - client error with HTTP 400 and standard error object"""
        response = client.get("/api/market/history?coin=BTC&start=invalid-timestamp")
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == "INVALID_VALUE"
        assert "Invalid ISO timestamp" in error["message"]

    def test_market_history_invalid_resolution(self, client):
        """Test getting market history with invalid resolution - FastAPI validation error with HTTP 422"""
        response = client.get("/api/market/history?coin=BTC&resolution=not-a-number")
        # FastAPI returns 422 for query parameter type validation errors
        assert response.status_code == 422
        data = response.json()
        # FastAPI's validation error format
        assert "detail" in data


def test_market_history_endpoint(client, db):
    """Ensure history endpoint returns persisted snapshots."""
    base_ts = datetime.now(timezone.utc).replace(microsecond=0, second=0)
    rows = [
        {
            "coin": "BTC",
            "resolution": 60,
            "timestamp": base_ts - timedelta(minutes=2),
            "open": 50000.0,
            "high": 50050.0,
            "low": 49900.0,
            "close": 50010.0,
            "volume": 12.3,
            "source": "test",
        },
        {
            "coin": "BTC",
            "resolution": 60,
            "timestamp": base_ts - timedelta(minutes=1),
            "open": 50010.0,
            "high": 50100.0,
            "low": 50000.0,
            "close": 50080.0,
            "volume": 8.1,
            "source": "test",
        },
    ]
    db.record_market_prices(rows)

    response = client.get("/api/market/history?coin=BTC&resolution=60&limit=10")
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["coin"] == "BTC"
    assert payload["resolution"] == 60
    assert len(payload["records"]) == 2
    assert payload["records"][0]["close"] == rows[0]["close"]
    assert payload["records"][1]["close"] == rows[1]["close"]
