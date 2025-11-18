"""Tests for error handling"""

import pytest
from backend.utils.errors import (
    AppError,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    ExternalServiceError
)


class TestErrors:
    """Test error classes"""
    
    def test_app_error(self):
        """Test base AppError"""
        error = AppError("Test error", status_code=500)
        assert error.message == "Test error"
        assert error.status_code == 500
        assert error.details == {}
        
        error_dict = error.to_dict()
        assert error_dict['error'] == "Test error"
    
    def test_app_error_with_details(self):
        """Test AppError with details"""
        details = {'field': 'value', 'count': 42}
        error = AppError("Test error", details=details)
        
        error_dict = error.to_dict()
        assert error_dict['error'] == "Test error"
        assert error_dict['details'] == details
    
    def test_validation_error(self):
        """Test ValidationError"""
        error = ValidationError("Invalid input")
        assert error.status_code == 400
        assert error.message == "Invalid input"
    
    def test_not_found_error(self):
        """Test NotFoundError"""
        error = NotFoundError("Resource not found")
        assert error.status_code == 404
    
    def test_unauthorized_error(self):
        """Test UnauthorizedError"""
        error = UnauthorizedError("Unauthorized")
        assert error.status_code == 401
    
    def test_forbidden_error(self):
        """Test ForbiddenError"""
        error = ForbiddenError("Forbidden")
        assert error.status_code == 403
    
    def test_conflict_error(self):
        """Test ConflictError"""
        error = ConflictError("Conflict")
        assert error.status_code == 409
    
    def test_external_service_error(self):
        """Test ExternalServiceError"""
        error = ExternalServiceError("Service unavailable", status_code=503)
        assert error.status_code == 503
