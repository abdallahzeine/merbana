"""
backend/schemas/settings.py
==========================
Pydantic schemas for StoreSettings and PasswordRequirement entities.

Based on StoreSettings and PasswordRequirement models from backend/models.py
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import TimestampStr


class SensitiveActionKey(str, Enum):
    """Keys for sensitive actions that may require password."""

    CREATE_ORDER = "create_order"
    DELETE_ORDER = "delete_order"
    DEPOSIT_CASH = "deposit_cash"
    WITHDRAW_CASH = "withdraw_cash"
    CLOSE_SHIFT = "close_shift"
    ADD_DEBTOR = "add_debtor"
    MARK_DEBTOR_PAID = "mark_debtor_paid"
    DELETE_DEBTOR = "delete_debtor"
    IMPORT_DATABASE = "import_database"


class PasswordRequirementBase(BaseModel):
    """Base password requirement fields."""

    action_name: SensitiveActionKey = Field(description="Sensitive action key")
    is_required: bool = Field(default=True, description="Whether password is required")


class PasswordRequirementCreate(PasswordRequirementBase):
    """Schema for creating a password requirement."""

    store_settings_id: int = Field(description="Store settings ID")


class PasswordRequirementResponse(PasswordRequirementBase):
    """Full password requirement model for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Password requirement ID")


class PasswordRequirementMap(BaseModel):
    """Map of sensitive action keys to whether password is required."""

    create_order: bool = Field(
        default=True, description="Password required for creating orders"
    )
    delete_order: bool = Field(
        default=True, description="Password required for deleting orders"
    )
    deposit_cash: bool = Field(
        default=True, description="Password required for depositing cash"
    )
    withdraw_cash: bool = Field(
        default=True, description="Password required for withdrawing cash"
    )
    close_shift: bool = Field(
        default=True, description="Password required for closing shift"
    )
    add_debtor: bool = Field(
        default=True, description="Password required for adding debtors"
    )
    mark_debtor_paid: bool = Field(
        default=True, description="Password required for marking debtors as paid"
    )
    delete_debtor: bool = Field(
        default=True, description="Password required for deleting debtors"
    )
    import_database: bool = Field(
        default=True, description="Password required for importing database"
    )


class SecuritySettings(BaseModel):
    """Security settings containing password requirements."""

    password_required_for: PasswordRequirementMap = Field(
        description="Map of actions to whether password is required"
    )


class SettingsBase(BaseModel):
    """Base settings fields."""

    company_name: str = Field(default="", max_length=255, description="Company name")


class SettingsCreate(SettingsBase):
    """Schema for creating initial settings."""

    security: SecuritySettings = Field(description="Security settings")


class SettingsUpdate(BaseModel):
    """Schema for updating settings."""

    company_name: Optional[str] = Field(
        default=None, max_length=255, description="Company name"
    )
    security: Optional[SecuritySettings] = Field(
        default=None, description="Security settings"
    )


class SettingsResponse(SettingsBase):
    """Full settings model for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Settings ID")
    security: SecuritySettings = Field(
        description="Security settings with password requirements map"
    )
