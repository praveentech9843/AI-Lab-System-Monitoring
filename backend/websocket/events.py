"""
WebSocket Event Formatter Module.
Provides helper functions that produce structured event payloads with ISO UTC timestamps.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Union
from uuid import UUID


def _get_utc_timestamp() -> str:
    """
    Helper function to generate an ISO 8601 UTC timestamp string.
    """
    return datetime.now(timezone.utc).isoformat()


def student_join_event(student_id: Union[UUID, str]) -> Dict[str, Any]:
    """
    Creates a structured event payload when a student joins the monitoring stream.
    """
    return {
        "event": "STUDENT_JOINED",
        "timestamp": _get_utc_timestamp(),
        "data": {"student_id": str(student_id)}
    }


def student_leave_event(student_id: Union[UUID, str]) -> Dict[str, Any]:
    """
    Creates a structured event payload when a student leaves the monitoring stream.
    """
    return {
        "event": "STUDENT_LEFT",
        "timestamp": _get_utc_timestamp(),
        "data": {"student_id": str(student_id)}
    }


def exam_started_event(session_id: Union[UUID, str]) -> Dict[str, Any]:
    """
    Creates a structured event payload when an exam session commences.
    """
    return {
        "event": "EXAM_STARTED",
        "timestamp": _get_utc_timestamp(),
        "data": {"session_id": str(session_id)}
    }


def exam_finished_event(session_id: Union[UUID, str]) -> Dict[str, Any]:
    """
    Creates a structured event payload when an exam session finishes.
    """
    return {
        "event": "EXAM_FINISHED",
        "timestamp": _get_utc_timestamp(),
        "data": {"session_id": str(session_id)}
    }


def alert_created_event(alert_id: Union[UUID, str]) -> Dict[str, Any]:
    """
    Creates a structured event payload when an AI anomaly alert is triggered.
    """
    return {
        "event": "ALERT_CREATED",
        "timestamp": _get_utc_timestamp(),
        "data": {"alert_id": str(alert_id)}
    }
