"""
ActivityLog Pydantic Schemas Module.
Defines validation and serialization schemas for ActivityLog entities.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ActivityLogBase(BaseModel):
    """
    Base Pydantic schema for ActivityLog holding shared attributes.
    """
    session_id: UUID = Field(..., description="ID of the associated exam session")
    student_id: UUID = Field(..., description="ID of the associated student")
    activity_type: str = Field(..., max_length=100, description="Type of detected activity")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI detection confidence score (0.0 to 1.0)")

    model_config = ConfigDict(from_attributes=True)


class ActivityLogCreate(ActivityLogBase):
    """
    Pydantic schema for creating a new ActivityLog entry.
    """
    pass


class ActivityLogResponse(ActivityLogBase):
    """
    Pydantic schema for ActivityLog HTTP response data.
    """
    id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
