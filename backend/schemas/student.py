"""
Student Pydantic Schemas Module.
Defines validation and serialization schemas for Student entities.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StudentBase(BaseModel):
    """
    Base Pydantic schema for Student holding shared attributes.
    """
    register_number: str = Field(..., max_length=50, description="Unique registration number")
    name: str = Field(..., min_length=2, max_length=150, description="Full name of the student")
    department: str = Field(..., max_length=100, description="Academic department name")
    year: str = Field(..., max_length=20, description="Academic year of study")
    email: EmailStr = Field(..., description="Unique email address")

    model_config = ConfigDict(from_attributes=True)


class StudentCreate(StudentBase):
    """
    Pydantic schema for creating a new Student.
    """
    password: str = Field(..., min_length=8, description="Plaintext password (minimum 8 characters)")


class StudentUpdate(BaseModel):
    """
    Pydantic schema for updating existing Student fields. All fields are optional.
    """
    register_number: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    department: Optional[str] = Field(None, max_length=100)
    year: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class StudentResponse(StudentBase):
    """
    Pydantic schema for Student HTTP response data.
    Excludes sensitive fields like password.
    """
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
