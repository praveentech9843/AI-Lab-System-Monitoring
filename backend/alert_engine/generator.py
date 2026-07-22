"""
Alert Engine Generator Module.
Generates structured AlertResult objects from AlertRequest inputs.
"""
import uuid
from datetime import datetime, timezone

from alert_engine.formatter import format_alert_message
from alert_engine.models import AlertRequest, AlertResult
from alert_engine.rules import get_severity_for_risk_level, get_title_for_severity


def generate_alert(request: AlertRequest) -> AlertResult:
    """
    Generates an AlertResult notification object based on an AlertRequest input.
    """
    severity = get_severity_for_risk_level(request.risk_level)
    title = get_title_for_severity(severity)
    message = format_alert_message(request.triggered_events, request.total_score)
    alert_id = uuid.uuid4()
    timestamp = datetime.now(timezone.utc)

    return AlertResult(
        alert_id=alert_id,
        student_id=request.student_id,
        session_id=request.session_id,
        severity=severity,
        title=title,
        message=message,
        timestamp=timestamp,
    )
