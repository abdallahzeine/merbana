"""
backend/routers/activity.py
===========================
Activity log API endpoints.

Provides query access to audit trail of user actions.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.schemas import (
    ActivityLogResponse,
    ActivityLogListResponse,
)
from backend.services import get_activity_logs

router = APIRouter()


@router.get("", response_model=ActivityLogListResponse)
def list_activity_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db),
) -> ActivityLogListResponse:
    """
    List activity logs with optional filtering and pagination.

    Returns the audit trail of user actions, ordered by timestamp (newest first).
    """
    logs = get_activity_logs(
        db,
        skip=offset,
        limit=limit,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )

    # Get total count for the query (without pagination)
    from sqlalchemy import func
    from backend.models import ActivityLog

    query = db.query(func.count(ActivityLog.id))

    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    if date_from:
        query = query.filter(ActivityLog.timestamp >= date_from)
    if date_to:
        query = query.filter(ActivityLog.timestamp <= date_to)

    total = query.scalar()

    return ActivityLogListResponse(
        data=[ActivityLogResponse.model_validate(log) for log in logs],
        total=total,
    )
