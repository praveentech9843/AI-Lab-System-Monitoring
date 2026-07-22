"""
Computer Event CRUD Operations Module.
Handles persisting and querying student workstation logs and state records.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, desc, func
from sqlalchemy.orm import Session
from database.models import ComputerEvent
from schemas.computer import ComputerEventCreate


def create_computer_event(db: Session, event_create: ComputerEventCreate) -> ComputerEvent:
    """
    Creates and stores a new monitoring event from a workstation agent.
    """
    db_event = ComputerEvent(
        computer_id=event_create.computer_id,
        student_name=event_create.student_name,
        active_application=event_create.active_application,
        active_website=event_create.active_website,
        cpu_usage=event_create.cpu_usage,
        ram_usage=event_create.ram_usage,
        screenshot_path=event_create.screenshot_path,
        activity_type=event_create.activity_type,
        confidence=event_create.confidence,
    )
    db.add(db_event)
    try:
        db.commit()
        db.refresh(db_event)
    except Exception:
        db.rollback()
        raise
    return db_event


def get_latest_computer_states(db: Session) -> List[ComputerEvent]:
    """
    Returns the latest event/state for every unique computer_id.
    Uses a standard window function to select the row with the most recent timestamp per computer.
    """
    # Select subquery with row numbers partitioned by computer_id
    subquery = (
        select(
            ComputerEvent,
            func.row_number().over(
                partition_by=ComputerEvent.computer_id,
                order_by=ComputerEvent.timestamp.desc()
            ).label("row_num")
        )
    ).subquery()

    # Query matching only the first row (the latest event) per computer_id
    stmt = (
        select(ComputerEvent)
        .select_from(subquery)
        .where(subquery.c.row_num == 1)
        .order_by(subquery.c.computer_id.asc())
    )

    return list(db.scalars(stmt).all())


def get_computer_event_history(db: Session, computer_id: str, limit: int = 50) -> List[ComputerEvent]:
    """
    Retrieves chronological log of monitoring events for a single computer.
    """
    stmt = (
        select(ComputerEvent)
        .where(ComputerEvent.computer_id == computer_id)
        .order_by(ComputerEvent.timestamp.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_latest_screenshot(db: Session, computer_id: str) -> Optional[str]:
    """
    Retrieves the screenshot path from the latest event that has one for the computer.
    """
    stmt = (
        select(ComputerEvent.screenshot_path)
        .where(ComputerEvent.computer_id == computer_id)
        .where(ComputerEvent.screenshot_path.is_not(None))
        .where(ComputerEvent.screenshot_path != "")
        .order_by(ComputerEvent.timestamp.desc())
        .limit(1)
    )
    return db.scalar(stmt)
