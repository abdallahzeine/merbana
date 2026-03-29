"""
backend/routers/categories.py
=============================
Category management API endpoints.

Provides CRUD operations for product categories with guarded delete.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.models import Category
from backend.schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithProductCount,
    CategoryListResponse,
)
from backend.services import get_categories_with_counts, delete_category_guarded

router = APIRouter()


@router.get("", response_model=CategoryListResponse)
def list_categories(
    db: Session = Depends(get_db),
) -> CategoryListResponse:
    """
    List all categories.

    Returns a list of all product categories with product counts.
    """
    categories = get_categories_with_counts(db)
    return CategoryListResponse(data=categories)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """
    Create a new category.

    Creates a category with the specified ID and name.
    """
    # Check for duplicate ID
    existing = db.query(Category).filter(Category.id == category.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": f"Category with ID '{category.id}' already exists",
                "code": "DUPLICATE_ID",
                "details": None,
            },
        )

    db_category = Category(
        id=category.id,
        name=category.name,
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return CategoryResponse.model_validate(db_category)


@router.get("/{category_id}", response_model=CategoryWithProductCount)
def get_category(
    category_id: str,
    db: Session = Depends(get_db),
) -> CategoryWithProductCount:
    """
    Get a category by ID.

    Returns the category details including product count.
    """
    categories = get_categories_with_counts(db)
    category = next((c for c in categories if c.id == category_id), None)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Category with ID '{category_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: str,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """
    Update a category.

    Updates the specified category's name.
    """
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Category with ID '{category_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    if category_update.name is not None:
        db_category.name = category_update.name

    db.commit()
    db.refresh(db_category)

    return CategoryResponse.model_validate(db_category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a category.

    Deletes the category only if it has no products assigned.
    Returns 409 CONFLICT if the category has products.
    """
    try:
        delete_category_guarded(db, category_id)
        db.commit()
    except Exception as e:
        # Check if it's a conflict error from the service
        if "Cannot delete" in str(e) and "product" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": str(e),
                    "code": "CONFLICT",
                    "details": None,
                },
            )
        elif "not found" in str(e).lower():
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
