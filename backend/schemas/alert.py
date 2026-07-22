"""
Alert Pydantic Schemas Module.
Defines validation and serialization schemas for Alert entities.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AlertBase(BaseModel):
    """
    Base Pydantic schema for Alert holding shared attributes.
    """
    student_id: UUID = Field(..., description="ID of the student associated with the alert")
    session_id: UUID = Field(..., description="ID of the exam session associated with the alert")
    alert_type: str = Field(..., max_length=100, description="Type of alert triggered (e.g. mobile_phone, unauthorized_person)")
    severity: str = Field(..., max_length=50, description="Severity level (e.g. low, medium, high, critical)")
    message: str = Field(..., max_length=500, description="Detailed alert description message")

    model_config = ConfigDict(from_attributes=True)


class AlertCreate(AlertBase):
    """
    Pydantic schema for creating a new Alert event.
    """
    pass


class AlertResponse(AlertBase):
    """
    Pydantic schema for Alert HTTP response data.
    """
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
