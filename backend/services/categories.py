"""
backend/services/categories.py
==============================
Category management service with guarded delete.

Provides functions for:
- Getting categories with product counts
- Checking if a category can be deleted
- Deleting a category only if it has no products

This prevents accidental deletion of categories that have products assigned.
"""

from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import Category, Product
from ..schemas import CategoryWithProductCount
from ..errors import NotFoundError, ConflictError
from .activity import log_activity


def get_categories_with_counts(db: Session) -> List[CategoryWithProductCount]:
    """
    Get all categories with product counts.

    Args:
        db: Database session

    Returns:
        List of categories with product count information
    """
    # Query categories with product counts using join
    results = (
        db.query(
            Category,
            func.count(Product.id).label("product_count"),
        )
        .outerjoin(Product, Category.id == Product.category_id)
        .group_by(Category.id)
        .all()
    )

    categories_with_counts = []
    for category, product_count in results:
        cat_with_count = CategoryWithProductCount(
            id=category.id,
            name=category.name,
            product_count=product_count,
        )
        categories_with_counts.append(cat_with_count)

    return categories_with_counts


def can_delete_category(db: Session, category_id: str) -> bool:
    """
    Check if a category can be deleted (has no products).

    Args:
        db: Database session
        category_id: Category ID to check

    Returns:
        True if category can be deleted, False otherwise

    Raises:
        NotFoundError: If category not found
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundError(f"Category with id '{category_id}' not found")

    # Check if category has any products
    product_count = (
        db.query(func.count(Product.id))
        .filter(Product.category_id == category_id)
        .scalar()
    )

    return product_count == 0


def delete_category_guarded(
    db: Session,
    category_id: str,
    user_id: str = None,
    user_name: str = "System",
) -> None:
    """
    Delete a category only if it has no products.

    Args:
        db: Database session
        category_id: Category ID to delete
        user_id: User ID deleting the category (for logging)
        user_name: User name deleting the category (for logging)

    Raises:
        NotFoundError: If category not found
        ConflictError: If category has products and cannot be deleted
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundError(f"Category with id '{category_id}' not found")

    # Check if category can be deleted
    if not can_delete_category(db, category_id):
        # Get product count for error message
        product_count = (
            db.query(func.count(Product.id))
            .filter(Product.category_id == category_id)
            .scalar()
        )

        raise ConflictError(
            f"Cannot delete category '{category.name}' - it has {product_count} product(s)",
            details={
                "category_id": category_id,
                "category_name": category.name,
                "product_count": product_count,
            },
        )

    # Store category name before deletion for logging
    category_name = category.name

    # Delete the category
    db.delete(category)

    # Log activity
    action = f"Category '{category_name}' deleted"
    log_activity(db, user_id, user_name, action)
