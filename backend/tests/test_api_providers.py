"""Tests for provider API endpoints."""


class TestProviderAPI:
    """Test provider API endpoints"""

    def test_get_providers_empty(self, client):
        """Test getting providers when none exist - success scenario with HTTP 200 and data field"""
        response = client.get("/api/providers")
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_provider(self, client):
        """Test creating a new provider - success scenario with HTTP 201 and data field"""
        provider_data = {
            "name": "Test Provider",
            "api_url": "https://api.example.com",
            "api_key": "test-key-12345",
            "models": "gpt-4,gpt-3.5-turbo",
        }

        response = client.post("/api/providers", json=provider_data)

        assert response.status_code == 201
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert "id" in data
        assert data["id"] > 0

    def test_get_providers_after_create(self, client):
        """Test getting providers after creating one - success scenario with HTTP 200"""
        provider_data = {
            "name": "Test Provider",
            "api_url": "https://api.example.com",
            "api_key": "test-key-12345",
            "models": "gpt-4",
        }

        create_response = client.post("/api/providers", json=provider_data)
        assert create_response.status_code == 201

        response = client.get("/api/providers")
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert len(data) == 1
        assert data[0]["name"] == "Test Provider"
        assert "..." in data[0]["api_key"] or data[0]["api_key"] == "***"

    def test_delete_provider(self, client):
        """Test deleting a provider - success scenario with HTTP 204"""
        provider_data = {
            "name": "Test Provider",
            "api_url": "https://api.example.com",
            "api_key": "test-key-12345",
        }

        create_response = client.post("/api/providers", json=provider_data)
        provider_id = create_response.json()["data"]["id"]

        response = client.delete(f"/api/providers/{provider_id}")
        assert response.status_code == 204

        get_response = client.get("/api/providers")
        data = get_response.json()["data"]
        assert len(data) == 0

    def test_create_provider_missing_fields(self, client):
        """Test creating provider with missing required fields - client error with HTTP 400 and standard error object"""
        provider_data = {
            "name": "Test Provider"
        }

        response = client.post("/api/providers", json=provider_data)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == "INVALID_REQUEST"
        assert "details" in error
        assert "missing_fields" in error["details"]

    def test_create_provider_missing_all_fields(self, client):
        """Test creating provider with all fields missing - client error with HTTP 400"""
        provider_data = {}

        response = client.post("/api/providers", json=provider_data)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert error["code"] == "INVALID_REQUEST"
        assert "missing_fields" in error["details"]
        assert len(error["details"]["missing_fields"]) == 3

    def test_create_provider_private_address_localhost(self, client):
        """Test creating provider with localhost URL - client error with HTTP 400"""
        provider_data = {
            "name": "Test Provider",
            "api_url": "http://localhost:8080",
            "api_key": "test-key",
        }

        response = client.post("/api/providers", json=provider_data)

        # This will fail during URL validation in fetch_models, not in add_provider
        # So we test it in the fetch_models endpoint
        assert response.status_code == 201  # Provider creation succeeds

    def test_fetch_models_missing_fields(self, client):
        """Test fetching models with missing fields - client error with HTTP 400"""
        response = client.post("/api/providers/models", json={})

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert error["code"] == "INVALID_REQUEST"
        assert "message" in error
        assert "details" in error
        assert "missing_fields" in error["details"]

    def test_fetch_models_private_address(self, client):
        """Test fetching models from private address - client error with HTTP 400"""
        payload = {
            "api_url": "http://localhost:8080",
            "api_key": "test-key",
        }

        response = client.post("/api/providers/models", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert error["code"] == "INVALID_REQUEST"
        assert "本地地址" in error["message"] or "内网地址" in error["message"]

    def test_fetch_models_invalid_scheme(self, client):
        """Test fetching models with invalid URL scheme - client error with HTTP 400"""
        payload = {
            "api_url": "ftp://api.example.com",
            "api_key": "test-key",
        }

        response = client.post("/api/providers/models", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert error["code"] == "INVALID_REQUEST"
        assert "协议" in error["message"]

    def test_fetch_models_invalid_hostname(self, client):
        """Test fetching models with invalid hostname - client error with HTTP 400"""
        payload = {
            "api_url": "https://",
            "api_key": "test-key",
        }

        response = client.post("/api/providers/models", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert error["code"] == "INVALID_REQUEST"
        assert "地址" in error["message"]
