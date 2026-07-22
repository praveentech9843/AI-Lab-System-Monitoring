"""
Reports Statistics Helper Module.
Provides mathematical and statistical aggregation utilities handling empty inputs safely.
"""
from typing import List, Union


def calculate_average_score(scores: List[Union[int, float]]) -> float:
    """
    Calculates the arithmetic average score of a numeric list.
    Returns 0.0 if the input list is empty.
    """
    if not scores:
        return 0.0
    return round(float(sum(scores)) / len(scores), 2)


def calculate_highest_score(scores: List[int]) -> int:
    """
    Calculates the maximum score from an integer list.
    Returns 0 if the input list is empty.
    """
    if not scores:
        return 0
    return max(scores)


def count_total_alerts(alert_count_list: List[int]) -> int:
    """
    Sums a list of integer alert counts.
    Returns 0 if the input list is empty.
    """
    if not alert_count_list:
        return 0
    return sum(alert_count_list)
