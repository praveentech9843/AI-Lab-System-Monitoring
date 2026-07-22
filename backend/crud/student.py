"""
Student CRUD Operations Module.
Provides database access functions for Student ORM models with safe transaction handling.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Student
from schemas.student import StudentCreate, StudentUpdate


def create_student(db: Session, student_create: StudentCreate) -> Student:
    """
    Creates a new Student record in the database.
    """
    db_student = Student(
        register_number=student_create.register_number,
        name=student_create.name,
        department=student_create.department,
        year=student_create.year,
        email=student_create.email,
        password_hash=student_create.password,
    )
    db.add(db_student)
    try:
        db.commit()
        db.refresh(db_student)
    except Exception:
        db.rollback()
        raise
    return db_student


def get_student_by_id(db: Session, student_id: UUID) -> Optional[Student]:
    """
    Retrieves a Student record by primary key ID.
    """
    statement = select(Student).where(Student.id == student_id)
    return db.scalar(statement)


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """
    Retrieves a Student record by email address.
    """
    statement = select(Student).where(Student.email == email)
    return db.scalar(statement)


def get_student_by_register_number(db: Session, register_number: str) -> Optional[Student]:
    """
    Retrieves a Student record by registration number.
    """
    statement = select(Student).where(Student.register_number == register_number)
    return db.scalar(statement)


def get_all_students(db: Session, skip: int = 0, limit: int = 100) -> List[Student]:
    """
    Retrieves a list of Student records ordered by creation time descending.
    """
    statement = select(Student).order_by(Student.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def update_student(db: Session, student_id: UUID, student_update: StudentUpdate) -> Optional[Student]:
    """
    Updates an existing Student record with provided fields.
    """
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        return None

    update_data = student_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = update_data.pop("password")

    for field, value in update_data.items():
        setattr(db_student, field, value)

    try:
        db.commit()
        db.refresh(db_student)
    except Exception:
        db.rollback()
        raise
    return db_student


def delete_student(db: Session, student_id: UUID) -> bool:
    """
    Deletes a Student record by ID. Returns True if deleted, False if not found.
    """
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        return False

    db.delete(db_student)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True
