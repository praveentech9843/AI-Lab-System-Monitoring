"""
Optimized Database Engine Configuration Module.
- SQLite WAL mode: eliminates reader/writer blocking, dramatically reduces write latency
- Synchronous=NORMAL: safe durability with much lower write overhead than FULL
- Cache size: 64MB in-memory page cache to avoid repeated disk reads
- Pooled connections with pre-ping health checks
"""
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

from config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    # SQLite: single writer, allow more concurrent readers via WAL
    engine_kwargs["pool_size"] = 1
else:
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800,
    })

engine: Engine = create_engine(
    url=settings.DATABASE_URL,
    **engine_kwargs
)

# ── SQLite-specific performance pragmas ───────────────────────────────────────
if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        # WAL mode: readers never block writers, writers never block readers
        cursor.execute("PRAGMA journal_mode=WAL")
        # NORMAL sync: safe on power loss (SQLite docs: "good enough for most apps")
        cursor.execute("PRAGMA synchronous=NORMAL")
        # 64MB page cache in memory — avoids repeated disk seeks on hot data
        cursor.execute("PRAGMA cache_size=-65536")
        # Keep temp tables in memory
        cursor.execute("PRAGMA temp_store=MEMORY")
        # 5-second busy timeout instead of immediate lock error
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()
