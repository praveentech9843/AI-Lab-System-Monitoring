"""
Reports Package Interface.
Exports Pydantic models, statistical helpers, generators, and exporter functions.
"""
from .exporter import export_session_report, export_student_report
from .generator import generate_session_report, generate_student_report
from .models import SessionReport, StudentReport
from .statistics import (
    calculate_average_score,
    calculate_highest_score,
    count_total_alerts,
)

__all__ = [
    "StudentReport",
    "SessionReport",
    "calculate_average_score",
    "calculate_highest_score",
    "count_total_alerts",
    "generate_student_report",
    "generate_session_report",
    "export_student_report",
    "export_session_report",
]
