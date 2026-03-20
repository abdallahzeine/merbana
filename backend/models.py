"""
SQLAlchemy 2.x ORM Models for Merbana Backend

Based on Task 1 Audit (JSON_to_SQLite_Audit.md)
All models use string UUID primary keys to match frontend strategy.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    ForeignKey,
    Index,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class Category(Base):
    """
    Product categories.

    Audit Reference: src/types/types.ts:37-40
    Delete Behavior: Blocked if products reference category (guarded delete)
    """

    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    __table_args__ = (Index("ix_categories_name", "name"),)


class Product(Base):
    """
    Products available for sale.

    Audit Reference: src/types/types.ts:1-10
    Field Mapping:
        - categoryId (TS) -> category_id (DB), optional
        - trackStock (TS) -> track_stock (DB), optional
        - createdAt (TS) -> created_at (DB), required
    """

    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    category_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[str] = mapped_column(String(50), nullable=False)
    stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    track_stock: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Relationships
    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="products",
    )
    sizes: Mapped[List["ProductSize"]] = relationship(
        "ProductSize",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductSize.sort_order",
    )

    __table_args__ = (
        Index("ix_products_name", "name"),
        Index("ix_products_category_id", "category_id"),
    )


class ProductSize(Base):
    """
    Size variants for products (nested array in JSON).

    Audit Reference: src/types/types.ts:1-10 (sizes field)
    Decision Lock: sort_order column added for stable ordering
    """

    __tablename__ = "product_sizes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="sizes")

    __table_args__ = (Index("ix_product_sizes_product_id", "product_id"),)


class StoreUser(Base):
    """
    Application users.

    Audit Reference: src/types/types.ts:42-47
    Delete Behavior: user_id in related tables SET NULL to preserve audit history
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    activity_logs: Mapped[List["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="user",
    )
    cash_transactions: Mapped[List["CashTransaction"]] = relationship(
        "CashTransaction",
        back_populates="user",
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="user",
    )


class ActivityLog(Base):
    """
    Audit trail of user actions.

    Audit Reference: src/types/types.ts:49-55
    Decision Lock: user_id SET NULL on user deletion (preserve history)
    """

    __tablename__ = "activity_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    user: Mapped[Optional["StoreUser"]] = relationship(
        "StoreUser",
        back_populates="activity_logs",
    )

    __table_args__ = (
        Index("ix_activity_log_timestamp", "timestamp"),
        Index("ix_activity_log_user_id", "user_id"),
    )


class Order(Base):
    """
    Customer orders.

    Audit Reference: src/types/types.ts:24-35
    Decision Lock: No unique constraint on order_number (preserves rollover)
    """

    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    order_number: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[str] = mapped_column(String(50), nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    order_type: Mapped[str] = mapped_column(String(20), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped[Optional["StoreUser"]] = relationship(
        "StoreUser",
        back_populates="orders",
    )
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    cash_transactions: Mapped[List["CashTransaction"]] = relationship(
        "CashTransaction",
        back_populates="order",
    )

    __table_args__ = (
        Index("ix_orders_date", "date"),
        Index("ix_orders_order_number", "order_number"),
        Index("ix_orders_user_id", "user_id"),
    )


class OrderItem(Base):
    """
    Items within an order (historical snapshot).

    Audit Reference: src/types/types.ts:12-19
    Decision Lock: product_id is nullable FK with SET NULL (historical orders may reference deleted products)
    Historical Fields: name, price, size, subtotal captured at order time
    """

    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    size: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped[Optional["Product"]] = relationship("Product")

    __table_args__ = (
        Index("ix_order_items_order_id", "order_id"),
        Index("ix_order_items_product_id", "product_id"),
    )


class CashTransaction(Base):
    """
    Cash register transactions.

    Audit Reference: src/types/types.ts:100-108
    Decision Lock: user_id SET NULL on user deletion (preserve transaction history)
    """

    __tablename__ = "cash_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date: Mapped[str] = mapped_column(String(50), nullable=False)
    order_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    order: Mapped[Optional["Order"]] = relationship(
        "Order",
        back_populates="cash_transactions",
    )
    user: Mapped[Optional["StoreUser"]] = relationship(
        "StoreUser",
        back_populates="cash_transactions",
    )

    __table_args__ = (
        Index("ix_cash_transactions_date", "date"),
        Index("ix_cash_transactions_order_id", "order_id"),
        Index("ix_cash_transactions_user_id", "user_id"),
    )


class Debtor(Base):
    """
    Debt tracking for customers.

    Audit Reference: src/types/types.ts:79-86
    """

    __tablename__ = "debtors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(50), nullable=False)
    paid_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_debtors_paid_at", "paid_at"),
        Index("ix_debtors_created_at", "created_at"),
    )


class StoreSettings(Base):
    """
    Application settings (single row table).

    Audit Reference: src/types/types.ts:74-77
    Decision Lock: last_stock_reset stored here (not separate table)
    Decision Lock: password requirements stored in separate table (normalized)
    """

    __tablename__ = "store_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    last_stock_reset: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    password_requirements: Mapped[List["PasswordRequirement"]] = relationship(
        "PasswordRequirement",
        back_populates="store_settings",
        cascade="all, delete-orphan",
    )


class PasswordRequirement(Base):
    """
    Password requirements for sensitive actions (normalized from JSON).

    Audit Reference: src/types/types.ts:57-68 (SensitiveActionKey enum)
    Decision Lock: Separate table instead of JSON column
    """

    __tablename__ = "password_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_settings_id: Mapped[int] = mapped_column(
        ForeignKey("store_settings.id", ondelete="CASCADE"),
        nullable=False,
    )
    action_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="One of: create_order, delete_order, deposit_cash, withdraw_cash, close_shift, add_debtor, mark_debtor_paid, delete_debtor, import_database",
    )
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    store_settings: Mapped["StoreSettings"] = relationship(
        "StoreSettings",
        back_populates="password_requirements",
    )

    __table_args__ = (
        UniqueConstraint(
            "store_settings_id",
            "action_name",
            name="uq_password_requirements_settings_action",
        ),
    )
