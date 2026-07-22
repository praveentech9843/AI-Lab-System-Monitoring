"""
Event Queue — SQLite-backed offline event buffer.
Persists events to disk so they survive agent restarts.
Flushes automatically when backend becomes available.
"""
import json
import logging
import sqlite3
import threading
from datetime import datetime, timezone
from typing import List

import config

logger = logging.getLogger("agent.event_queue")

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS event_queue (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type TEXT    NOT NULL,
    confidence  REAL    NOT NULL DEFAULT 1.0,
    queued_at   TEXT    NOT NULL
);
"""


class EventQueue:
    """
    Thread-safe SQLite-backed queue for offline event buffering.
    Events are stored locally when the backend is unreachable and
    flushed in batches when connectivity is restored.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(config.QUEUE_DB_PATH, check_same_thread=False)
        self._conn.execute(_CREATE_TABLE_SQL)
        self._conn.commit()
        count = self.size()
        if count:
            logger.info("Offline queue loaded: %d pending events.", count)

    # ── Enqueue ──────────────────────────────────────────────────────

    def enqueue(self, activity_type: str, confidence: float = 1.0) -> None:
        """Add a single event to the queue."""
        with self._lock:
            current = self._get_size_unlocked()
            if current >= config.MAX_QUEUE_SIZE:
                # Drop oldest event to make room
                self._conn.execute("DELETE FROM event_queue WHERE id = (SELECT MIN(id) FROM event_queue)")
                logger.debug("Queue full — oldest event dropped.")
            self._conn.execute(
                "INSERT INTO event_queue (activity_type, confidence, queued_at) VALUES (?, ?, ?)",
                (activity_type, confidence, datetime.now(timezone.utc).isoformat()),
            )
            self._conn.commit()

    # ── Dequeue ──────────────────────────────────────────────────────

    def dequeue_batch(self, batch_size: int = None) -> List[dict]:
        """Fetch up to batch_size events from the queue (oldest first)."""
        size = batch_size or config.FLUSH_BATCH_SIZE
        with self._lock:
            cursor = self._conn.execute(
                "SELECT id, activity_type, confidence, queued_at FROM event_queue ORDER BY id ASC LIMIT ?",
                (size,),
            )
            rows = cursor.fetchall()
        return [
            {"_id": row[0], "activity_type": row[1], "confidence": row[2], "queued_at": row[3]}
            for row in rows
        ]

    def remove(self, event_ids: List[int]) -> None:
        """Remove successfully sent events from the queue."""
        if not event_ids:
            return
        with self._lock:
            placeholders = ",".join("?" * len(event_ids))
            self._conn.execute(
                f"DELETE FROM event_queue WHERE id IN ({placeholders})", event_ids
            )
            self._conn.commit()

    # ── Helpers ──────────────────────────────────────────────────────

    def size(self) -> int:
        with self._lock:
            return self._get_size_unlocked()

    def _get_size_unlocked(self) -> int:
        cursor = self._conn.execute("SELECT COUNT(*) FROM event_queue")
        return cursor.fetchone()[0]

    def flush(self, api_client) -> int:
        """
        Attempt to send all queued events using api_client.
        Returns the number of events successfully sent.
        """
        batch = self.dequeue_batch()
        if not batch:
            return 0

        sent_count = 0
        success_ids = []

        for event in batch:
            ok = api_client.post_activity(
                activity_type=event["activity_type"],
                confidence=event["confidence"],
            )
            if ok:
                success_ids.append(event["_id"])
                sent_count += 1

        if success_ids:
            self.remove(success_ids)
            logger.info("Flushed %d queued events.", sent_count)

        return sent_count

    def close(self) -> None:
        """Close the SQLite connection gracefully."""
        self._conn.close()
