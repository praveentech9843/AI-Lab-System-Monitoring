"""
WebSocket Package Interface.
Exports ConnectionManager, global manager instance, router, and event formatters.
"""
from .events import (
    alert_created_event,
    exam_finished_event,
    exam_started_event,
    student_join_event,
    student_leave_event,
)
from .manager import ConnectionManager, manager
from .routes import router

__all__ = [
    "ConnectionManager",
    "manager",
    "router",
    "student_join_event",
    "student_leave_event",
    "exam_started_event",
    "exam_finished_event",
    "alert_created_event",
]
