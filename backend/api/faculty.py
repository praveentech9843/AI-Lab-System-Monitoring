"""
Faculty Management REST API Router.
Provides CRUD endpoints for managing Faculty entities.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from crud.faculty import (
    create_faculty,
    delete_faculty,
    get_all_faculty,
    get_faculty_by_email,
    get_faculty_by_employee_id,
    get_faculty_by_id,
    update_faculty,
)
from database.session import get_db
from schemas.faculty import FacultyCreate, FacultyResponse, FacultyUpdate

router = APIRouter(prefix="/faculty", tags=["Faculty"])


@router.post("/", response_model=FacultyResponse, status_code=status.HTTP_201_CREATED)
def create_new_faculty(faculty_data: FacultyCreate, db: Session = Depends(get_db)):
    """
    Creates a new faculty record.
    """
    if get_faculty_by_email(db, faculty_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faculty with this email already exists."
        )
    if get_faculty_by_employee_id(db, faculty_data.employee_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faculty with this employee ID already exists."
        )
    return create_faculty(db, faculty_data)


@router.get("/", response_model=List[FacultyResponse], status_code=status.HTTP_200_OK)
def read_all_faculty(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a paginated list of all faculty members.
    """
    return get_all_faculty(db, skip=skip, limit=limit)


@router.get("/{faculty_id}", response_model=FacultyResponse, status_code=status.HTTP_200_OK)
def read_faculty_by_id(faculty_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieves a faculty member by ID.
    """
    faculty = get_faculty_by_id(db, faculty_id)
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty not found."
        )
    return faculty


@router.put("/{faculty_id}", response_model=FacultyResponse, status_code=status.HTTP_200_OK)
def update_existing_faculty(
    faculty_id: UUID,
    faculty_data: FacultyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Updates an existing faculty record (Protected).
    """
    updated_faculty = update_faculty(db, faculty_id, faculty_data)
    if not updated_faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty not found."
        )
    return updated_faculty


@router.delete("/{faculty_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_faculty(
    faculty_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deletes a faculty record by ID (Protected).
    """
    success = delete_faculty(db, faculty_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty not found."
        )
    return None
