"""
Database Declarative Base Module.
Provides the central SQLAlchemy 2.x DeclarativeBase class for ORM models.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Abstract Base Class for all database ORM models.

    Every SQLAlchemy ORM model in the application must inherit from this class
    to enable automatic table metadata collection and relationship mapping.
    """
    pass
