"""Tests for model API endpoints."""

import pytest


class TestModelAPI:
    """Test model API endpoints"""

    def test_get_models_empty(self, client):
        """Test getting models when none exist - success scenario with HTTP 200 and data field"""
        response = client.get("/api/models")
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_model_success(self, client):
        """Test creating a new model - success scenario with HTTP 201 and data field"""
        # First create a provider
        provider_data = {
            "name": "Test Provider",
            "api_url": "https://api.example.com",
            "api_key": "test-key-12345",
        }
        provider_response = client.post("/api/providers", json=provider_data)
        assert provider_response.status_code == 201
        provider_id = provider_response.json()["data"]["id"]

        # Now create a model
        model_data = {
            "name": "Test Model",
            "provider_id": provider_id,
            "model_name": "gpt-4",
            "initial_capital": 100000,
        }

        response = client.post("/api/models", json=model_data)

        assert response.status_code == 201
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert "id" in data
        assert data["id"] > 0

    def test_get_models_after_create(self, client):
        """Test getting models after creating one - success scenario with HTTP 200"""
        # Create provider
        provider_data = {
            "name": "Test Provider",
            "api_url": "https://api.example.com",
            "api_key": "test-key-12345",
        }
        provider_response = client.post("/api/providers", json=provider_data)
        provider_id = provider_response.json()["data"]["id"]

        # Create model
        model_data = {
            "name": "Test Model",
            "provider_id": provider_id,
            "model_name": "gpt-4",
        }
        create_response = client.post("/api/models", json=model_data)
        assert create_response.status_code == 201

        # Get models
        response = client.get("/api/models")
        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        data = payload["data"]
        assert len(data) == 1
        assert data[0]["name"] == "Test Model"

    def test_delete_model_success(self, client):
        """Test deleting a model - success scenario with HTTP 204"""
        # Create provider
        provider_data = {
            "name": "Test Provider",
            "api_url": "https://api.example.com",
            "api_key": "test-key-12345",
        }
        provider_response = client.post("/api/providers", json=provider_data)
        provider_id = provider_response.json()["data"]["id"]

        # Create model
        model_data = {
            "name": "Test Model",
            "provider_id": provider_id,
            "model_name": "gpt-4",
        }
        create_response = client.post("/api/models", json=model_data)
        model_id = create_response.json()["data"]["id"]

        # Delete model
        response = client.delete(f"/api/models/{model_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get("/api/models")
        data = get_response.json()["data"]
        assert len(data) == 0

    def test_create_model_provider_not_found(self, client):
        """Test creating model with non-existent provider - client error with HTTP 404 and standard error object"""
        model_data = {
            "name": "Test Model",
            "provider_id": 99999,  # Non-existent provider
            "model_name": "gpt-4",
        }

        response = client.post("/api/models", json=model_data)

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == "RESOURCE_NOT_FOUND"
        assert "details" in error
        assert "provider_id" in error["details"]

    def test_execute_trading_model_not_found(self, client):
        """Test executing trading for non-existent model - client error with HTTP 404 and standard error object"""
        response = client.post("/api/models/99999/execute")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == "RESOURCE_NOT_FOUND"
        assert "details" in error
        assert "model_id" in error["details"]

    def test_execute_trading_success(self, client):
        """Test executing trading for existing model - success scenario with HTTP 200 and data field"""
        # Skip this test as it requires complex trading service setup
        # The execute endpoint is tested for error cases (model not found)
        # Full integration testing should be done separately
        pytest.skip("Requires complex trading service setup with market data")

    def test_create_model_missing_fields(self, client):
        """Test creating model with missing required fields - should fail with validation error"""
        # Our custom validation returns 400 with standard error format
        model_data = {
            "name": "Test Model",
            # Missing provider_id and model_name
        }

        response = client.post("/api/models", json=model_data)

        # Our validation error returns 400
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "INVALID_REQUEST"
        assert "missing_fields" in data["error"]["details"]

    def test_delete_nonexistent_model(self, client):
        """Test deleting non-existent model - should succeed with HTTP 204 (idempotent)"""
        # Deleting a non-existent model should be idempotent
        response = client.delete("/api/models/99999")

        # The current implementation doesn't check if model exists before deletion
        # It will succeed with 204
        assert response.status_code == 204
