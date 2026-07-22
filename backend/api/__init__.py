"""
API Routers Package Interface.
Exports all APIRouter modules for authentication, students, faculty, exam sessions, activity logs, and alerts.
"""
from .activity_log import router as activity_log_router
from .alert import router as alert_router
from .auth import router as auth_router
from .exam_session import router as exam_session_router
from .faculty import router as faculty_router
from .student import router as student_router

__all__ = [
    "auth_router",
    "student_router",
    "faculty_router",
    "exam_session_router",
    "activity_log_router",
    "alert_router",
]
