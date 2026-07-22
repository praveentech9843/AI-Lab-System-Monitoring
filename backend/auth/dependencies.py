"""
Authentication FastAPI Dependencies Module.
Provides OAuth2 token extraction and current user payload verification.
"""
from typing import Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.jwt_handler import decode_access_token

# OAuth2 scheme for extracting Bearer tokens from incoming Authorization headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    FastAPI dependency that extracts and validates the JWT Bearer token.
    Returns the decoded token payload dictionary. Does not query the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    return payload
