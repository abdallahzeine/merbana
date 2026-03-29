"""Initial schema baseline

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-03-20 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=False)

    op.create_table(
        "debtors",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.String(length=50), nullable=False),
        sa.Column("paid_at", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_debtors_created_at", "debtors", ["created_at"], unique=False)
    op.create_index("ix_debtors_paid_at", "debtors", ["paid_at"], unique=False)

    op.create_table(
        "store_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("last_stock_reset", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("category_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.String(length=50), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=True),
        sa.Column("track_stock", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_category_id", "products", ["category_id"], unique=False)
    op.create_index("ix_products_name", "products", ["name"], unique=False)

    op.create_table(
        "activity_log",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("user_name", sa.String(length=255), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activity_log_timestamp", "activity_log", ["timestamp"], unique=False)
    op.create_index("ix_activity_log_user_id", "activity_log", ["user_id"], unique=False)

    op.create_table(
        "orders",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("date", sa.String(length=50), nullable=False),
        sa.Column("total", sa.Float(), nullable=False),
        sa.Column("payment_method", sa.String(length=20), nullable=False),
        sa.Column("order_type", sa.String(length=20), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("user_name", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_date", "orders", ["date"], unique=False)
    op.create_index("ix_orders_order_number", "orders", ["order_number"], unique=False)
    op.create_index("ix_orders_user_id", "orders", ["user_id"], unique=False)

    op.create_table(
        "password_requirements",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("store_settings_id", sa.Integer(), nullable=False),
        sa.Column("action_name", sa.String(length=50), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["store_settings_id"], ["store_settings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "store_settings_id",
            "action_name",
            name="uq_password_requirements_settings_action",
        ),
    )

    op.create_table(
        "product_sizes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_sizes_product_id", "product_sizes", ["product_id"], unique=False)

    op.create_table(
        "cash_transactions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("date", sa.String(length=50), nullable=False),
        sa.Column("order_id", sa.String(length=36), nullable=True),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cash_transactions_date", "cash_transactions", ["date"], unique=False)
    op.create_index("ix_cash_transactions_order_id", "cash_transactions", ["order_id"], unique=False)
    op.create_index("ix_cash_transactions_user_id", "cash_transactions", ["user_id"], unique=False)

    op.create_table(
        "order_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("order_id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("size", sa.String(length=100), nullable=True),
        sa.Column("subtotal", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"], unique=False)
    op.create_index("ix_order_items_product_id", "order_items", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_order_items_product_id", table_name="order_items")
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")

    op.drop_index("ix_cash_transactions_user_id", table_name="cash_transactions")
    op.drop_index("ix_cash_transactions_order_id", table_name="cash_transactions")
    op.drop_index("ix_cash_transactions_date", table_name="cash_transactions")
    op.drop_table("cash_transactions")

    op.drop_index("ix_product_sizes_product_id", table_name="product_sizes")
    op.drop_table("product_sizes")

    op.drop_table("password_requirements")

    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_index("ix_orders_order_number", table_name="orders")
    op.drop_index("ix_orders_date", table_name="orders")
    op.drop_table("orders")

    op.drop_index("ix_activity_log_user_id", table_name="activity_log")
    op.drop_index("ix_activity_log_timestamp", table_name="activity_log")
    op.drop_table("activity_log")

    op.drop_index("ix_products_name", table_name="products")
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_table("products")

    op.drop_table("users")
    op.drop_table("store_settings")

    op.drop_index("ix_debtors_paid_at", table_name="debtors")
    op.drop_index("ix_debtors_created_at", table_name="debtors")
    op.drop_table("debtors")

    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")
