"""
CRUD Package Interface.
Exports all CRUD database functions for Student, Faculty, ExamSession, ActivityLog, and Alert entities.
"""
from .activity_log import (
    create_activity_log,
    delete_activity_log,
    get_activity_by_id,
    get_logs_by_session,
    get_logs_by_student,
)
from .alert import (
    create_alert,
    delete_alert,
    get_alert_by_id,
    get_alerts_by_session,
    get_alerts_by_student,
)
from .exam_session import (
    create_exam_session,
    delete_session,
    get_all_sessions,
    get_session_by_id,
    get_sessions_by_student,
    update_session,
)
from .faculty import (
    create_faculty,
    delete_faculty,
    get_all_faculty,
    get_faculty_by_email,
    get_faculty_by_employee_id,
    get_faculty_by_id,
    update_faculty,
)
from .student import (
    create_student,
    delete_student,
    get_all_students,
    get_student_by_email,
    get_student_by_id,
    get_student_by_register_number,
    update_student,
)

__all__ = [
    # Student CRUD
    "create_student",
    "get_student_by_id",
    "get_student_by_email",
    "get_student_by_register_number",
    "get_all_students",
    "update_student",
    "delete_student",
    # Faculty CRUD
    "create_faculty",
    "get_faculty_by_id",
    "get_faculty_by_email",
    "get_faculty_by_employee_id",
    "get_all_faculty",
    "update_faculty",
    "delete_faculty",
    # ExamSession CRUD
    "create_exam_session",
    "get_session_by_id",
    "get_sessions_by_student",
    "get_all_sessions",
    "update_session",
    "delete_session",
    # ActivityLog CRUD
    "create_activity_log",
    "get_activity_by_id",
    "get_logs_by_session",
    "get_logs_by_student",
    "delete_activity_log",
    # Alert CRUD
    "create_alert",
    "get_alert_by_id",
    "get_alerts_by_student",
    "get_alerts_by_session",
    "delete_alert",
]
