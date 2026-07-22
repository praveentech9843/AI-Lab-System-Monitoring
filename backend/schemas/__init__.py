"""
Schemas Package Interface.
Exports all Pydantic v2 schemas for Student, Faculty, ExamSession, ActivityLog, Alert, and Authentication.
"""
from .activity_log import ActivityLogBase, ActivityLogCreate, ActivityLogResponse
from .alert import AlertBase, AlertCreate, AlertResponse
from .auth import LoginRequest, TokenResponse
from .exam_session import ExamSessionBase, ExamSessionCreate, ExamSessionResponse, ExamSessionUpdate
from .faculty import FacultyBase, FacultyCreate, FacultyResponse, FacultyUpdate
from .student import StudentBase, StudentCreate, StudentResponse, StudentUpdate

__all__ = [
    # Authentication Schemas
    "LoginRequest",
    "TokenResponse",
    # Student Schemas
    "StudentBase",
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    # Faculty Schemas
    "FacultyBase",
    "FacultyCreate",
    "FacultyUpdate",
    "FacultyResponse",
    # ExamSession Schemas
    "ExamSessionBase",
    "ExamSessionCreate",
    "ExamSessionUpdate",
    "ExamSessionResponse",
    # ActivityLog Schemas
    "ActivityLogBase",
    "ActivityLogCreate",
    "ActivityLogResponse",
    # Alert Schemas
    "AlertBase",
    "AlertCreate",
    "AlertResponse",
]
