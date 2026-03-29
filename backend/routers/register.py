"""
backend/routers/register.py
===========================
Cash register operations API endpoints.

Provides endpoints for depositing, withdrawing, and closing shift,
along with viewing register state and transaction history.
"""

from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.models import CashTransaction
from backend.schemas import (
    DepositRequest,
    WithdrawalRequest,
    ShiftCloseRequest,
    RegisterStateResponse,
    CashTransactionResponse,
    CashTransactionListResponse,
)
from backend.services import (
    get_register_state,
    deposit_cash,
    withdraw_cash,
    close_shift,
)

router = APIRouter()


@router.get("", response_model=RegisterStateResponse)
def get_register(
    limit: int = Query(50, ge=1, le=200, description="Number of recent transactions"),
    db: Session = Depends(get_db),
) -> RegisterStateResponse:
    """
    Get current register state.

    Returns current balance and recent cash transactions.
    """
    state = get_register_state(db, limit=limit)

    return RegisterStateResponse(
        current_balance=state["current_balance"],
        transactions=[
            CashTransactionResponse.model_validate(t) for t in state["transactions"]
        ],
    )


@router.post(
    "/deposit",
    response_model=CashTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def deposit(
    request: DepositRequest,
    db: Session = Depends(get_db),
) -> CashTransactionResponse:
    """
    Deposit cash into the register.

    Records a deposit transaction and increases the register balance.
    """
    try:
        transaction = deposit_cash(
            db,
            amount=request.amount,
            note=request.note,
        )
        db.commit()
        return CashTransactionResponse.model_validate(transaction)
    except Exception as e:
        error_str = str(e).lower()
        if "validation" in error_str or "must be positive" in error_str:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": str(e),
                    "code": "VALIDATION_ERROR",
                    "details": None,
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Internal server error",
                    "code": "INTERNAL_ERROR",
                    "details": None,
                },
            )


@router.post(
    "/withdrawal",
    response_model=CashTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def withdraw(
    request: WithdrawalRequest,
    db: Session = Depends(get_db),
) -> CashTransactionResponse:
    """
    Withdraw cash from the register.

    Records a withdrawal transaction and decreases the register balance.
    Returns 422 if insufficient balance.
    """
    try:
        transaction = withdraw_cash(
            db,
            amount=request.amount,
            note=request.note,
        )
        db.commit()
        return CashTransactionResponse.model_validate(transaction)
    except Exception as e:
        error_str = str(e).lower()
        if "insufficient balance" in error_str:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": str(e),
                    "code": "VALIDATION_ERROR",
                    "details": None,
                },
            )
        elif "validation" in error_str or "must be positive" in error_str:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": str(e),
                    "code": "VALIDATION_ERROR",
                    "details": None,
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Internal server error",
                    "code": "INTERNAL_ERROR",
                    "details": None,
                },
            )


@router.post(
    "/close-shift",
    response_model=Union[CashTransactionResponse, dict],
    status_code=status.HTTP_201_CREATED,
)
def close_current_shift(
    request: ShiftCloseRequest,
    db: Session = Depends(get_db),
) -> Union[CashTransactionResponse, dict]:
    """
    Close the current shift.

    Records a shift_close transaction that zeros out the register balance.
    Returns transaction details if balance was non-zero, or a message if balance was zero.
    """
    try:
        transaction = close_shift(db, note=request.note)
        db.commit()

        if transaction is None:
            return {"message": "Shift closed successfully (zero balance)", "balance": 0}

        return CashTransactionResponse.model_validate(transaction)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "code": "INTERNAL_ERROR",
                "details": None,
            },
        )


@router.get("/transactions", response_model=CashTransactionListResponse)
def list_transactions(
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    date_from: Optional[str] = Query(None, description="Filter from date"),
    date_to: Optional[str] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db),
) -> CashTransactionListResponse:
    """
    List cash transactions.

    Returns cash transaction history with optional date filtering and pagination.
    """
    from sqlalchemy import desc

    query = db.query(CashTransaction).order_by(desc(CashTransaction.date))

    if date_from:
        query = query.filter(CashTransaction.date >= date_from)
    if date_to:
        query = query.filter(CashTransaction.date <= date_to)

    # Get total count
    total = query.count()

    # Apply pagination
    transactions = query.offset(offset).limit(limit).all()

    return CashTransactionListResponse(
        data=[CashTransactionResponse.model_validate(t) for t in transactions],
        total=total,
    )
