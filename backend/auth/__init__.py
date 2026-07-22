"""
Authentication Package Interface.
Exports all security, JWT, authentication, and dependency utilities.
"""
from .auth import authenticate_faculty, authenticate_student
from .dependencies import get_current_user, oauth2_scheme
from .jwt_handler import create_access_token, decode_access_token
from .security import hash_password, verify_password

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "authenticate_student",
    "authenticate_faculty",
    "oauth2_scheme",
    "get_current_user",
]
