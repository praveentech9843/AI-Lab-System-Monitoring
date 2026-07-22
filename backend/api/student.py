"""
Student Management REST API Router.
Provides CRUD endpoints for managing Student entities.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from crud.student import (
    create_student,
    delete_student,
    get_all_students,
    get_student_by_email,
    get_student_by_id,
    get_student_by_register_number,
    update_student,
)
from database.session import get_db
from schemas.student import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_new_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    """
    Creates a new student record.
    """
    if get_student_by_email(db, student_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this email already exists."
        )
    if get_student_by_register_number(db, student_data.register_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this registration number already exists."
        )
    return create_student(db, student_data)


@router.get("/", response_model=List[StudentResponse], status_code=status.HTTP_200_OK)
def read_all_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a paginated list of all students.
    """
    return get_all_students(db, skip=skip, limit=limit)


@router.get("/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
def read_student_by_id(student_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieves a student by ID.
    """
    student = get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found."
        )
    return student


@router.put("/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
def update_existing_student(
    student_id: UUID,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Updates an existing student record (Protected).
    """
    updated_student = update_student(db, student_id, student_data)
    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found."
        )
    return updated_student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_student(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deletes a student record by ID (Protected).
    """
    success = delete_student(db, student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found."
        )
    return None
