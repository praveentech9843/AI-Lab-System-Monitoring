"""
Exam Session Management REST API Router.
Provides CRUD endpoints for managing ExamSession entities.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from crud.exam_session import (
    create_exam_session,
    delete_session,
    get_all_sessions,
    get_session_by_id,
    update_session,
)
from database.session import get_db
from schemas.exam_session import ExamSessionCreate, ExamSessionResponse, ExamSessionUpdate

router = APIRouter(prefix="/sessions", tags=["Exam Sessions"])


@router.post("/", response_model=ExamSessionResponse, status_code=status.HTTP_201_CREATED)
def create_new_session(
    session_data: ExamSessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Creates a new exam session (Protected).
    """
    return create_exam_session(db, session_data)


@router.get("/", response_model=List[ExamSessionResponse], status_code=status.HTTP_200_OK)
def read_all_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a paginated list of all exam sessions.
    """
    return get_all_sessions(db, skip=skip, limit=limit)


@router.get("/{session_id}", response_model=ExamSessionResponse, status_code=status.HTTP_200_OK)
def read_session_by_id(session_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieves an exam session by ID.
    """
    session_obj = get_session_by_id(db, session_id)
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam session not found."
        )
    return session_obj


@router.put("/{session_id}", response_model=ExamSessionResponse, status_code=status.HTTP_200_OK)
def update_existing_session(
    session_id: UUID,
    session_data: ExamSessionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Updates an existing exam session record (Protected).
    """
    updated = update_session(db, session_id, session_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam session not found."
        )
    return updated


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deletes an exam session record by ID (Protected).
    """
    success = delete_session(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam session not found."
        )
    return None
