"""
Database Package Interface.
Exports essential database foundation components and ORM models for clean imports across the application.
"""
from .base import Base
from .database import engine
from .models import ActivityLog, Alert, ExamSession, Faculty, Student
from .session import SessionLocal, get_db

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "Student",
    "Faculty",
    "ExamSession",
    "ActivityLog",
    "Alert",
]
