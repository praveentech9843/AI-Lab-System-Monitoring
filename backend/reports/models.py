"""
Reports Pydantic Models Module.
Defines report schemas for individual StudentReport and aggregated SessionReport.
"""
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StudentReport(BaseModel):
    """
    Pydantic schema representing an individual student's monitoring performance report.
    """
    student_id: Union[UUID, str] = Field(..., description="Student identifier")
    student_name: str = Field(..., description="Full name of the student")
    session_id: Union[UUID, str] = Field(..., description="Exam session identifier")
    total_events: int = Field(..., ge=0, description="Total number of logged anomaly events")
    total_score: int = Field(..., ge=0, description="Total risk score calculated")
    risk_level: str = Field(..., description="Assigned risk level (LOW, MEDIUM, HIGH, CRITICAL)")
    total_alerts: int = Field(..., ge=0, description="Total number of alerts generated")
    triggered_events: List[str] = Field(..., description="List of unique triggered event names")

    model_config = ConfigDict(from_attributes=True)


class SessionReport(BaseModel):
    """
    Pydantic schema representing an aggregated exam session summary report.
    """
    session_id: Union[UUID, str] = Field(..., description="Exam session identifier")
    total_students: int = Field(..., ge=0, description="Total number of participating students")
    average_score: float = Field(..., ge=0.0, description="Average risk score across all students")
    highest_score: int = Field(..., ge=0, description="Highest individual risk score in the session")
    total_alerts: int = Field(..., ge=0, description="Total aggregate alerts across all students")
    student_reports: List[StudentReport] = Field(..., description="List of individual StudentReport objects")

    model_config = ConfigDict(from_attributes=True)
