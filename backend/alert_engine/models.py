"""
Alert Engine Pydantic Models Module.
Defines alert request payload and alert result notification schemas.
"""
from datetime import datetime
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AlertRequest(BaseModel):
    """
    Pydantic schema representing an alert generation request.
    """
    student_id: Union[UUID, str] = Field(..., description="Student identifier")
    session_id: Union[UUID, str] = Field(..., description="Exam session identifier")
    risk_level: str = Field(..., description="Calculated risk level (LOW, MEDIUM, HIGH, CRITICAL)")
    total_score: int = Field(..., ge=0, description="Total risk score")
    triggered_events: List[str] = Field(..., description="List of triggered anomaly event names")

    model_config = ConfigDict(from_attributes=True)


class AlertResult(BaseModel):
    """
    Pydantic schema representing the formatted generated alert result.
    """
    alert_id: UUID = Field(..., description="Unique alert identifier")
    student_id: Union[UUID, str] = Field(..., description="Student identifier")
    session_id: Union[UUID, str] = Field(..., description="Exam session identifier")
    severity: str = Field(..., description="Alert severity level (INFO, WARNING, HIGH, CRITICAL)")
    title: str = Field(..., description="Descriptive alert title")
    message: str = Field(..., description="Human-readable formatted alert message")
    timestamp: datetime = Field(..., description="Timestamp when alert was generated")

    model_config = ConfigDict(from_attributes=True)
