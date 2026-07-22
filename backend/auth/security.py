"""
Password Security Module.
Provides password hashing and verification utilities using pwdlib.
"""
from pwdlib import PasswordHash

# Initialize recommended PasswordHash instance (Argon2 / bcrypt standard)
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hashes a plaintext password string using pwdlib.
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a hashed password string using pwdlib.
    """
    return password_hash.verify(plain_password, hashed_password)
