"""
backend/schemas/debtors.py
=========================
Pydantic schemas for Debtor entities.

Based on Debtor model from backend/models.py
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import UUIDstr, TimestampStr, ListResponse


class DebtorBase(BaseModel):
    """Base debtor fields."""

    name: str = Field(max_length=255, description="Debtor name")
    amount: float = Field(ge=0, description="Debt amount")
    note: Optional[str] = Field(default=None, description="Debtor note")


class DebtorCreate(DebtorBase):
    """Schema for creating a new debtor."""

    id: UUIDstr = Field(description="Debtor ID (UUID)")
    created_at: TimestampStr = Field(description="Creation timestamp")


class DebtorUpdate(BaseModel):
    """Schema for updating a debtor."""

    note: Optional[str] = Field(default=None, description="Debtor note")
    paid_at: Optional[TimestampStr] = Field(
        default=None, description="Payment timestamp"
    )


class DebtorResponse(DebtorBase):
    """Full debtor model for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUIDstr = Field(description="Debtor ID")
    created_at: TimestampStr = Field(description="Creation timestamp")
    paid_at: Optional[TimestampStr] = Field(
        default=None, description="Payment timestamp"
    )


class DebtorListResponse(ListResponse[DebtorResponse]):
    """Response wrapper for listing debtors."""

    pass


class MarkPaidRequest(BaseModel):
    """Request schema for marking a debtor as paid."""

    paid_at: Optional[TimestampStr] = Field(
        default=None, description="Payment timestamp (defaults to now if not provided)"
    )
