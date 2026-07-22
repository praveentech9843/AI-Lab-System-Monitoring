"""
Activity Log Management REST API Router.
Provides endpoints for creating, querying, and deleting ActivityLog entities.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from crud.activity_log import (
    create_activity_log,
    delete_activity_log,
    get_logs_by_session,
    get_logs_by_student,
)
from database.session import get_db
from schemas.activity_log import ActivityLogCreate, ActivityLogResponse

router = APIRouter(prefix="/activities", tags=["Activity Logs"])


@router.post("/", response_model=ActivityLogResponse, status_code=status.HTTP_201_CREATED)
def create_new_activity_log(
    log_data: ActivityLogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Creates a new activity log entry (Protected).
    """
    return create_activity_log(db, log_data)


@router.get("/student/{student_id}", response_model=List[ActivityLogResponse], status_code=status.HTTP_200_OK)
def read_logs_by_student(student_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves all activity logs for a specific student.
    """
    return get_logs_by_student(db, student_id, skip=skip, limit=limit)


@router.get("/session/{session_id}", response_model=List[ActivityLogResponse], status_code=status.HTTP_200_OK)
def read_logs_by_session(session_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves all activity logs for a specific exam session.
    """
    return get_logs_by_session(db, session_id, skip=skip, limit=limit)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_activity_log(
    activity_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deletes an activity log record by ID (Protected).
    """
    success = delete_activity_log(db, activity_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found."
        )
    return None
