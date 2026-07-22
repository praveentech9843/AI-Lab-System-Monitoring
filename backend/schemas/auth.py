"""
Authentication Pydantic Schemas Module.
Defines request and response schemas for login and token responses.
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """
    Pydantic schema for user login requests.
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User plaintext password")

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """
    Pydantic schema for JWT access token responses.
    """
    access_token: str = Field(..., description="Signed JWT access token string")
    token_type: str = Field("bearer", description="Token type designation")

    model_config = ConfigDict(from_attributes=True)
