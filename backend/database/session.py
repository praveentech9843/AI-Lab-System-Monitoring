"""
Database Session and Dependency Injection Module.
Provides SQLAlchemy Session management and the FastAPI get_db dependency.
"""
from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from database.database import engine

# Configured session factory bound to the database engine
SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Prevents attribute access errors on objects after session commit
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session per request.

    Guarantees that the database session is safely closed when the request
    is completed, even if an exception occurs during request handling.

    Yields:
        Session: An active SQLAlchemy database session object.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
