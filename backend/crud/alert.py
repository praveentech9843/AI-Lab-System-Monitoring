"""
Alert CRUD Operations Module.
Provides database access functions for Alert ORM models with safe transaction handling.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Alert
from schemas.alert import AlertCreate


def create_alert(db: Session, alert_create: AlertCreate) -> Alert:
    """
    Creates a new Alert record in the database.
    """
    db_alert = Alert(
        student_id=alert_create.student_id,
        session_id=alert_create.session_id,
        alert_type=alert_create.alert_type,
        severity=alert_create.severity,
        message=alert_create.message,
    )
    db.add(db_alert)
    try:
        db.commit()
        db.refresh(db_alert)
    except Exception:
        db.rollback()
        raise
    return db_alert


def get_alert_by_id(db: Session, alert_id: UUID) -> Optional[Alert]:
    """
    Retrieves an Alert record by primary key ID.
    """
    statement = select(Alert).where(Alert.id == alert_id)
    return db.scalar(statement)


def get_alerts_by_student(db: Session, student_id: UUID, skip: int = 0, limit: int = 100) -> List[Alert]:
    """
    Retrieves all Alert records for a specific student ordered by creation time descending.
    """
    statement = (
        select(Alert)
        .where(Alert.student_id == student_id)
        .order_by(Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_alerts_by_session(db: Session, session_id: UUID, skip: int = 0, limit: int = 100) -> List[Alert]:
    """
    Retrieves all Alert records for a specific exam session ordered by creation time descending.
    """
    statement = (
        select(Alert)
        .where(Alert.session_id == session_id)
        .order_by(Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def delete_alert(db: Session, alert_id: UUID) -> bool:
    """
    Deletes an Alert record by ID. Returns True if deleted, False if not found.
    """
    db_alert = get_alert_by_id(db, alert_id)
    if not db_alert:
        return False

    db.delete(db_alert)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True
