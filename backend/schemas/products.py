"""
backend/schemas/products.py
===========================
Pydantic schemas for Product and ProductSize entities.

Based on Product and ProductSize models from backend/models.py
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import UUIDstr, TimestampStr, ListResponse


class ProductSizeBase(BaseModel):
    """Base product size fields."""

    name: str = Field(
        max_length=100, description="Size name (e.g., 'Small', 'Medium', 'Large')"
    )
    price: float = Field(ge=0, description="Price for this size")


class ProductSizeCreate(ProductSizeBase):
    """Schema for creating a product size."""

    id: UUIDstr = Field(description="Size ID (UUID)")
    sort_order: int = Field(default=0, description="Sort order for display")


class ProductSizeResponse(ProductSizeBase):
    """Full product size model for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUIDstr = Field(description="Size ID")
    sort_order: int = Field(description="Sort order for display")


class ProductBase(BaseModel):
    """Base product fields."""

    name: str = Field(max_length=255, description="Product name")
    price: float = Field(ge=0, description="Base price")
    category_id: Optional[UUIDstr] = Field(default=None, description="Category ID")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    id: UUIDstr = Field(description="Product ID (UUID)")
    created_at: TimestampStr = Field(description="Creation timestamp")
    sizes: List[ProductSizeCreate] = Field(
        default_factory=list, description="Product sizes"
    )


class ProductUpdate(BaseModel):
    """Schema for updating a product."""

    name: Optional[str] = Field(
        default=None, max_length=255, description="Product name"
    )
    price: Optional[float] = Field(default=None, ge=0, description="Base price")
    category_id: Optional[UUIDstr] = Field(default=None, description="Category ID")
    sizes: Optional[List[ProductSizeCreate]] = Field(
        default=None, description="Product sizes"
    )


class ProductResponse(ProductBase):
    """Full product model for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUIDstr = Field(description="Product ID")
    created_at: TimestampStr = Field(description="Creation timestamp")
    sizes: List[ProductSizeResponse] = Field(
        default_factory=list, description="Product sizes"
    )
    category_name: Optional[str] = Field(
        default=None, description="Category name (for response)"
    )


class ProductListResponse(ListResponse[ProductResponse]):
    """Response wrapper for listing products."""

    pass
