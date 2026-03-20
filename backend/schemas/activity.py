"""
backend/schemas/activity.py
===========================
Pydantic schemas for ActivityLog entities.

Based on ActivityLog model from backend/models.py
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import UUIDstr, TimestampStr, ListResponse


class ActivityLogBase(BaseModel):
    """Base activity log fields."""

    user_id: Optional[UUIDstr] = Field(
        default=None, description="User ID who performed the action"
    )
    user_name: str = Field(
        max_length=255, description="User name who performed the action"
    )
    action: str = Field(description="Action description")
    timestamp: TimestampStr = Field(description="Action timestamp")


class ActivityLogCreate(ActivityLogBase):
    """Schema for creating an activity log entry."""

    id: UUIDstr = Field(description="Activity log ID (UUID)")


class ActivityLogResponse(ActivityLogBase):
    """Full activity log model for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUIDstr = Field(description="Activity log ID")


class ActivityLogListResponse(ListResponse[ActivityLogResponse]):
    """Response wrapper for listing activity logs."""

    pass


class ActivityLogFilter(BaseModel):
    """Filter parameters for activity log queries."""

    date_from: Optional[TimestampStr] = Field(
        default=None, description="Filter logs from this date"
    )
    date_to: Optional[TimestampStr] = Field(
        default=None, description="Filter logs until this date"
    )
    user_id: Optional[UUIDstr] = Field(default=None, description="Filter by user ID")
