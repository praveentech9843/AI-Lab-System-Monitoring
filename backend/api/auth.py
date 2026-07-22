"""
Authentication REST API Router.
Provides endpoints for Student and Faculty registration and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.auth import authenticate_faculty, authenticate_student
from auth.jwt_handler import create_access_token
from crud.faculty import create_faculty, get_faculty_by_email, get_faculty_by_employee_id
from crud.student import create_student, get_student_by_email, get_student_by_register_number
from database.session import get_db
from schemas.auth import LoginRequest, TokenResponse
from schemas.faculty import FacultyCreate, FacultyResponse
from schemas.student import StudentCreate, StudentResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/student/register", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def register_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    """
    Registers a new Student account.
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


@router.post("/student/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login_student(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a Student and returns a signed JWT access token.
    """
    student = authenticate_student(db, login_data.email, login_data.password)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": str(student.id), "role": "student"})
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/faculty/register", response_model=FacultyResponse, status_code=status.HTTP_201_CREATED)
def register_faculty(faculty_data: FacultyCreate, db: Session = Depends(get_db)):
    """
    Registers a new Faculty member account.
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


@router.post("/faculty/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login_faculty(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a Faculty member and returns a signed JWT access token.
    """
    faculty = authenticate_faculty(db, login_data.email, login_data.password)
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": str(faculty.id), "role": "faculty"})
    return TokenResponse(access_token=token, token_type="bearer")
