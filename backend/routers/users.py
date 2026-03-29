"""
backend/routers/users.py
========================
User management API endpoints.

Provides CRUD operations for application users.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.errors import NotFoundError, DuplicateIdError
from backend.models import StoreUser
from backend.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    ErrorResponse,
)

router = APIRouter()


@router.get("", response_model=UserListResponse)
def list_users(
    db: Session = Depends(get_db),
) -> UserListResponse:
    """
    List all users.

    Returns a list of all application users ordered by creation date.
    """
    users = db.query(StoreUser).order_by(StoreUser.created_at.desc()).all()
    return UserListResponse(data=[UserResponse.model_validate(u) for u in users])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Create a new user.

    Creates a user with the specified ID, name, password, and creation timestamp.
    """
    # Check for duplicate ID
    existing = db.query(StoreUser).filter(StoreUser.id == user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": f"User with ID '{user.id}' already exists",
                "code": "DUPLICATE_ID",
                "details": None,
            },
        )

    db_user = StoreUser(
        id=user.id,
        name=user.name,
        password=user.password,
        created_at=user.created_at,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return UserResponse.model_validate(db_user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Get a user by ID.

    Returns the user details for the specified user ID.
    """
    user = db.query(StoreUser).filter(StoreUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"User with ID '{user_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Update a user.

    Updates the specified user's name and/or password.
    Only provided fields are updated.
    """
    db_user = db.query(StoreUser).filter(StoreUser.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"User with ID '{user_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    # Update only provided fields
    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.password is not None:
        db_user.password = user_update.password

    db.commit()
    db.refresh(db_user)

    return UserResponse.model_validate(db_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a user.

    Deletes the user with the specified ID.
    Related activity logs, cash transactions, and orders will have
    user_id set to NULL to preserve history.
    """
    db_user = db.query(StoreUser).filter(StoreUser.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"User with ID '{user_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    db.delete(db_user)
    db.commit()

    return None
