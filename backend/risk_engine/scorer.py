"""
AI Risk Engine Event Scorer Module.
Calculates individual risk score for a given event type using configured thresholds.
"""
from risk_engine.thresholds import EVENT_THRESHOLDS


def calculate_event_score(event_type: str) -> int:
    """
    Returns the numeric risk score for a given event type.
    Unknown or unrecognized event types return 0.
    """
    normalized_type = event_type.upper().strip()
    return EVENT_THRESHOLDS.get(normalized_type, 0)
