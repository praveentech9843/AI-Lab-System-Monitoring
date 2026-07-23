"""
Blocked Website Pydantic Schemas Module.
Defines validation and serialization schemas for Blocked Website configurations.
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class BlockedWebsiteBase(BaseModel):
    """
    Base Pydantic schema for Blocked Website holding shared attributes.
    """
    domain: str = Field(..., max_length=255, description="Domain name or keyword to block (e.g. youtube.com)")
    enabled: bool = Field(True, description="Whether this block rule is currently active")

    model_config = ConfigDict(from_attributes=True)


class BlockedWebsiteCreate(BlockedWebsiteBase):
    """
    Pydantic schema for creating/registering a new Blocked Website.
    """
    pass


class BlockedWebsiteResponse(BlockedWebsiteBase):
    """
    Pydantic schema for Blocked Website HTTP response data.
    """
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
