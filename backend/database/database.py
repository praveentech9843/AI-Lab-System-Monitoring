"""
Database Engine Configuration Module.
Configures the SQLAlchemy 2.x engine using application settings for PostgreSQL connection.
"""
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from config import settings

# Production-ready SQLAlchemy Engine instance for PostgreSQL connection
engine: Engine = create_engine(
    url=settings.DATABASE_URL,
    echo=False,              # Set to True for SQL query logging during debugging
    pool_pre_ping=True,      # Validates connections before usage to prevent stale connection errors
    pool_size=10,            # Maximum number of permanent connections kept in the pool
    max_overflow=20,         # Maximum number of temporary connections allowed beyond pool_size
    pool_recycle=1800        # Recycles connections after 30 minutes to prevent server-side drops
)
