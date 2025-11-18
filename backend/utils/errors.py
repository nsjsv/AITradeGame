"""Error handling utilities

Provides custom exception classes and error handling middleware.
"""

import logging
from typing import Dict, Any, Optional
from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        error_dict = {
            'error': self.message
        }
        if self.details:
            error_dict['details'] = self.details
        return error_dict


class ValidationError(AppError):
    """Validation error (400)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class NotFoundError(AppError):
    """Resource not found error (404)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class UnauthorizedError(AppError):
    """Unauthorized error (401)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class ForbiddenError(AppError):
    """Forbidden error (403)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class ConflictError(AppError):
    """Conflict error (409)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, details=details)


class ExternalServiceError(AppError):
    """External service error (502/503)"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=status_code, details=details)


def register_error_handlers(app):
    """Register error handlers with Flask app
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        """Handle custom application errors"""
        logger.error(
            f"Application error: {error.message}",
            extra={'status_code': error.status_code, 'details': error.details}
        )
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle HTTP exceptions"""
        logger.warning(
            f"HTTP exception: {error.description}",
            extra={'status_code': error.code}
        )
        return jsonify({'error': error.description}), error.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        """Handle unexpected errors"""
        logger.error(
            f"Unexpected error: {str(error)}",
            exc_info=True
        )
        # Don't expose internal error details in production
        return jsonify({
            'error': 'Internal server error'
        }), 500
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors"""
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors"""
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
