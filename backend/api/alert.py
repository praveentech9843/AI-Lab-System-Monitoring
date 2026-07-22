"""
Alert Management REST API Router.
Provides endpoints for creating, querying, and deleting Alert entities.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from crud.alert import (
    create_alert,
    delete_alert,
    get_alerts_by_session,
    get_alerts_by_student,
    get_all_alerts,
)
from database.session import get_db
from schemas.alert import AlertCreate, AlertResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_new_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Creates a new anomaly alert record (Protected).
    """
    return create_alert(db, alert_data)


@router.get("/", response_model=List[AlertResponse], status_code=status.HTTP_200_OK)
def read_all_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves all alerts across all sessions.
    """
    return get_all_alerts(db, skip=skip, limit=limit)

@router.get("/student/{student_id}", response_model=List[AlertResponse], status_code=status.HTTP_200_OK)
def read_alerts_by_student(student_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves all anomaly alerts for a specific student.
    """
    return get_alerts_by_student(db, student_id, skip=skip, limit=limit)


@router.get("/session/{session_id}", response_model=List[AlertResponse], status_code=status.HTTP_200_OK)
def read_alerts_by_session(session_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves all anomaly alerts for a specific exam session.
    """
    return get_alerts_by_session(db, session_id, skip=skip, limit=limit)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deletes an alert record by ID (Protected).
    """
    success = delete_alert(db, alert_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found."
        )
    return None
