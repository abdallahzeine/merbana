"""
Merbana Backend Package

SQLAlchemy models and database utilities for the Merbana POS system.
"""

__version__ = "1.0.0"

# Models
from .models import (
    Base,
    Category,
    Product,
    ProductSize,
    StoreUser,
    ActivityLog,
    Order,
    OrderItem,
    CashTransaction,
    Debtor,
    StoreSettings,
    PasswordRequirement,
)

# Configuration
from .config import Settings, get_settings

# Path utilities
from .paths import (
    is_packaged,
    get_dist_path,
    get_data_path,
    get_sqlite_db_path,
    ensure_data_dir,
)

# Database
from .database import (
    engine,
    SessionLocal,
    get_db,
    init_db,
)

# Error handling
from .errors import (
    ErrorCode,
    AppError,
    ValidationError,
    NotFoundError,
    ConflictError,
    DuplicateIdError,
    InternalError,
    error_response,
)

# Dependencies
from .dependencies import (
    get_current_user,
    require_user,
    require_permission,
)

__all__ = [
    # Version
    "__version__",
    # Models
    "Base",
    "Category",
    "Product",
    "ProductSize",
    "StoreUser",
    "ActivityLog",
    "Order",
    "OrderItem",
    "CashTransaction",
    "Debtor",
    "StoreSettings",
    "PasswordRequirement",
    # Config
    "Settings",
    "get_settings",
    # Paths
    "is_packaged",
    "get_dist_path",
    "get_data_path",
    "get_sqlite_db_path",
    "ensure_data_dir",
    # Database
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    # Errors
    "ErrorCode",
    "AppError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "DuplicateIdError",
    "InternalError",
    "error_response",
    # Dependencies
    "get_current_user",
    "require_user",
    "require_permission",
]
