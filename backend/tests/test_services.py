"""
backend/tests/test_services.py
==============================
Tests for service layer functions.
"""

import pytest

from backend.services.settings import get_or_create_settings, update_settings
from backend.services.categories import get_categories_with_counts
from backend.schemas import SettingsUpdate, SecuritySettings, PasswordRequirementMap


class TestSettingsService:
    """Tests for settings service functions."""

    def test_get_or_create_settings_creates_defaults(self, test_db):
        """Test that get_or_create_settings creates default settings."""
        settings = get_or_create_settings(test_db)

        assert settings is not None
        assert settings.id == 1
        assert settings.company_name == ""

    def test_get_or_create_settings_returns_existing(self, test_db):
        """Test that get_or_create_settings returns existing settings."""
        settings1 = get_or_create_settings(test_db)
        test_db.commit()

        settings2 = get_or_create_settings(test_db)

        assert settings1.id == settings2.id

    def test_update_settings_company_name(self, test_db):
        """Test updating company name."""
        get_or_create_settings(test_db)
        test_db.commit()

        update_data = SettingsUpdate(company_name="Test Store")
        settings = update_settings(test_db, update_data)
        test_db.commit()

        assert settings.company_name == "Test Store"

    def test_update_settings_partial_update(self, test_db):
        """Test that only provided fields are updated."""
        get_or_create_settings(test_db)
        test_db.commit()

        update_data = SettingsUpdate(company_name="Updated Store")
        settings = update_settings(test_db, update_data)
        test_db.commit()

        assert settings.company_name == "Updated Store"


class TestCategoryService:
    """Tests for category service functions."""

    def test_get_categories_with_counts_empty(self, test_db):
        """Test get_categories_with_counts returns empty list when no categories."""
        categories = get_categories_with_counts(test_db)

        assert categories == []

    def test_get_categories_with_counts_with_products(self, test_db):
        """Test get_categories_with_counts includes product counts."""
        from backend.models import Category, Product

        # FIXED: Using valid UUID format
        category = Category(
            id="11111111-1111-1111-1111-111111111111", name="Test Category"
        )
        test_db.add(category)
        test_db.commit()

        product1 = Product(
            id="test-prod-svc-1",
            name="Product 1",
            price=5.00,
            category_id="11111111-1111-1111-1111-111111111111",
            created_at="2024-01-15T10:30:00Z",
        )
        product2 = Product(
            id="test-prod-svc-2",
            name="Product 2",
            price=6.00,
            category_id="11111111-1111-1111-1111-111111111111",
            created_at="2024-01-15T10:30:00Z",
        )
        test_db.add(product1)
        test_db.add(product2)
        test_db.commit()

        categories = get_categories_with_counts(test_db)

        assert len(categories) == 1
        assert categories[0].id == "11111111-1111-1111-1111-111111111111"
        assert categories[0].name == "Test Category"
        assert categories[0].product_count == 2

    def test_get_categories_with_counts_mixed_products(self, test_db):
        """Test get_categories_with_counts with categories having different counts."""
        from backend.models import Category, Product

        # FIXED: Using valid UUID format
        cat1 = Category(id="22222222-2222-2222-2222-222222222222", name="Category 1")
        cat2 = Category(id="33333333-3333-3333-3333-333333333333", name="Category 2")
        test_db.add(cat1)
        test_db.add(cat2)
        test_db.commit()

        for i in range(3):
            test_db.add(
                Product(
                    id=f"test-prod-svc-1-{i}",
                    name=f"Product {i}",
                    price=5.00,
                    category_id="22222222-2222-2222-2222-222222222222",
                    created_at="2024-01-15T10:30:00Z",
                )
            )

        for i in range(1):
            test_db.add(
                Product(
                    id=f"test-prod-svc-2-{i}",
                    name=f"Product {i}",
                    price=5.00,
                    category_id="33333333-3333-3333-3333-333333333333",
                    created_at="2024-01-15T10:30:00Z",
                )
            )

        test_db.commit()

        categories = get_categories_with_counts(test_db)

        assert len(categories) == 2

        cat_dict = {c.id: c for c in categories}
        assert cat_dict["22222222-2222-2222-2222-222222222222"].product_count == 3
        assert cat_dict["33333333-3333-3333-3333-333333333333"].product_count == 1
