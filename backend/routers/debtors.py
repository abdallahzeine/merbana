"""
backend/routers/debtors.py
==========================
Debtor management API endpoints.

Provides CRUD operations for debt tracking with payment status.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.models import Debtor
from backend.schemas import (
    DebtorCreate,
    DebtorUpdate,
    DebtorResponse,
    DebtorListResponse,
    MarkPaidRequest,
)
from backend.services.activity import log_activity

router = APIRouter()


@router.get("", response_model=DebtorListResponse)
def list_debtors(
    status: Optional[str] = Query("all", description="Filter: unpaid|paid|all"),
    db: Session = Depends(get_db),
) -> DebtorListResponse:
    """
    List debtors.

    Optional status filter:
    - unpaid: Only unpaid debtors (paid_at is null)
    - paid: Only paid debtors (paid_at is not null)
    - all: All debtors (default)
    """
    query = db.query(Debtor)

    if status == "unpaid":
        query = query.filter(Debtor.paid_at.is_(None))
    elif status == "paid":
        query = query.filter(Debtor.paid_at.isnot(None))

    debtors = query.order_by(Debtor.created_at.desc()).all()
    return DebtorListResponse(data=[DebtorResponse.model_validate(d) for d in debtors])


@router.post("", response_model=DebtorResponse, status_code=status.HTTP_201_CREATED)
def create_debtor(
    debtor: DebtorCreate,
    db: Session = Depends(get_db),
) -> DebtorResponse:
    """
    Create a new debtor.

    Creates a debtor record with the specified details.
    """
    # Check for duplicate ID
    existing = db.query(Debtor).filter(Debtor.id == debtor.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": f"Debtor with ID '{debtor.id}' already exists",
                "code": "DUPLICATE_ID",
                "details": None,
            },
        )

    db_debtor = Debtor(
        id=debtor.id,
        name=debtor.name,
        amount=debtor.amount,
        note=debtor.note,
        created_at=debtor.created_at,
        paid_at=None,
    )
    db.add(db_debtor)
    db.commit()
    db.refresh(db_debtor)

    # Log activity
    action = f"Debtor '{debtor.name}' added - Amount: ${debtor.amount:.2f}"
    log_activity(db, None, "System", action)
    db.commit()

    return DebtorResponse.model_validate(db_debtor)


@router.get("/{debtor_id}", response_model=DebtorResponse)
def get_debtor(
    debtor_id: str,
    db: Session = Depends(get_db),
) -> DebtorResponse:
    """
    Get a debtor by ID.

    Returns the debtor details including payment status.
    """
    debtor = db.query(Debtor).filter(Debtor.id == debtor_id).first()
    if not debtor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Debtor with ID '{debtor_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    return DebtorResponse.model_validate(debtor)


@router.put("/{debtor_id}", response_model=DebtorResponse)
def update_debtor(
    debtor_id: str,
    debtor_update: DebtorUpdate,
    db: Session = Depends(get_db),
) -> DebtorResponse:
    """
    Update a debtor.

    Updates the debtor's note and/or paid_at status.
    """
    db_debtor = db.query(Debtor).filter(Debtor.id == debtor_id).first()
    if not db_debtor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Debtor with ID '{debtor_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    if debtor_update.note is not None:
        db_debtor.note = debtor_update.note
    if debtor_update.paid_at is not None:
        db_debtor.paid_at = debtor_update.paid_at

    db.commit()
    db.refresh(db_debtor)

    return DebtorResponse.model_validate(db_debtor)


@router.post("/{debtor_id}/mark-paid", response_model=DebtorResponse)
def mark_debtor_paid(
    debtor_id: str,
    request: MarkPaidRequest,
    db: Session = Depends(get_db),
) -> DebtorResponse:
    """
    Mark a debtor as paid.

    Sets the paid_at timestamp. Uses current time if not provided.
    """
    db_debtor = db.query(Debtor).filter(Debtor.id == debtor_id).first()
    if not db_debtor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Debtor with ID '{debtor_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    # Set paid timestamp
    if request.paid_at:
        db_debtor.paid_at = request.paid_at
    else:
        # Default to current timestamp in JS format
        db_debtor.paid_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    db.commit()
    db.refresh(db_debtor)

    # Log activity
    action = (
        f"Debtor '{db_debtor.name}' marked as paid - Amount: ${db_debtor.amount:.2f}"
    )
    log_activity(db, None, "System", action)
    db.commit()

    return DebtorResponse.model_validate(db_debtor)


@router.delete("/{debtor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_debtor(
    debtor_id: str,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a debtor.

    Permanently removes the debtor record.
    """
    db_debtor = db.query(Debtor).filter(Debtor.id == debtor_id).first()
    if not db_debtor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Debtor with ID '{debtor_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    # Log activity before deletion
    action = f"Debtor '{db_debtor.name}' deleted - Amount: ${db_debtor.amount:.2f}"
    log_activity(db, None, "System", action)

    db.delete(db_debtor)
    db.commit()

    return None
