"""Error handling utilities

Provides custom exception classes and error handling middleware.
"""

import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.api.responses import error_response
from backend.config import error_types

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type or error_types.INTERNAL_SERVER_ERROR
        self.details = details
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to standard error response format"""
        return error_response(
            error_type=self.error_type,
            message=self.message,
            details=self.details
        )


class ValidationError(AppError):
    """Validation error (400)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            status_code=400,
            error_type=error_types.INVALID_REQUEST,
            details=details
        )


class NotFoundError(AppError):
    """Resource not found error (404)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            status_code=404,
            error_type=error_types.RESOURCE_NOT_FOUND,
            details=details
        )


class UnauthorizedError(AppError):
    """Unauthorized error (401)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            status_code=401,
            error_type=error_types.UNAUTHORIZED,
            details=details
        )


class ForbiddenError(AppError):
    """Forbidden error (403)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            status_code=403,
            error_type=error_types.FORBIDDEN,
            details=details
        )


class ConflictError(AppError):
    """Conflict error (409)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            status_code=409,
            error_type=error_types.CONFLICT,
            details=details
        )


class ExternalServiceError(AppError):
    """External service error (502/503)"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            status_code=status_code,
            error_type=error_types.EXTERNAL_SERVICE_ERROR,
            details=details
        )


def register_error_handlers(app: FastAPI) -> None:
    """Register error handlers with FastAPI app."""

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, error: AppError):
        logger.error(
            "Application error: %s",
            error.message,
            extra={"status_code": error.status_code, "error_type": error.error_type, "details": error.details},
        )
        return JSONResponse(status_code=error.status_code, content=error.to_dict())

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, error: StarletteHTTPException):
        logger.warning(
            "HTTP exception: %s", error.detail, extra={"status_code": error.status_code}
        )
        
        # Check if detail is already in standard error format
        if isinstance(error.detail, dict) and 'error' in error.detail:
            # Detail is already a standard error response, use it directly
            content = error.detail
        else:
            # Map HTTP status codes to error types
            error_type_map = {
                400: error_types.INVALID_REQUEST,
                401: error_types.UNAUTHORIZED,
                403: error_types.FORBIDDEN,
                404: error_types.RESOURCE_NOT_FOUND,
                409: error_types.CONFLICT,
                500: error_types.INTERNAL_SERVER_ERROR,
            }
            error_type = error_type_map.get(error.status_code, error_types.INTERNAL_SERVER_ERROR)
            
            # Extract message from detail
            if isinstance(error.detail, dict):
                message = error.detail.get('message', str(error.detail))
                details = {k: v for k, v in error.detail.items() if k != 'message'}
                content = error_response(error_type, message, details if details else None)
            else:
                content = error_response(error_type, str(error.detail))
        
        return JSONResponse(status_code=error.status_code, content=content)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, error: Exception):
        logger.error("Unexpected error: %s", str(error), exc_info=True)
        content = error_response(
            error_types.INTERNAL_SERVER_ERROR,
            "Internal server error"
        )
        return JSONResponse(status_code=500, content=content)
