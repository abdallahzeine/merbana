"""
backend/services/settings.py
============================
Settings management service with defaults.

Provides functions for:
- Getting or creating singleton settings
- Updating settings with merge logic
- Managing password requirements for sensitive actions

Settings is a singleton (single row table) with default values.
"""

from typing import Dict, Optional

from sqlalchemy.orm import Session

from ..models import StoreSettings, PasswordRequirement
from ..schemas import (
    SettingsUpdate,
    SettingsCreate,
    SecuritySettings,
    PasswordRequirementMap,
)
from ..schemas.settings import SensitiveActionKey
from ..errors import NotFoundError


def initialize_default_password_requirements(
    db: Session,
    settings_id: int,
) -> None:
    """
    Create all 9 default password requirements.

    Args:
        db: Database session
        settings_id: Store settings ID to associate with
    """
    default_actions = [
        SensitiveActionKey.CREATE_ORDER,
        SensitiveActionKey.DELETE_ORDER,
        SensitiveActionKey.DEPOSIT_CASH,
        SensitiveActionKey.WITHDRAW_CASH,
        SensitiveActionKey.CLOSE_SHIFT,
        SensitiveActionKey.ADD_DEBTOR,
        SensitiveActionKey.MARK_DEBTOR_PAID,
        SensitiveActionKey.DELETE_DEBTOR,
        SensitiveActionKey.IMPORT_DATABASE,
    ]

    for action in default_actions:
        req = PasswordRequirement(
            store_settings_id=settings_id,
            action_name=action.value,
            is_required=True,
        )
        db.add(req)


def get_or_create_settings(db: Session) -> StoreSettings:
    """
    Get the singleton settings or create with defaults.

    Args:
        db: Database session

    Returns:
        StoreSettings instance (existing or newly created)
    """
    settings = db.query(StoreSettings).first()

    if not settings:
        # Create default settings
        settings = StoreSettings(
            id=1,
            company_name="",
        )
        db.add(settings)
        db.flush()  # Flush to get the ID

        # Create default password requirements
        try:
            initialize_default_password_requirements(db, settings.id)
            db.commit()  # Commit to persist settings and requirements
        except Exception:
            db.rollback()
            raise

    return settings


def get_password_requirements(db: Session) -> Dict[str, bool]:
    """
    Get map of action -> is_required for all password requirements.

    Args:
        db: Database session

    Returns:
        Dictionary mapping action names to boolean (True if password required)
    """
    settings = get_or_create_settings(db)

    requirements = {}
    for req in settings.password_requirements:
        requirements[req.action_name] = req.is_required

    # Ensure all 9 actions are present (defaults to True)
    all_actions = [
        "create_order",
        "delete_order",
        "deposit_cash",
        "withdraw_cash",
        "close_shift",
        "add_debtor",
        "mark_debtor_paid",
        "delete_debtor",
        "import_database",
    ]

    for action in all_actions:
        if action not in requirements:
            requirements[action] = True

    return requirements


def update_password_requirement(
    db: Session,
    action: str,
    is_required: bool,
) -> PasswordRequirement:
    """
    Toggle password requirement for a single action.

    Args:
        db: Database session
        action: Action name (e.g., 'create_order')
        is_required: Whether password is required

    Returns:
        Updated PasswordRequirement instance

    Raises:
        NotFoundError: If requirement not found
    """
    settings = get_or_create_settings(db)

    req = (
        db.query(PasswordRequirement)
        .filter(
            PasswordRequirement.store_settings_id == settings.id,
            PasswordRequirement.action_name == action,
        )
        .first()
    )

    if not req:
        raise NotFoundError(f"Password requirement for action '{action}' not found")

    req.is_required = is_required

    return req


def update_settings(
    db: Session,
    update_data: SettingsUpdate,
) -> StoreSettings:
    """
    Update settings with merge logic.

    Only updates fields that are provided (not None).

    Args:
        db: Database session
        update_data: Settings update data

    Returns:
        Updated StoreSettings instance
    """
    settings = get_or_create_settings(db)

    # Update company_name if provided
    if update_data.company_name is not None:
        settings.company_name = update_data.company_name

    # Update password requirements if provided
    if update_data.security is not None and update_data.security.password_required_for:
        req_map = update_data.security.password_required_for

        # Update each action
        for action_name, is_required in req_map.model_dump().items():
            req = (
                db.query(PasswordRequirement)
                .filter(
                    PasswordRequirement.store_settings_id == settings.id,
                    PasswordRequirement.action_name == action_name,
                )
                .first()
            )

            if req:
                req.is_required = is_required
            else:
                # Create new requirement if doesn't exist
                new_req = PasswordRequirement(
                    store_settings_id=settings.id,
                    action_name=action_name,
                    is_required=is_required,
                )
                db.add(new_req)

    return settings
