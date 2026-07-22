"""
ExamSession CRUD Operations Module.
Provides database access functions for ExamSession ORM models with safe transaction handling.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import ExamSession
from schemas.exam_session import ExamSessionCreate, ExamSessionUpdate


def create_exam_session(db: Session, session_create: ExamSessionCreate) -> ExamSession:
    """
    Creates a new ExamSession record in the database.
    """
    db_session = ExamSession(
        student_id=session_create.student_id,
        faculty_id=session_create.faculty_id,
        status=session_create.status,
    )
    db.add(db_session)
    try:
        db.commit()
        db.refresh(db_session)
    except Exception:
        db.rollback()
        raise
    return db_session


def get_session_by_id(db: Session, session_id: UUID) -> Optional[ExamSession]:
    """
    Retrieves an ExamSession record by primary key ID.
    """
    statement = select(ExamSession).where(ExamSession.id == session_id)
    return db.scalar(statement)


def get_sessions_by_student(db: Session, student_id: UUID, skip: int = 0, limit: int = 100) -> List[ExamSession]:
    """
    Retrieves all ExamSessions for a specific student ordered by start time descending.
    """
    statement = (
        select(ExamSession)
        .where(ExamSession.student_id == student_id)
        .order_by(ExamSession.start_time.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_all_sessions(db: Session, skip: int = 0, limit: int = 100) -> List[ExamSession]:
    """
    Retrieves a list of all ExamSessions ordered by start time descending.
    """
    statement = select(ExamSession).order_by(ExamSession.start_time.desc()).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def update_session(db: Session, session_id: UUID, session_update: ExamSessionUpdate) -> Optional[ExamSession]:
    """
    Updates an existing ExamSession record with provided fields.
    """
    db_session = get_session_by_id(db, session_id)
    if not db_session:
        return None

    update_data = session_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)

    try:
        db.commit()
        db.refresh(db_session)
    except Exception:
        db.rollback()
        raise
    return db_session


def delete_session(db: Session, session_id: UUID) -> bool:
    """
    Deletes an ExamSession record by ID. Returns True if deleted, False if not found.
    """
    db_session = get_session_by_id(db, session_id)
    if not db_session:
        return False

    db.delete(db_session)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True
