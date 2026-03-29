"""
backend/schemas/errors.py
=========================
Error response schemas for standardized API error handling.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    """Field-level error detail."""

    model_config = ConfigDict(from_attributes=True)

    loc: List[str] = Field(
        description="Location of the error (e.g., ['body', 'field_name'])"
    )
    msg: str = Field(description="Error message")
    type: str = Field(description="Error type")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    model_config = ConfigDict(from_attributes=True)

    error: str = Field(description="Human-readable error message")
    code: str = Field(description="Machine-readable error code")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error context"
    )
    validation_errors: Optional[List[ErrorDetail]] = Field(
        default=None,
        description="Validation error details (Pydantic validation failures)",
    )


def error_response_from_exception(
    message: str,
    code: str,
    details: Optional[Dict[str, Any]] = None,
) -> ErrorResponse:
    """
    Create an ErrorResponse from exception information.

    Args:
        message: Human-readable error message
        code: Machine-readable error code
        details: Optional additional error context

    Returns:
        ErrorResponse instance
    """
    return ErrorResponse(
        error=message,
        code=code,
        details=details,
    )
