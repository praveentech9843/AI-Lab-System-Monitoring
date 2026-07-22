"""
Reports Exporter Module.
Converts report Pydantic models into dictionary representations ready for JSON serialization or future export formats.
"""
from typing import Any, Dict

from reports.models import SessionReport, StudentReport


def export_student_report(report: StudentReport) -> Dict[str, Any]:
    """
    Exports a StudentReport model to a serializable dictionary using Pydantic model_dump.
    """
    return report.model_dump(mode="json")


def export_session_report(report: SessionReport) -> Dict[str, Any]:
    """
    Exports a SessionReport model to a serializable dictionary using Pydantic model_dump.
    """
    return report.model_dump(mode="json")
