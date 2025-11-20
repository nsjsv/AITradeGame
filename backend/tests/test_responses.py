"""Tests for API response helpers"""

import pytest
from backend.api.responses import success_response, error_response


class TestSuccessResponse:
    """Test success_response helper"""
    
    def test_success_response_with_data(self):
        """Test success response with data"""
        data = {"id": 1, "name": "test"}
        response = success_response(data)
        
        assert "data" in response
        assert response["data"] == data
        assert "meta" not in response
    
    def test_success_response_with_meta(self):
        """Test success response with metadata"""
        data = [1, 2, 3]
        meta = {"page": 1, "total": 100}
        response = success_response(data, meta)
        
        assert response["data"] == data
        assert response["meta"] == meta
    
    def test_success_response_with_none(self):
        """Test success response with None data"""
        response = success_response(None)
        
        assert "data" in response
        assert response["data"] is None


class TestErrorResponse:
    """Test error_response helper"""
    
    def test_error_response_basic(self):
        """Test basic error response"""
        response = error_response("INVALID_REQUEST", "Invalid input")
        
        assert "error" in response
        assert response["error"]["code"] == "INVALID_REQUEST"
        assert response["error"]["message"] == "Invalid input"
        assert "details" not in response["error"]
    
    def test_error_response_with_details(self):
        """Test error response with details"""
        details = {"field": "email", "reason": "invalid format"}
        response = error_response("INVALID_FORMAT", "Email format is invalid", details)
        
        assert response["error"]["code"] == "INVALID_FORMAT"
        assert response["error"]["message"] == "Email format is invalid"
        assert response["error"]["details"] == details
    
    def test_error_response_without_details(self):
        """Test that details field is optional"""
        response = error_response("NOT_FOUND", "Resource not found")
        
        assert "error" in response
        assert "code" in response["error"]
        assert "message" in response["error"]
        assert "details" not in response["error"]
    
    def test_error_type_upper_snake_case(self):
        """Test that error types follow UPPER_SNAKE_CASE convention"""
        test_cases = [
            "INVALID_REQUEST",
            "RESOURCE_NOT_FOUND",
            "INSUFFICIENT_BALANCE",
            "INTERNAL_SERVER_ERROR"
        ]
        
        for error_type in test_cases:
            response = error_response(error_type, "Test message")
            assert response["error"]["code"] == error_type
            # Verify it's uppercase
            assert error_type.isupper()
            # Verify it uses underscores
            assert "_" in error_type or error_type.isalpha()
    
    def test_error_response_structure(self):
        """Test complete error response structure"""
        details = {"required": 1000, "available": 500}
        response = error_response(
            "INSUFFICIENT_BALANCE",
            "Account balance too low",
            details
        )
        
        # Verify structure
        assert isinstance(response, dict)
        assert "error" in response
        assert isinstance(response["error"], dict)
        assert set(response["error"].keys()) == {"code", "message", "details"}
