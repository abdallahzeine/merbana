"""
backend/schemas/common.py
=========================
Common Pydantic types and utilities for schema validation.

Provides reusable type aliases and generic response wrappers.
"""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

UUIDstr = Annotated[str, StringConstraints(pattern=r"^[0-9a-f-]{36}$")]

TimestampStr = Annotated[
    str,
    Field(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?$"
    ),
]

T = TypeVar("T")


class ListResponse(BaseModel, Generic[T]):
    """Generic wrapper for list endpoints."""

    model_config = ConfigDict(from_attributes=True)

    data: List[T] = []
    total: Optional[int] = None


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=50, ge=1, le=100, description="Max records to return")
