"""
backend/services/orders.py
==========================
Order creation and deletion workflows with atomic transactions.

Provides functions for:
- Creating orders with cash transaction and activity logging
- Deleting orders with transaction reversal and activity logging
- Calculating next order number with rollover (capped at 100)

All operations are atomic - either all steps succeed or all are rolled back.
Note: Transaction management is handled by the caller (FastAPI routes via get_db).
"""

from typing import Optional
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import Order, OrderItem, CashTransaction
from ..schemas import OrderCreate
from ..errors import NotFoundError
from .activity import log_activity


def get_next_order_number(db: Session) -> int:
    """
    Calculate the next order number with rollover.

    Order numbers are capped at 100 and roll over to 1.

    Args:
        db: Database session

    Returns:
        Next order number (1-100)
    """
    # Get the max order number
    max_number = db.query(func.max(Order.order_number)).scalar()

    if max_number is None:
        return 1

    # Roll over at 100
    next_number = max_number + 1
    if next_number > 100:
        next_number = 1

    return next_number


def create_order(
    db: Session,
    order_data: OrderCreate,
    user_id: Optional[str] = None,
    user_name: str = "System",
) -> Order:
    """
    Create an order with full workflow.

    This is an atomic operation managed by the caller's transaction:
    1. Calculate order_number (max + 1, rollover 1-100)
    2. Calculate total from items
    3. Create order and order_items
    4. Create cash transaction for the sale
    5. Log activity

    Args:
        db: Database session
        order_data: Order creation data
        user_id: User ID creating the order
        user_name: User name creating the order

    Returns:
        Created Order instance

    Raises:
        NotFoundError: If a product doesn't exist
    """
    from datetime import datetime, timezone

    # Step 1: Calculate next order number
    order_number = get_next_order_number(db)

    # Step 2: Calculate total from items
    total = sum(item.subtotal for item in order_data.items)

    # Step 3: Generate IDs and timestamp
    order_id = str(uuid4())
    order_date = datetime.now(timezone.utc).isoformat()

    # Step 5: Create order
    order = Order(
        id=order_id,
        order_number=order_number,
        date=order_date,
        total=total,
        payment_method=order_data.payment_method.value,
        order_type=order_data.order_type.value,
        note=order_data.note,
        user_id=user_id or order_data.user_id,
        user_name=user_name or order_data.user_name or "System",
    )
    db.add(order)
    db.flush()  # Flush to get the order ID

    # Step 4: Create order items
    for item_data in order_data.items:
        order_item = OrderItem(
            id=str(uuid4()),
            order_id=order.id,
            product_id=item_data.product_id,
            name=item_data.name,
            price=item_data.price,
            quantity=item_data.quantity,
            size=item_data.size,
            subtotal=item_data.subtotal,
        )
        db.add(order_item)

    # Step 5: Create cash transaction for the sale
    cash_tx = CashTransaction(
        id=str(uuid4()),
        type="sale",
        amount=total,
        note=f"Order #{order_number}",
        date=order_date,
        order_id=order.id,
        user_id=user_id or order_data.user_id,
    )
    db.add(cash_tx)

    # Step 6: Log activity
    action = f"Order #{order_number} created - Total: ${total:.2f}"
    log_activity(db, user_id, user_name, action)

    return order


def delete_order(
    db: Session,
    order_id: str,
    user_id: Optional[str] = None,
    user_name: str = "System",
) -> None:
    """
    Delete an order with full workflow.

    This is an atomic operation managed by the caller's transaction:
    1. Find the order
    2. Reverse cash transaction (remove sale tx)
    3. Delete order and items
    4. Log activity

    Args:
        db: Database session
        order_id: Order ID to delete
        user_id: User ID deleting the order
        user_name: User name deleting the order

    Raises:
        NotFoundError: If order not found
    """
    # Step 1: Find the order with items
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise NotFoundError(f"Order with id '{order_id}' not found")

    # Store order info before deletion
    order_number = order.order_number
    order_total = order.total

    # Step 2: Reverse cash transaction
    # Find and delete the sale transaction for this order
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

    # Step 3: Delete order items (cascade will handle this, but be explicit)
    for item in order.items:
        db.delete(item)

    # Step 4: Delete the order
    db.delete(order)

    # Step 5: Log activity
    action = f"Order #{order_number} deleted - Total: ${order_total:.2f}"
    log_activity(db, user_id, user_name, action)
