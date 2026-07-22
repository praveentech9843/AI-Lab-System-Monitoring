"""
AI Risk Engine Pydantic Models Module.
Defines risk event inputs and risk calculation result models.
"""
from datetime import datetime
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RiskEvent(BaseModel):
    """
    Pydantic schema representing an individual detected behavior event.
    """
    event_type: str = Field(..., description="Name/type of the detected event")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    timestamp: datetime = Field(..., description="Timestamp when event occurred")

    model_config = ConfigDict(from_attributes=True)


class RiskResult(BaseModel):
    """
    Pydantic schema representing the evaluated risk score and risk level result.
    """
    student_id: Union[UUID, str] = Field(..., description="Student identifier")
    session_id: Union[UUID, str] = Field(..., description="Exam session identifier")
    total_score: int = Field(..., ge=0, description="Calculated total risk score")
    risk_level: str = Field(..., description="Risk level designation (LOW, MEDIUM, HIGH, CRITICAL)")
    triggered_events: List[str] = Field(..., description="List of unique triggered event names")

    model_config = ConfigDict(from_attributes=True)
