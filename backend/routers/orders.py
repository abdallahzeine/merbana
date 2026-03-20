"""
backend/routers/orders.py
=========================
Order management API endpoints.

Provides CRUD operations for orders with cash transaction management.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import String
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.models import Order
from backend.schemas import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderSummary,
    OrderListResponse,
    OrderSummaryListResponse,
)
from backend.services import create_order, delete_order, get_next_order_number

router = APIRouter()


@router.get("/next-number", response_model=dict)
def get_next_number(
    db: Session = Depends(get_db),
) -> dict:
    """
    Get the next order number.

    Returns the next available order number (1-100, rolls over after 100).
    """
    next_number = get_next_order_number(db)
    return {"order_number": next_number}


@router.get("", response_model=OrderSummaryListResponse)
def list_orders(
    date_from: Optional[str] = Query(
        None, description="Filter orders from date (inclusive)"
    ),
    date_to: Optional[str] = Query(
        None, description="Filter orders to date (inclusive)"
    ),
    search: Optional[str] = Query(None, description="Search in order notes or numbers"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db),
) -> OrderSummaryListResponse:
    """
    List orders with optional filtering and pagination.

    Returns order summaries for performance (lighter than full order details).
    """
    query = db.query(Order)

    # Apply filters
    if date_from:
        query = query.filter(Order.date >= date_from)
    if date_to:
        query = query.filter(Order.date <= date_to)
    if search:
        # Search in order number or note
        search_term = f"%{search}%"
        query = query.filter(
            (Order.note.ilike(search_term))
            | (Order.order_number.cast(String).like(search_term))
        )

    # Order by date descending (most recent first)
    query = query.order_by(Order.date.desc())

    # Get total count for pagination info
    total = query.count()

    # Apply pagination
    orders = query.offset(offset).limit(limit).all()

    return OrderSummaryListResponse(
        data=[OrderSummary.model_validate(o) for o in orders],
        total=total,
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_new_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
) -> OrderResponse:
    """
    Create a new order.

    Creates an order with items, creates cash transaction,
    and logs the activity. All operations are atomic.
    """
    try:
        db_order = create_order(
            db,
            order_data=order,
            user_id=order.user_id,
            user_name=order.user_name or "System",
        )
        db.commit()

        # Refresh to get items loaded
        db.refresh(db_order)
        return OrderResponse.model_validate(db_order)
    except Exception as e:
        error_str = str(e).lower()
        if "not found" in error_str:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": str(e),
                    "code": "NOT_FOUND",
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


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
) -> OrderResponse:
    """
    Get an order by ID.

    Returns the full order details including all items.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Order with ID '{order_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    return OrderResponse.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_order(
    order_id: str,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete an order.

    Deletes the order, reverses cash transaction,
    and logs the activity. All operations are atomic.
    """
    try:
        delete_order(db, order_id=order_id)
        db.commit()
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": str(e),
                    "code": "NOT_FOUND",
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

    return None
