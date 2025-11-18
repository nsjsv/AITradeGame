"""Tests for market history persistence and API."""

from datetime import datetime, timedelta, timezone


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
    payload = response.get_json()
    assert payload["coin"] == "BTC"
    assert payload["resolution"] == 60
    assert len(payload["records"]) == 2
    assert payload["records"][0]["close"] == rows[0]["close"]
    assert payload["records"][1]["close"] == rows[1]["close"]
