"""
backend/schemas/users.py
=======================
Pydantic schemas for User entities.

Based on StoreUser model from backend/models.py
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import UUIDstr, TimestampStr, ListResponse


class UserBase(BaseModel):
    """Base user fields."""

    name: str = Field(max_length=255, description="User's display name")
    password: Optional[str] = Field(
        default=None, max_length=255, description="User password (nullable for display)"
    )


class UserCreate(UserBase):
    """Schema for creating a new user."""

    id: UUIDstr = Field(description="User ID (UUID)")
    created_at: TimestampStr = Field(description="Creation timestamp")


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    name: Optional[str] = Field(
        default=None, max_length=255, description="User's display name"
    )
    password: Optional[str] = Field(
        default=None, max_length=255, description="User password"
    )


class UserResponse(UserBase):
    """Full user model for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUIDstr = Field(description="User ID")
    created_at: TimestampStr = Field(description="Creation timestamp")


class UserListResponse(ListResponse[UserResponse]):
    """Response wrapper for listing users."""

    pass
