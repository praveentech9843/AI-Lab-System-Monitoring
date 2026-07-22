"""
Schemas Package Interface.
Exports all Pydantic v2 schemas for Student, Faculty, ExamSession, ActivityLog, and Alert entities.
"""
from .activity_log import ActivityLogBase, ActivityLogCreate, ActivityLogResponse
from .alert import AlertBase, AlertCreate, AlertResponse
from .exam_session import ExamSessionBase, ExamSessionCreate, ExamSessionResponse, ExamSessionUpdate
from .faculty import FacultyBase, FacultyCreate, FacultyResponse, FacultyUpdate
from .student import StudentBase, StudentCreate, StudentResponse, StudentUpdate

__all__ = [
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
