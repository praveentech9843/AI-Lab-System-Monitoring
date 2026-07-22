"""
ActivityLog CRUD Operations Module.
Provides database access functions for ActivityLog ORM models with safe transaction handling.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import ActivityLog
from schemas.activity_log import ActivityLogCreate


def create_activity_log(db: Session, log_create: ActivityLogCreate) -> ActivityLog:
    """
    Creates a new ActivityLog record in the database.
    """
    db_log = ActivityLog(
        session_id=log_create.session_id,
        student_id=log_create.student_id,
        activity_type=log_create.activity_type,
        confidence=log_create.confidence,
    )
    db.add(db_log)
    try:
        db.commit()
        db.refresh(db_log)
    except Exception:
        db.rollback()
        raise
    return db_log


def get_activity_by_id(db: Session, activity_id: UUID) -> Optional[ActivityLog]:
    """
    Retrieves an ActivityLog record by primary key ID.
    """
    statement = select(ActivityLog).where(ActivityLog.id == activity_id)
    return db.scalar(statement)


def get_logs_by_session(db: Session, session_id: UUID, skip: int = 0, limit: int = 100) -> List[ActivityLog]:
    """
    Retrieves all ActivityLogs for a specific exam session ordered by timestamp descending.
    """
    statement = (
        select(ActivityLog)
        .where(ActivityLog.session_id == session_id)
        .order_by(ActivityLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_logs_by_student(db: Session, student_id: UUID, skip: int = 0, limit: int = 100) -> List[ActivityLog]:
    """
    Retrieves all ActivityLogs for a specific student ordered by timestamp descending.
    """
    statement = (
        select(ActivityLog)
        .where(ActivityLog.student_id == student_id)
        .order_by(ActivityLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def delete_activity_log(db: Session, activity_id: UUID) -> bool:
    """
    Deletes an ActivityLog record by ID. Returns True if deleted, False if not found.
    """
    db_log = get_activity_by_id(db, activity_id)
    if not db_log:
        return False

    db.delete(db_log)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True
