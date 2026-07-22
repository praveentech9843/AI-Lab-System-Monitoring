"""
Alert Engine Rules Module.
Defines severity mappings and title templates for risk levels.
"""
from typing import Dict

# Map risk level to alert severity designation
SEVERITY_MAP: Dict[str, str] = {
    "LOW": "INFO",
    "MEDIUM": "WARNING",
    "HIGH": "HIGH",
    "CRITICAL": "CRITICAL",
}

# Map alert severity to descriptive title templates
TITLE_TEMPLATES: Dict[str, str] = {
    "INFO": "Low Risk Activity Notification",
    "WARNING": "Medium Risk Behavior Warning",
    "HIGH": "High Risk Anomaly Alert",
    "CRITICAL": "Critical Security Violation Alert",
}


def get_severity_for_risk_level(risk_level: str) -> str:
    """
    Returns the severity string corresponding to a risk level. Defaults to INFO if unknown.
    """
    normalized_level = risk_level.upper().strip()
    return SEVERITY_MAP.get(normalized_level, "INFO")


def get_title_for_severity(severity: str) -> str:
    """
    Returns the descriptive title template corresponding to an alert severity.
    """
    normalized_severity = severity.upper().strip()
    return TITLE_TEMPLATES.get(normalized_severity, "System Alert Notification")
