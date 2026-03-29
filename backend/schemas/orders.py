"""
backend/schemas/orders.py
=========================
Pydantic schemas for Order and OrderItem entities.

Based on Order and OrderItem models from backend/models.py
"""

from enum import Enum
from typing import List, Optional

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .common import UUIDstr, TimestampStr, ListResponse


class PaymentMethod(str, Enum):
    """Payment method options."""

    CASH = "cash"
    SHAMCASH = "shamcash"


class OrderType(str, Enum):
    """Order type options."""

    DINE_IN = "dine_in"
    TAKEAWAY = "takeaway"


class OrderItemCreate(BaseModel):
    """Schema for creating an order item."""

    product_id: UUIDstr = Field(description="Product ID")
    name: str = Field(max_length=255, description="Product name at time of order")
    price: float = Field(ge=0, description="Unit price at time of order")
    quantity: int = Field(gt=0, description="Quantity ordered")
    size: Optional[str] = Field(
        default=None, max_length=100, description="Size variant"
    )
    subtotal: float = Field(ge=0, description="Line item subtotal")


class OrderItemResponse(BaseModel):
    """Full order item model for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUIDstr = Field(description="Order item ID")
    order_id: UUIDstr = Field(description="Order ID")
    product_id: Optional[UUIDstr] = Field(
        default=None, description="Product ID (nullable for historical)"
    )
    name: str = Field(max_length=255, description="Product name at time of order")
    price: float = Field(description="Unit price at time of order")
    quantity: int = Field(description="Quantity ordered")
    size: Optional[str] = Field(default=None, description="Size variant")
    subtotal: float = Field(description="Line item subtotal")


class OrderBase(BaseModel):
    """Base order fields."""

    order_number: int = Field(description="Order number")
    date: TimestampStr = Field(description="Order date/time")
    total: float = Field(ge=0, description="Order total")
    payment_method: PaymentMethod = Field(description="Payment method")
    order_type: OrderType = Field(description="Order type")
    note: Optional[str] = Field(default=None, description="Order note")
    user_id: Optional[UUIDstr] = Field(
        default=None, description="User ID who created the order"
    )
    user_name: Optional[str] = Field(
        default=None, max_length=255, description="User name who created the order"
    )


class OrderCreate(BaseModel):
    """Schema for creating a new order."""

    payment_method: PaymentMethod = Field(description="Payment method")
    order_type: OrderType = Field(description="Order type")
    note: Optional[str] = Field(default=None, description="Order note")
    user_id: Optional[UUIDstr] = Field(
        default=None, description="User ID who created the order"
    )
    user_name: Optional[str] = Field(
        default=None, max_length=255, description="User name who created the order"
    )
    items: List[OrderItemCreate] = Field(min_length=1, description="Order items")


class OrderUpdate(BaseModel):
    """Schema for updating an order."""

    note: Optional[str] = Field(default=None, description="Order note")


class OrderResponse(OrderBase):
    """Full order model for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUIDstr = Field(description="Order ID")
    items: List[OrderItemResponse] = Field(
        default_factory=list, description="Order items"
    )


class OrderSummary(BaseModel):
    """Minimal order fields for list endpoints (performance-optimized)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUIDstr = Field(description="Order ID")
    order_number: int = Field(description="Order number")
    date: TimestampStr = Field(description="Order date")
    total: float = Field(description="Order total")


class OrderListResponse(ListResponse[OrderResponse]):
    """Response wrapper for listing orders."""

    pass


class OrderSummaryListResponse(ListResponse[OrderSummary]):
    """Response wrapper for listing order summaries."""

    pass
