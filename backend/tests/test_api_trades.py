"""Tests for trades API endpoints."""


class TestTradesAPI:
    """Test trades API endpoints"""

    def test_get_portfolio_success(self, client, db):
        """Test getting portfolio for existing model - success scenario with HTTP 200 and data field"""
        # Create provider and model
        provider_id = db.add_provider("Test Provider", "https://api.example.com", "test-key")
        model_id = db.add_model("Test Model", provider_id, "gpt-4")

        response = client.get(f"/api/models/{model_id}/portfolio")
        
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert "portfolio" in data
        assert "account_value_history" in data

    def test_get_portfolio_model_not_found(self, client):
        """Test getting portfolio for non-existent model - error scenario with HTTP 404 and standard error object"""
        non_existent_model_id = 99999
        
        response = client.get(f"/api/models/{non_existent_model_id}/portfolio")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == "RESOURCE_NOT_FOUND"
        assert str(non_existent_model_id) in error["message"]
        assert "details" in error
        assert error["details"]["model_id"] == non_existent_model_id

    def test_get_trades_success(self, client, db):
        """Test getting trades for existing model - success scenario with HTTP 200 and data field"""
        # Create provider and model
        provider_id = db.add_provider("Test Provider", "https://api.example.com", "test-key")
        model_id = db.add_model("Test Model", provider_id, "gpt-4")

        response = client.get(f"/api/models/{model_id}/trades")
        
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert isinstance(data, list)

    def test_get_trades_with_limit(self, client, db):
        """Test getting trades with custom limit - success scenario with HTTP 200"""
        # Create provider and model
        provider_id = db.add_provider("Test Provider", "https://api.example.com", "test-key")
        model_id = db.add_model("Test Model", provider_id, "gpt-4")

        response = client.get(f"/api/models/{model_id}/trades?limit=10")
        
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert isinstance(data, list)

    def test_get_trades_model_not_found(self, client):
        """Test getting trades for non-existent model - error scenario with HTTP 404 and standard error object"""
        non_existent_model_id = 99999
        
        response = client.get(f"/api/models/{non_existent_model_id}/trades")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert error["code"] == "RESOURCE_NOT_FOUND"
        assert str(non_existent_model_id) in error["message"]
        assert error["details"]["model_id"] == non_existent_model_id

    def test_get_conversations_success(self, client, db):
        """Test getting conversations for existing model - success scenario with HTTP 200 and data field"""
        # Create provider and model
        provider_id = db.add_provider("Test Provider", "https://api.example.com", "test-key")
        model_id = db.add_model("Test Model", provider_id, "gpt-4")

        response = client.get(f"/api/models/{model_id}/conversations")
        
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert isinstance(data, list)

    def test_get_conversations_with_limit(self, client, db):
        """Test getting conversations with custom limit - success scenario with HTTP 200"""
        # Create provider and model
        provider_id = db.add_provider("Test Provider", "https://api.example.com", "test-key")
        model_id = db.add_model("Test Model", provider_id, "gpt-4")

        response = client.get(f"/api/models/{model_id}/conversations?limit=5")
        
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert isinstance(data, list)

    def test_get_conversations_model_not_found(self, client):
        """Test getting conversations for non-existent model - error scenario with HTTP 404 and standard error object"""
        non_existent_model_id = 99999
        
        response = client.get(f"/api/models/{non_existent_model_id}/conversations")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert error["code"] == "RESOURCE_NOT_FOUND"
        assert str(non_existent_model_id) in error["message"]
        assert error["details"]["model_id"] == non_existent_model_id

    def test_get_aggregated_portfolio_success(self, client):
        """Test getting aggregated portfolio - success scenario with HTTP 200 and data field"""
        response = client.get("/api/aggregated/portfolio")
        
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert isinstance(data, dict)

    def test_get_models_chart_data_success(self, client):
        """Test getting models chart data - success scenario with HTTP 200 and data field"""
        response = client.get("/api/models/chart-data")
        
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert isinstance(data, list)

    def test_get_models_chart_data_with_limit(self, client):
        """Test getting models chart data with custom limit - success scenario with HTTP 200"""
        response = client.get("/api/models/chart-data?limit=50")
        
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload

    def test_get_leaderboard_success(self, client):
        """Test getting leaderboard - success scenario with HTTP 200 and data field"""
        response = client.get("/api/leaderboard")
        
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert isinstance(data, list)
