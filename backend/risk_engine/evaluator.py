"""
AI Risk Engine Evaluator Module.
Evaluates a list of risk events for a session and computes total risk score and risk level.
"""
from typing import List, Union
from uuid import UUID

from risk_engine.models import RiskEvent, RiskResult
from risk_engine.scorer import calculate_event_score


def evaluate_risk(
    student_id: Union[UUID, str],
    session_id: Union[UUID, str],
    events: List[RiskEvent]
) -> RiskResult:
    """
    Evaluates a collection of RiskEvent objects for a student session.
    Calculates total confidence-weighted score, sorted unique triggered event names, and classifies risk level.
    """
    total_score: int = 0
    triggered_events_set = set()

    for event in events:
        base_score = calculate_event_score(event.event_type)
        score = int(base_score * event.confidence)
        total_score += score
        if event.event_type:
            triggered_events_set.add(event.event_type)

    if total_score <= 20:
        risk_level = "LOW"
    elif total_score <= 50:
        risk_level = "MEDIUM"
    elif total_score <= 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    return RiskResult(
        student_id=student_id,
        session_id=session_id,
        total_score=total_score,
        risk_level=risk_level,
        triggered_events=sorted(triggered_events_set)
    )
