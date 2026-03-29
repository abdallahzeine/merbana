"""
backend/errors.py
=================
Error handling and custom exceptions for the Merbana backend.

Provides standardized error responses and exception classes
for consistent API error handling.
"""

from typing import Any, Dict, Optional


class ErrorCode:
    """Standard error codes for API responses."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    DUPLICATE_ID = "DUPLICATE_ID"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AppError(Exception):
    """
    Base exception class for application errors.

    Attributes:
        message: Human-readable error message
        code: Machine-readable error code (use ErrorCode constants)
        details: Optional dictionary with additional error context
        status_code: HTTP status code for this error
    """

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format for JSON response."""
        return {
            "error": self.message,
            "code": self.code,
            "details": self.details,
        }


class ValidationError(AppError):
    """Raised when request data fails validation."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            details=details,
            status_code=422,
        )


class NotFoundError(AppError):
    """Raised when a requested entity doesn't exist."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.NOT_FOUND,
            details=details,
            status_code=404,
        )


class ConflictError(AppError):
    """Raised when an operation conflicts with existing state (e.g., category has products)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.CONFLICT,
            details=details,
            status_code=409,
        )


class DuplicateIdError(AppError):
    """Raised when attempting to create an entity with an ID that already exists."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.DUPLICATE_ID,
            details=details,
            status_code=409,
        )


class InternalError(AppError):
    """Raised when an unexpected server error occurs."""

    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INTERNAL_ERROR,
            details=details,
            status_code=500,
        )


def error_response(
    message: str,
    code: str = ErrorCode.INTERNAL_ERROR,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.

    Standard error response shape:
    {
        "error": str,
        "code": str,
        "details": dict | null
    }

    Args:
        message: Human-readable error message
        code: Machine-readable error code
        details: Optional additional error context

    Returns:
        Dictionary formatted for JSON error response
    """
    return {
        "error": message,
        "code": code,
        "details": details,
    }
