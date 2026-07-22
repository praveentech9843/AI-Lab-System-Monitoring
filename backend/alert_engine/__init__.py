"""
Alert Engine Package Interface.
Exports Pydantic models, alert rules, message formatters, and the alert generator function.
"""
from .formatter import format_alert_message
from .generator import generate_alert
from .models import AlertRequest, AlertResult
from .rules import (
    SEVERITY_MAP,
    TITLE_TEMPLATES,
    get_severity_for_risk_level,
    get_title_for_severity,
)

__all__ = [
    "AlertRequest",
    "AlertResult",
    "generate_alert",
    "format_alert_message",
    "get_severity_for_risk_level",
    "get_title_for_severity",
    "SEVERITY_MAP",
    "TITLE_TEMPLATES",
]
