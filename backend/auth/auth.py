"""
User Authentication Logic Module.
Provides credential validation for Students and Faculty members using CRUD lookup and pwdlib verification.
"""
from typing import Optional

from sqlalchemy.orm import Session

from auth.security import verify_password
from crud.faculty import get_faculty_by_email, get_faculty_by_employee_id
from crud.student import get_student_by_email, get_student_by_register_number
from database.models import Faculty, Student


def authenticate_student(db: Session, email_or_reg: str, password: str) -> Optional[Student]:
    """
    Authenticates a Student by email or registration number and plaintext password.
    Returns Student ORM object if valid, None otherwise.
    """
    student = get_student_by_email(db, email_or_reg)
    if not student:
        student = get_student_by_register_number(db, email_or_reg)
    if not student:
        return None
    if not verify_password(password, student.password_hash):
        return None
    return student


def authenticate_faculty(db: Session, email_or_emp_id: str, password: str) -> Optional[Faculty]:
    """
    Authenticates a Faculty member by email or employee ID and plaintext password.
    Returns Faculty ORM object if valid, None otherwise.
    """
    faculty = get_faculty_by_email(db, email_or_emp_id)
    if not faculty:
        faculty = get_faculty_by_employee_id(db, email_or_emp_id)
    if not faculty:
        return None
    if not verify_password(password, faculty.password_hash):
        return None
    return faculty
