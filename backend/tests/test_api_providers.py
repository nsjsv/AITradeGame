"""Tests for provider API endpoints"""

import pytest
import json


class TestProviderAPI:
    """Test provider API endpoints"""
    
    def test_get_providers_empty(self, client):
        """Test getting providers when none exist"""
        response = client.get('/api/providers')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_provider(self, client):
        """Test creating a new provider"""
        provider_data = {
            'name': 'Test Provider',
            'api_url': 'https://api.example.com',
            'api_key': 'test-key-12345',
            'models': 'gpt-4,gpt-3.5-turbo'
        }
        
        response = client.post(
            '/api/providers',
            data=json.dumps(provider_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'id' in data
        assert 'message' in data
        assert data['id'] > 0
    
    def test_get_providers_after_create(self, client):
        """Test getting providers after creating one"""
        # Create provider
        provider_data = {
            'name': 'Test Provider',
            'api_url': 'https://api.example.com',
            'api_key': 'test-key-12345',
            'models': 'gpt-4'
        }
        
        create_response = client.post(
            '/api/providers',
            data=json.dumps(provider_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        
        # Get providers
        response = client.get('/api/providers')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == 'Test Provider'
        # API key should be masked
        assert '...' in data[0]['api_key'] or data[0]['api_key'] == '***'
    
    def test_delete_provider(self, client):
        """Test deleting a provider"""
        # Create provider
        provider_data = {
            'name': 'Test Provider',
            'api_url': 'https://api.example.com',
            'api_key': 'test-key-12345'
        }
        
        create_response = client.post(
            '/api/providers',
            data=json.dumps(provider_data),
            content_type='application/json'
        )
        provider_id = json.loads(create_response.data)['id']
        
        # Delete provider
        response = client.delete(f'/api/providers/{provider_id}')
        assert response.status_code == 200
        
        # Verify deleted
        get_response = client.get('/api/providers')
        data = json.loads(get_response.data)
        assert len(data) == 0
    
    def test_create_provider_missing_fields(self, client):
        """Test creating provider with missing required fields"""
        provider_data = {
            'name': 'Test Provider'
            # Missing api_url and api_key
        }
        
        response = client.post(
            '/api/providers',
            data=json.dumps(provider_data),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
