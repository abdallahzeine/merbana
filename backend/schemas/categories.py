"""
backend/schemas/categories.py
===========================
Pydantic schemas for Category entities.

Based on Category model from backend/models.py
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import UUIDstr, ListResponse


class CategoryBase(BaseModel):
    """Base category fields."""

    name: str = Field(max_length=255, description="Category name")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    id: UUIDstr = Field(description="Category ID (UUID)")


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: Optional[str] = Field(
        default=None, max_length=255, description="Category name"
    )


class CategoryResponse(CategoryBase):
    """Full category model for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUIDstr = Field(description="Category ID")


class CategoryWithProductCount(CategoryResponse):
    """Category response with product count for guarded delete checks."""

    model_config = ConfigDict(from_attributes=True)

    product_count: int = Field(
        default=0, description="Number of products in this category"
    )


class CategoryListResponse(ListResponse[CategoryWithProductCount]):
    """Response wrapper for listing categories."""

    pass
