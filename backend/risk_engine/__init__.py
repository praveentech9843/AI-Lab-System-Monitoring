"""
Risk Engine Package Interface.
Exports Pydantic models, threshold constants, event scorer, and risk evaluator functions.
"""
from .evaluator import evaluate_risk
from .models import RiskEvent, RiskResult
from .scorer import calculate_event_score
from .thresholds import (
    FACE_MISSING,
    HEAD_DOWN,
    LOOKING_AWAY,
    MULTIPLE_FACE,
    PHONE_DETECTED,
    TAB_SWITCH,
)

__all__ = [
    "RiskEvent",
    "RiskResult",
    "calculate_event_score",
    "evaluate_risk",
    "TAB_SWITCH",
    "MULTIPLE_FACE",
    "FACE_MISSING",
    "HEAD_DOWN",
    "LOOKING_AWAY",
    "PHONE_DETECTED",
]
