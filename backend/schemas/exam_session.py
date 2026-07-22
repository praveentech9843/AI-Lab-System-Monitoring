"""
ExamSession Pydantic Schemas Module.
Defines validation and serialization schemas for ExamSession entities.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExamSessionBase(BaseModel):
    """
    Base Pydantic schema for ExamSession holding shared attributes.
    """
    student_id: UUID = Field(..., description="ID of the student associated with the session")
    faculty_id: Optional[UUID] = Field(None, description="ID of the supervising faculty member")
    status: str = Field("active", max_length=50, description="Session status (e.g. active, completed)")

    model_config = ConfigDict(from_attributes=True)


class ExamSessionCreate(ExamSessionBase):
    """
    Pydantic schema for creating a new ExamSession.
    """
    pass


class ExamSessionUpdate(BaseModel):
    """
    Pydantic schema for updating existing ExamSession fields. All fields are optional.
    """
    faculty_id: Optional[UUID] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class ExamSessionResponse(ExamSessionBase):
    """
    Pydantic schema for ExamSession HTTP response data.
    """
    id: UUID
    start_time: datetime
    end_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
