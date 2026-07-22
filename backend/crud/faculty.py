"""
Faculty CRUD Operations Module.
Provides database access functions for Faculty ORM models with safe transaction handling and password hashing.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.security import hash_password
from database.models import Faculty
from schemas.faculty import FacultyCreate, FacultyUpdate


def create_faculty(db: Session, faculty_create: FacultyCreate) -> Faculty:
    """
    Creates a new Faculty record in the database with hashed password.
    """
    db_faculty = Faculty(
        employee_id=faculty_create.employee_id,
        name=faculty_create.name,
        email=faculty_create.email,
        password_hash=hash_password(faculty_create.password),
        role=faculty_create.role,
    )
    db.add(db_faculty)
    try:
        db.commit()
        db.refresh(db_faculty)
    except Exception:
        db.rollback()
        raise
    return db_faculty


def get_faculty_by_id(db: Session, faculty_id: UUID) -> Optional[Faculty]:
    """
    Retrieves a Faculty record by primary key ID.
    """
    statement = select(Faculty).where(Faculty.id == faculty_id)
    return db.scalar(statement)


def get_faculty_by_email(db: Session, email: str) -> Optional[Faculty]:
    """
    Retrieves a Faculty record by email address.
    """
    statement = select(Faculty).where(Faculty.email == email)
    return db.scalar(statement)


def get_faculty_by_employee_id(db: Session, employee_id: str) -> Optional[Faculty]:
    """
    Retrieves a Faculty record by employee ID.
    """
    statement = select(Faculty).where(Faculty.employee_id == employee_id)
    return db.scalar(statement)


def get_all_faculty(db: Session, skip: int = 0, limit: int = 100) -> List[Faculty]:
    """
    Retrieves a list of Faculty records ordered by creation time descending.
    """
    statement = select(Faculty).order_by(Faculty.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def update_faculty(db: Session, faculty_id: UUID, faculty_update: FacultyUpdate) -> Optional[Faculty]:
    """
    Updates an existing Faculty record with provided fields and hashes password if updated.
    """
    db_faculty = get_faculty_by_id(db, faculty_id)
    if not db_faculty:
        return None

    update_data = faculty_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(db_faculty, field, value)

    try:
        db.commit()
        db.refresh(db_faculty)
    except Exception:
        db.rollback()
        raise
    return db_faculty


def delete_faculty(db: Session, faculty_id: UUID) -> bool:
    """
    Deletes a Faculty record by ID. Returns True if deleted, False if not found.
    """
    db_faculty = get_faculty_by_id(db, faculty_id)
    if not db_faculty:
        return False

    db.delete(db_faculty)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True
