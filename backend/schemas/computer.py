"""
Computer Schema Module.
Defines schemas for ComputerEvent payloads and responses.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ComputerEventCreate(BaseModel):
    computer_id: str = Field(..., max_length=50, description="ID of the computer (e.g. PC-01)")
    student_name: Optional[str] = Field(None, max_length=150)
    active_application: Optional[str] = Field(None, max_length=150)
    active_website: Optional[str] = Field(None, max_length=150)
    cpu_usage: float = Field(0.0, description="CPU usage percent")
    ram_usage: float = Field(0.0, description="RAM usage percent")
    screenshot_path: Optional[str] = Field(None, max_length=255)
    activity_type: str = Field(..., max_length=100)
    confidence: float = Field(1.0, description="Confidence score")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class ComputerEventResponse(ComputerEventCreate):
    id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
