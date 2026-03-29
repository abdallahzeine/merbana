"""
backend/routers/settings.py
===========================
Settings management API endpoints.

Provides access to singleton settings with password requirements.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.models import StoreSettings, PasswordRequirement
from backend.schemas import (
    SettingsUpdate,
    SettingsResponse,
    PasswordRequirementMap,
    SecuritySettings,
)
from backend.schemas.settings import SensitiveActionKey
from backend.services import (
    get_or_create_settings,
    update_settings,
    get_password_requirements,
    update_password_requirement,
)

router = APIRouter()


def _build_settings_response(db: Session, settings: StoreSettings) -> SettingsResponse:
    """Build SettingsResponse with security requirements."""
    requirements = get_password_requirements(db)

    security = SecuritySettings(
        password_required_for=PasswordRequirementMap(**requirements)
    )

    return SettingsResponse(
        id=settings.id,
        company_name=settings.company_name,
        security=security,
    )


@router.get("", response_model=SettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
) -> SettingsResponse:
    """
    Get application settings.

    Returns the singleton settings including company name and password requirements.
    """
    settings = get_or_create_settings(db)
    return _build_settings_response(db, settings)


@router.put("", response_model=SettingsResponse)
def update_app_settings(
    settings_update: SettingsUpdate,
    db: Session = Depends(get_db),
) -> SettingsResponse:
    """
    Update application settings.

    Updates company name and/or password requirements.
    Only provided fields are updated.
    """
    try:
        settings = update_settings(db, settings_update)
        db.commit()
        return _build_settings_response(db, settings)
    except Exception as e:
        if "not found" in str(e).lower():
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


@router.get("/password-requirements", response_model=PasswordRequirementMap)
def get_password_requirements_map(
    db: Session = Depends(get_db),
) -> PasswordRequirementMap:
    """
    Get password requirements map.

    Returns a map of sensitive action keys to whether password is required.
    """
    requirements = get_password_requirements(db)
    return PasswordRequirementMap(**requirements)


@router.put("/password-requirements/{action}", response_model=SettingsResponse)
def update_single_password_requirement(
    action: SensitiveActionKey,
    is_required: bool,
    db: Session = Depends(get_db),
) -> SettingsResponse:
    """
    Update password requirement for a single action.

    Toggles whether password is required for the specified sensitive action.
    """
    try:
        update_password_requirement(db, action.value, is_required)
        db.commit()

        settings = get_or_create_settings(db)
        return _build_settings_response(db, settings)
    except Exception as e:
        if "not found" in str(e).lower():
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
