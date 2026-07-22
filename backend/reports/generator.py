"""
Reports Generator Module.
Generates structured StudentReport and SessionReport Pydantic models.
"""
from typing import List, Union
from uuid import UUID

from reports.models import SessionReport, StudentReport
from reports.statistics import (
    calculate_average_score,
    calculate_highest_score,
    count_total_alerts,
)


def generate_student_report(
    student_id: Union[UUID, str],
    student_name: str,
    session_id: Union[UUID, str],
    total_events: int,
    total_score: int,
    risk_level: str,
    total_alerts: int,
    triggered_events: List[str],
) -> StudentReport:
    """
    Constructs an individual StudentReport Pydantic instance.
    """
    return StudentReport(
        student_id=student_id,
        student_name=student_name,
        session_id=session_id,
        total_events=total_events,
        total_score=total_score,
        risk_level=risk_level,
        total_alerts=total_alerts,
        triggered_events=triggered_events,
    )


def generate_session_report(
    session_id: Union[UUID, str],
    student_reports: List[StudentReport],
) -> SessionReport:
    """
    Aggregates a list of StudentReport instances into a SessionReport.
    Uses statistics helper functions to calculate averages, max scores, and total alerts.
    """
    scores = [r.total_score for r in student_reports]
    alerts = [r.total_alerts for r in student_reports]

    return SessionReport(
        session_id=session_id,
        total_students=len(student_reports),
        average_score=calculate_average_score(scores),
        highest_score=calculate_highest_score(scores),
        total_alerts=count_total_alerts(alerts),
        student_reports=student_reports,
    )
