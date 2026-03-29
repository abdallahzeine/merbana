"""
backend/services/register.py
============================
Cash register operations service.

Provides functions for:
- Getting register state (balance + transactions)
- Depositing cash
- Withdrawing cash
- Closing shift
- Adding/reversing sale transactions (internal)

All cash transactions are recorded for audit purposes.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models import CashTransaction, Order
from ..schemas import DepositRequest, WithdrawalRequest, ShiftCloseRequest
from ..errors import NotFoundError, ValidationError
from .activity import log_activity


def get_register_state(
    db: Session,
    limit: int = 50,
) -> dict:
    """
    Get current register state including balance and recent transactions.

    Args:
        db: Database session
        limit: Maximum number of recent transactions to return

    Returns:
        Dictionary with current_balance and transactions list
    """
    # Calculate current balance from all transactions
    transactions = (
        db.query(CashTransaction)
        .order_by(desc(CashTransaction.date))
        .limit(limit)
        .all()
    )

    # Calculate balance
    current_balance = 0.0
    for tx in db.query(CashTransaction).all():
        if tx.type in ["sale", "deposit"]:
            current_balance += tx.amount
        elif tx.type in ["withdrawal", "shift_close"]:
            current_balance -= tx.amount

    return {
        "current_balance": current_balance,
        "transactions": transactions,
    }


def deposit_cash(
    db: Session,
    amount: float,
    note: Optional[str] = None,
    user_id: Optional[str] = None,
    user_name: str = "System",
) -> CashTransaction:
    """
    Add cash to the register.

    Args:
        db: Database session
        amount: Amount to deposit (positive)
        note: Optional note
        user_id: User ID making the deposit
        user_name: User name making the deposit

    Returns:
        Created CashTransaction instance
    """
    if amount <= 0:
        raise ValidationError("Deposit amount must be positive")

    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    transaction = CashTransaction(
        id=str(uuid4()),
        type="deposit",
        amount=amount,
        note=note or "Cash deposit",
        date=timestamp,
        order_id=None,
        user_id=user_id,
    )

    db.add(transaction)

    # Log activity
    action = f"Cash deposit: ${amount:.2f}"
    if note:
        action += f" ({note})"
    log_activity(db, user_id, user_name, action)

    return transaction


def withdraw_cash(
    db: Session,
    amount: float,
    note: Optional[str] = None,
    user_id: Optional[str] = None,
    user_name: str = "System",
) -> CashTransaction:
    """
    Remove cash from the register.

    Args:
        db: Database session
        amount: Amount to withdraw (positive value)
        note: Optional note
        user_id: User ID making the withdrawal
        user_name: User name making the withdrawal

    Returns:
        Created CashTransaction instance

    Raises:
        ValidationError: If amount exceeds current balance
    """
    if amount <= 0:
        raise ValidationError("Withdrawal amount must be positive")

    # Check if sufficient balance
    state = get_register_state(db)
    if state["current_balance"] < amount:
        raise ValidationError(
            "Insufficient balance for withdrawal",
            details={
                "requested": amount,
                "available": state["current_balance"],
            },
        )

    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    transaction = CashTransaction(
        id=str(uuid4()),
        type="withdrawal",
        amount=amount,
        note=note or "Cash withdrawal",
        date=timestamp,
        order_id=None,
        user_id=user_id,
    )

    db.add(transaction)

    # Log activity
    action = f"Cash withdrawal: ${amount:.2f}"
    if note:
        action += f" ({note})"
    log_activity(db, user_id, user_name, action)

    return transaction


def close_shift(
    db: Session,
    note: Optional[str] = None,
    user_id: Optional[str] = None,
    user_name: str = "System",
) -> Optional[CashTransaction]:
    """
    Close the current shift.

    Records a shift_close transaction and zeros out the balance.
    Returns None if balance was zero (no transaction created).

    Args:
        db: Database session
        note: Optional note
        user_id: User ID closing the shift
        user_name: User name closing the shift

    Returns:
        Created CashTransaction instance for the shift close, or None if balance was zero
    """
    state = get_register_state(db)
    current_balance = state["current_balance"]

    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    action = f"Shift closed - Balance: ${current_balance:.2f}"
    if note:
        action += f" ({note})"
    log_activity(db, user_id, user_name, action)

    if current_balance <= 0:
        return None

    transaction = CashTransaction(
        id=str(uuid4()),
        type="shift_close",
        amount=current_balance,
        note=note or "Shift closed",
        date=timestamp,
        order_id=None,
        user_id=user_id,
    )

    db.add(transaction)

    return transaction


def add_sale_transaction(
    db: Session,
    order_id: str,
    amount: float,
    user_id: Optional[str] = None,
) -> CashTransaction:
    """
    Internal: Add a sale transaction when an order is created.

    Args:
        db: Database session
        order_id: Associated order ID
        amount: Sale amount
        user_id: User ID who created the order

    Returns:
        Created CashTransaction instance
    """
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    transaction = CashTransaction(
        id=str(uuid4()),
        type="sale",
        amount=amount,
        note=f"Sale for order",
        date=timestamp,
        order_id=order_id,
        user_id=user_id,
    )

    db.add(transaction)

    return transaction


def reverse_sale_transaction(
    db: Session,
    order_id: str,
) -> None:
    """
    Internal: Reverse (delete) a sale transaction when an order is deleted.

    Args:
        db: Database session
        order_id: Associated order ID
    """
    sale_tx = (
        db.query(CashTransaction)
        .filter(
            CashTransaction.order_id == order_id,
            CashTransaction.type == "sale",
        )
        .first()
    )

    if sale_tx:
        db.delete(sale_tx)
