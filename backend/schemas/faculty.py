"""
Faculty Pydantic Schemas Module.
Defines validation and serialization schemas for Faculty entities.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class FacultyBase(BaseModel):
    """
    Base Pydantic schema for Faculty holding shared attributes.
    """
    employee_id: str = Field(..., max_length=50, description="Unique employee identifier")
    name: str = Field(..., min_length=2, max_length=150, description="Full name of the faculty member")
    email: EmailStr = Field(..., description="Unique email address")
    role: str = Field("faculty", max_length=50, description="Administrative role")

    model_config = ConfigDict(from_attributes=True)


class FacultyCreate(FacultyBase):
    """
    Pydantic schema for creating a new Faculty member.
    """
    password: str = Field(..., min_length=8, description="Plaintext password (minimum 8 characters)")


class FacultyUpdate(BaseModel):
    """
    Pydantic schema for updating existing Faculty fields. All fields are optional.
    """
    employee_id: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class FacultyResponse(FacultyBase):
    """
    Pydantic schema for Faculty HTTP response data.
    Excludes sensitive fields like password.
    """
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
