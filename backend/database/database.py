"""
Database Engine Configuration Module.
Configures the SQLAlchemy 2.x engine using application settings for PostgreSQL or SQLite connections.
"""
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800,
    })

# SQLAlchemy Engine instance configured based on target DATABASE_URL
engine: Engine = create_engine(
    url=settings.DATABASE_URL,
    **engine_kwargs
)
