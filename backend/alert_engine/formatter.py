"""
Alert Engine Message Formatter Module.
Provides helper functions to format human-readable alert messages consistently.
"""
from typing import List


def format_alert_message(triggered_events: List[str], total_score: int) -> str:
    """
    Formats a list of triggered event names into a human-readable alert message.
    """
    if not triggered_events:
        return f"Student triggered unusual activity (Total Score: {total_score})."

    events_str = ", ".join(triggered_events)
    return f"Student triggered: {events_str} (Total Score: {total_score})"
