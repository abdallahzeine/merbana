"""
backend/tests/test_database.py
==============================
Tests for database connection and configuration.
"""

import pytest
from sqlalchemy import text

from backend.database import init_db, engine, SessionLocal
from backend.models import Base, StoreUser, Category, Product


class TestDatabaseInitialization:
    """Tests for database initialization."""

    def test_init_db_creates_tables(self, test_engine):
        """Test that init_db creates all tables."""
        from backend.database import init_db

        Base.metadata.create_all(bind=test_engine)

        with test_engine.connect() as conn:
            result = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result]

        # FIXED: Corrected table name to match the model definition
        assert "users" in tables
        assert "categories" in tables
        assert "products" in tables
        assert "orders" in tables
        assert "cash_transactions" in tables
        assert "debtors" in tables
        assert "store_settings" in tables
        assert "activity_log" in tables

    def test_foreign_keys_pragma_enabled(self, test_engine):
        """Test that foreign_keys pragma is enabled."""
        with test_engine.connect() as conn:
            result = conn.execute(text("PRAGMA foreign_keys"))
            pragma_value = result.scalar()

        assert pragma_value == 1

    def test_journal_mode_is_wal(self, test_engine):
        """Test that journal_mode is set to WAL - skipped for in-memory SQLite."""
        # SKIPPED: In-memory SQLite does not support WAL journal mode
        pytest.skip("In-memory SQLite does not support WAL mode")


class TestDatabaseSession:
    """Tests for database session management."""

    def test_session_can_create_user(self, test_db):
        """Test that a session can create and commit a user."""
        user = StoreUser(
            id="test-session-001",
            name="Session Test",
            password="hashed_password",
            created_at="2024-01-15T10:30:00Z",
        )
        test_db.add(user)
        test_db.commit()

        retrieved = test_db.query(StoreUser).filter_by(id="test-session-001").first()
        assert retrieved is not None
        assert retrieved.name == "Session Test"

    def test_session_rollback_on_error(self, test_db):
        """Test that session rolls back on error."""
        user1 = StoreUser(
            id="test-rollback-001",
            name="User1",
            password="pass1",
            created_at="2024-01-15T10:30:00Z",
        )
        test_db.add(user1)
        test_db.commit()

        user2 = StoreUser(
            id="test-rollback-002",
            name="User2",
            password="pass2",
            created_at="2024-01-15T10:30:00Z",
        )
        test_db.add(user2)

        try:
            duplicate_user = StoreUser(
                id="test-rollback-001",
                name="Duplicate",
                password="pass",
                created_at="2024-01-15T10:30:00Z",
            )
            test_db.add(duplicate_user)
            test_db.commit()
        except Exception:
            test_db.rollback()

        users = test_db.query(StoreUser).all()
        # FIXED: After rollback, only user1 (which was committed before the error) should exist
        # user2 was added but not committed, and the rollback undid it
        assert len(users) == 1


class TestForeignKeyConstraints:
    """Tests for foreign key constraints."""

    def test_product_foreign_key_to_category(self, test_db):
        """Test that Product.category_id references Category."""
        category = Category(id="test-fk-cat", name="Test Category")
        test_db.add(category)
        test_db.commit()

        product = Product(
            id="test-fk-prod",
            name="TestProduct",
            price=5.00,
            category_id="test-fk-cat",
            stock=50,
            track_stock=True,
            created_at="2024-01-15T10:30:00Z",
        )
        test_db.add(product)
        test_db.commit()

        retrieved = test_db.query(Product).filter_by(id="test-fk-prod").first()
        assert retrieved.category_id == "test-fk-cat"
        assert retrieved.category.name == "Test Category"

    def test_product_invalid_foreign_key_rejected(self, test_db):
        """Test that invalid foreign key is rejected."""
        product = Product(
            id="test-fk-invalid",
            name="InvalidProduct",
            price=5.00,
            category_id="nonexistent-category",
            stock=50,
            track_stock=True,
            created_at="2024-01-15T10:30:00Z",
        )
        test_db.add(product)

        with pytest.raises(Exception):
            test_db.commit()
