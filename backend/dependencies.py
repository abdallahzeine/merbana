"""
backend/dependencies.py
=======================
FastAPI dependencies for the Merbana backend.

Provides reusable dependencies for database sessions, authentication,
and other common requirements across API endpoints.
"""

from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from .database import get_db as _get_db

# Re-export get_db for convenience
get_db = _get_db


def get_current_user(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
) -> dict:
    """
    Extract user information from request headers.

    This is a placeholder for authentication. In a real application,
    you would verify JWT tokens or session cookies here.

    Headers expected:
        X-User-Id: User ID (optional)
        X-User-Name: User name (optional)

    Returns:
        Dictionary with user_id and user_name, or None values if not provided.

    Usage:
        @app.get("/protected")
        def protected_route(user: dict = Depends(get_current_user)):
            if user["user_id"] is None:
                raise HTTPException(status_code=401, detail="Not authenticated")
            ...
    """
    return {
        "user_id": x_user_id,
        "user_name": x_user_name,
    }


def require_user(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
) -> dict:
    """
    Require authentication - raises 401 if user not provided.

    Usage:
        @app.post("/orders/")
        def create_order(user: dict = Depends(require_user)):
            # User is guaranteed to be authenticated here
            ...
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Authentication required",
                "code": "AUTH_REQUIRED",
                "details": None,
            },
        )

    return {
        "user_id": x_user_id,
        "user_name": x_user_name or "Unknown",
    }


def require_permission(permission: str):
    """
    Factory for creating permission-checking dependencies.

    Usage:
        @app.delete("/orders/{id}")
        def delete_order(
            user: dict = Depends(require_permission("delete_order"))
        ):
            ...

    Note: This is a placeholder. In a real app, check against user permissions.
    """

    def check_permission(
        user: dict = Depends(require_user),
    ) -> dict:
        # Placeholder: In production, check user permissions here
        # For now, just require authentication
        return user

    return check_permission
