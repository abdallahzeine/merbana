"""
backend/schemas/register.py
===========================
Pydantic schemas for CashTransaction (register) entities.

Based on CashTransaction model from backend/models.py
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import UUIDstr, TimestampStr, ListResponse


class TransactionType(str, Enum):
    """Transaction type options."""

    SALE = "sale"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    SHIFT_CLOSE = "shift_close"


class CashTransactionBase(BaseModel):
    """Base cash transaction fields."""

    type: TransactionType = Field(description="Transaction type")
    # gt=0 constraint: zero-amount transactions are rejected
    amount: float = Field(gt=0, description="Transaction amount")
    note: Optional[str] = Field(default=None, description="Transaction note")
    order_id: Optional[UUIDstr] = Field(default=None, description="Associated order ID")
    user_id: Optional[UUIDstr] = Field(
        default=None, description="User who created the transaction"
    )


class CashTransactionCreate(CashTransactionBase):
    """Schema for creating a new cash transaction."""

    id: UUIDstr = Field(description="Transaction ID (UUID)")
    date: TimestampStr = Field(description="Transaction date/time")


class CashTransactionResponse(CashTransactionBase):
    """Full cash transaction model for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUIDstr = Field(description="Transaction ID")
    date: TimestampStr = Field(description="Transaction date/time")


class CashTransactionListResponse(ListResponse[CashTransactionResponse]):
    """Response wrapper for listing cash transactions."""

    pass


class DepositRequest(BaseModel):
    """Request schema for depositing cash."""

    amount: float = Field(gt=0, description="Amount to deposit (positive value)")
    note: Optional[str] = Field(default=None, description="Deposit note")


class WithdrawalRequest(BaseModel):
    """Request schema for withdrawing cash. Service layer converts to negative."""

    amount: float = Field(
        gt=0,
        description="Amount to withdraw (positive value, converted to negative by service)",
    )
    note: Optional[str] = Field(default=None, description="Withdrawal note")


class ShiftCloseRequest(BaseModel):
    """Request schema for closing shift."""

    note: Optional[str] = Field(default=None, description="Shift close note")


class RegisterStateResponse(BaseModel):
    """Response schema for register state."""

    current_balance: float = Field(description="Current register balance")
    transactions: List[CashTransactionResponse] = Field(
        default_factory=list, description="Recent transactions"
    )
