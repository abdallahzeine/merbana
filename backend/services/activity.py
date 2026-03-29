"""
backend/services/activity.py
============================
Activity logging service for audit trails.

Provides functions to log user actions and query activity logs with filters.
All operations are logged for important business actions.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models import ActivityLog
from ..schemas import ActivityLogFilter


def log_activity(
    db: Session,
    user_id: Optional[str],
    user_name: str,
    action: str,
) -> ActivityLog:
    """
    Create an activity log entry.

    Args:
        db: Database session
        user_id: User ID who performed the action (nullable)
        user_name: User name who performed the action
        action: Action description

    Returns:
        Created ActivityLog instance
    """
    # Generate timestamp in ISO format
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    activity_log = ActivityLog(
        id=str(uuid4()),
        user_id=user_id,
        user_name=user_name,
        action=action,
        timestamp=timestamp,
    )

    db.add(activity_log)
    db.flush()  # Flush to get the ID but don't commit yet

    return activity_log


def get_activity_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[ActivityLog]:
    """
    Query activity logs with optional filters.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        user_id: Filter by user ID
        date_from: Filter logs from this date (ISO format)
        date_to: Filter logs until this date (ISO format)

    Returns:
        List of ActivityLog instances ordered by timestamp desc
    """
    query = db.query(ActivityLog)

    # Apply filters
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)

    if date_from:
        query = query.filter(ActivityLog.timestamp >= date_from)

    if date_to:
        query = query.filter(ActivityLog.timestamp <= date_to)

    # Order by timestamp descending (newest first)
    query = query.order_by(desc(ActivityLog.timestamp))

    # Apply pagination
    logs = query.offset(skip).limit(limit).all()

    return logs
