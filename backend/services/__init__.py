"""
backend/services/__init__.py
============================
Service layer for the Merbana backend.

This module provides business logic services for multi-entity workflows.
All services accept SQLAlchemy Session as a parameter for dependency injection
and testability outside the HTTP layer.

Service Layer Responsibilities:
- Encapsulate business logic and multi-entity workflows
- Manage database transactions (atomic operations)
- Handle side effects (cash transactions, activity logging)
- Provide reusable business operations for API routers
- Ensure data consistency across related entities

Transaction Management:
All multi-step workflows use explicit transaction boundaries:
    try:
        with db.begin():
            # All operations are atomic
            pass
    except Exception:
        # Automatic rollback
        raise

Services:
- activity: Activity logging and querying
- orders: Order creation and deletion workflows
- register: Cash register operations
- settings: Application settings management
- categories: Category management with guarded delete
"""

from .activity import log_activity, get_activity_logs
from .orders import create_order, delete_order, get_next_order_number
from .register import (
    get_register_state,
    deposit_cash,
    withdraw_cash,
    close_shift,
    add_sale_transaction,
    reverse_sale_transaction,
)
from .settings import (
    get_or_create_settings,
    update_settings,
    get_password_requirements,
    update_password_requirement,
    initialize_default_password_requirements,
)
from .categories import (
    get_categories_with_counts,
    can_delete_category,
    delete_category_guarded,
)

__all__ = [
    # Activity
    "log_activity",
    "get_activity_logs",
    # Orders
    "create_order",
    "delete_order",
    "get_next_order_number",
    # Register
    "get_register_state",
    "deposit_cash",
    "withdraw_cash",
    "close_shift",
    "add_sale_transaction",
    "reverse_sale_transaction",
    # Settings
    "get_or_create_settings",
    "update_settings",
    "get_password_requirements",
    "update_password_requirement",
    "initialize_default_password_requirements",
    # Categories
    "get_categories_with_counts",
    "can_delete_category",
    "delete_category_guarded",
]
