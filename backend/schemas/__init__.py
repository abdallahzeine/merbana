"""
backend/schemas/__init__.py
===========================
Pydantic schemas for Merbana Backend API.

Provides request/response validation models for all entities.
"""

# Common types
from .common import (
    UUIDstr,
    TimestampStr,
    ListResponse,
    PaginationParams,
)

# Error schemas
from .errors import (
    ErrorDetail,
    ErrorResponse,
    error_response_from_exception,
)

# User schemas
from .users import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
)

# Category schemas
from .categories import (
    CategoryBase,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithProductCount,
    CategoryListResponse,
)

# Product schemas
from .products import (
    ProductSizeBase,
    ProductSizeCreate,
    ProductSizeResponse,
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)

# Order schemas
from .orders import (
    PaymentMethod,
    OrderType,
    OrderItemCreate,
    OrderItemResponse,
    OrderBase,
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderSummary,
    OrderListResponse,
    OrderSummaryListResponse,
)

# Register (CashTransaction) schemas
from .register import (
    TransactionType,
    CashTransactionBase,
    CashTransactionCreate,
    CashTransactionResponse,
    CashTransactionListResponse,
    DepositRequest,
    WithdrawalRequest,
    ShiftCloseRequest,
    RegisterStateResponse,
)

# Debtor schemas
from .debtors import (
    DebtorBase,
    DebtorCreate,
    DebtorUpdate,
    DebtorResponse,
    DebtorListResponse,
    MarkPaidRequest,
)

# Settings schemas
from .settings import (
    SensitiveActionKey,
    PasswordRequirementBase,
    PasswordRequirementCreate,
    PasswordRequirementResponse,
    PasswordRequirementMap,
    SecuritySettings,
    SettingsBase,
    SettingsCreate,
    SettingsUpdate,
    SettingsResponse,
)


# Activity log schemas
from .activity import (
    ActivityLogBase,
    ActivityLogCreate,
    ActivityLogResponse,
    ActivityLogListResponse,
    ActivityLogFilter,
)

__all__ = [
    # Common
    "UUIDstr",
    "TimestampStr",
    "ListResponse",
    "PaginationParams",
    # Errors
    "ErrorDetail",
    "ErrorResponse",
    "error_response_from_exception",
    # Users
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    # Categories
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryWithProductCount",
    "CategoryListResponse",
    # Products
    "ProductSizeBase",
    "ProductSizeCreate",
    "ProductSizeResponse",
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductListResponse",
    # Orders
    "PaymentMethod",
    "OrderType",
    "OrderItemCreate",
    "OrderItemResponse",
    "OrderBase",
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderSummary",
    "OrderListResponse",
    "OrderSummaryListResponse",
    # Register
    "TransactionType",
    "CashTransactionBase",
    "CashTransactionCreate",
    "CashTransactionResponse",
    "CashTransactionListResponse",
    "DepositRequest",
    "WithdrawalRequest",
    "ShiftCloseRequest",
    "RegisterStateResponse",
    # Debtors
    "DebtorBase",
    "DebtorCreate",
    "DebtorUpdate",
    "DebtorResponse",
    "DebtorListResponse",
    "MarkPaidRequest",
    # Settings
    "SensitiveActionKey",
    "PasswordRequirementBase",
    "PasswordRequirementCreate",
    "PasswordRequirementResponse",
    "PasswordRequirementMap",
    "SecuritySettings",
    "SettingsBase",
    "SettingsCreate",
    "SettingsUpdate",
    "SettingsResponse",
    # Activity
    "ActivityLogBase",
    "ActivityLogCreate",
    "ActivityLogResponse",
    "ActivityLogListResponse",
    "ActivityLogFilter",
]
