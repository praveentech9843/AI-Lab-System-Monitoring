"""
Computer Monitoring REST API Router.
Provides endpoints for workstation events, screenshot uploads, latest states, and details.
"""
import os
import shutil
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.session import get_db
from database.models import ComputerEvent, Student, ExamSession, ActivityLog, Alert
from schemas.computer import ComputerEventCreate, ComputerEventResponse
from crud.computer import (
    create_computer_event,
    get_latest_computer_states,
    get_computer_event_history,
    get_latest_screenshot,
)
from websocket.manager import manager

router = APIRouter(prefix="/computers", tags=["Computers"])

SCREENSHOTS_DIR = "./static/screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

BLOCKED_WEBSITES = [
    "chatgpt.com",
    "deepseek.com",
    "gemini.google.com",
    "youtube.com",
    "reddit.com",
    "facebook.com",
    "instagram.com",
]

def is_domain_blocked(domain: str) -> bool:
    if not domain:
        return False
    d = domain.lower()
    return any(blocked in d or d in blocked for blocked in BLOCKED_WEBSITES)

@router.post("/event", response_model=ComputerEventResponse, status_code=status.HTTP_201_CREATED)
async def post_monitoring_event(
    event_data: ComputerEventCreate,
    db: Session = Depends(get_db)
):
    """
    Receives and processes workstation monitoring events.
    Applies blocked website checks, generates alerts, logs activities, and broadcasts real-time updates.
    """
    # 1. Resolve student and active session
    student = None
    session = None
    if event_data.student_name:
        # Match student by name case-insensitive
        stmt = select(Student).where(Student.name.ilike(event_data.student_name.strip()))
        student = db.scalar(stmt)
        if student:
            # Match latest active session
            stmt_sess = (
                select(ExamSession)
                .where(ExamSession.student_id == student.id)
                .where(ExamSession.status == "active")
                .order_by(ExamSession.start_time.desc())
                .limit(1)
            )
            session = db.scalar(stmt_sess)

    # 2. Check for blocked website
    is_blocked = is_domain_blocked(event_data.active_website)
    if is_blocked:
        # Override event properties to flag the violation
        event_data.activity_type = f"blocked_website:domain={event_data.active_website}"
        event_data.confidence = 0.98

    # 3. Create ComputerEvent log in DB
    db_event = create_computer_event(db, event_data)

    # 4. Bridge to standard ActivityLog if active session exists
    db_act = None
    if student and session:
        db_act = ActivityLog(
            session_id=session.id,
            student_id=student.id,
            activity_type=db_event.activity_type,
            confidence=db_event.confidence,
            timestamp=db_event.timestamp
        )
        db.add(db_act)
        try:
            db.commit()
            db.refresh(db_act)
        except Exception:
            db.rollback()

    # 5. Handle Alert generation on Blocked Website
    db_alert = None
    if is_blocked and student and session:
        db_alert = Alert(
            student_id=student.id,
            session_id=session.id,
            alert_type="blocked_website",
            severity="CRITICAL",
            message=f"Restricted website access: {event_data.active_website} at {event_data.computer_id}",
            created_at=db_event.timestamp
        )
        db.add(db_alert)
        try:
            db.commit()
            db.refresh(db_alert)
        except Exception:
            db.rollback()

    # 6. Prepare and broadcast Real-Time Updates via WebSocket
    payload_event = {
        "event": "COMPUTER_EVENT",
        "timestamp": db_event.timestamp.isoformat(),
        "data": {
            "id": str(db_event.id),
            "computer_id": db_event.computer_id,
            "student_name": db_event.student_name,
            "active_application": db_event.active_application,
            "active_website": db_event.active_website,
            "cpu_usage": db_event.cpu_usage,
            "ram_usage": db_event.ram_usage,
            "screenshot_path": db_event.screenshot_path,
            "activity_type": db_event.activity_type,
            "confidence": db_event.confidence,
            "timestamp": db_event.timestamp.isoformat(),
            # Add session context for real-time dashboard listeners
            "session_id": str(session.id) if session else None,
            "student_id": str(student.id) if student else None,
        }
    }
    await manager.broadcast(payload_event)

    # If bridged activity log created, broadcast it as well
    if db_act:
        await manager.broadcast({
            "event": "ACTIVITY_LOGGED",
            "timestamp": db_act.timestamp.isoformat(),
            "data": {
                "id": str(db_act.id),
                "session_id": str(db_act.session_id),
                "student_id": str(db_act.student_id),
                "activity_type": db_act.activity_type,
                "confidence": db_act.confidence,
                "timestamp": db_act.timestamp.isoformat(),
            }
        })

    # Broadcast alert if generated
    if db_alert:
        await manager.broadcast({
            "event": "ALERT_TRIGGERED",
            "timestamp": db_alert.created_at.isoformat(),
            "data": {
                "id": str(db_alert.id),
                "student_id": str(db_alert.student_id),
                "session_id": str(db_alert.session_id),
                "alert_type": db_alert.alert_type,
                "severity": db_alert.severity,
                "message": db_alert.message,
                "created_at": db_alert.created_at.isoformat(),
            }
        })

    return db_event

@router.post("/upload-screenshot/{computer_id}", status_code=status.HTTP_201_CREATED)
async def upload_screenshot(
    computer_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Uploads a screenshot image for a specific computer.
    Saves the file to the static screenshots directory.
    """
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{computer_id}_{ts}{ext}"
    filepath = os.path.join(SCREENSHOTS_DIR, filename)

    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {exc}"
        )

    # Find the latest event for this computer to link the screenshot path
    stmt = (
        select(ComputerEvent)
        .where(ComputerEvent.computer_id == computer_id)
        .order_by(ComputerEvent.timestamp.desc())
        .limit(1)
    )
    latest_event = db.scalar(stmt)
    if latest_event:
        latest_event.screenshot_path = filename
        try:
            db.commit()
        except Exception:
            db.rollback()

    return {
        "filename": filename,
        "screenshot_url": f"/static/screenshots/{filename}"
    }

@router.get("/states", response_model=List[ComputerEventResponse], status_code=status.HTTP_200_OK)
def read_latest_states(db: Session = Depends(get_db)):
    """
    Retrieves the latest state/status for every unique computer.
    """
    states = get_latest_computer_states(db)
    result = []
    for s in states:
        evt = ComputerEventResponse.model_validate(s)
        if evt.screenshot_path:
            ts = int(datetime.now(timezone.utc).timestamp() * 1000)
            evt.screenshot_path = f"{evt.screenshot_path}?t={ts}"
        result.append(evt)
    return result

@router.get("/{computer_id}/latest-screenshot", status_code=status.HTTP_200_OK)
def read_latest_screenshot(computer_id: str, db: Session = Depends(get_db)):
    """
    Returns the latest screenshot URL for a specific computer.
    """
    filename = get_latest_screenshot(db, computer_id)
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No screenshots found for this computer."
        )
    return {
        "computer_id": computer_id,
        "screenshot_url": f"http://localhost:8000/static/screenshots/{filename}",
        "filename": filename
    }

@router.get("/{computer_id}/details", status_code=status.HTTP_200_OK)
def read_computer_details(computer_id: str, db: Session = Depends(get_db)):
    """
    Retrieves complete details for a computer card, including last state and alert history.
    """
    # 1. Fetch latest event
    stmt_event = (
        select(ComputerEvent)
        .where(ComputerEvent.computer_id == computer_id)
        .order_by(ComputerEvent.timestamp.desc())
        .limit(1)
    )
    latest_event = db.scalar(stmt_event)
    if not latest_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No logs found for this computer."
        )

    # 2. Fetch student details and active session
    alerts_list = []
    student_data = None
    if latest_event.student_name:
        stmt_stud = select(Student).where(Student.name.ilike(latest_event.student_name.strip()))
        student = db.scalar(stmt_stud)
        if student:
            from schemas.student import StudentResponse
            student_data = StudentResponse.model_validate(student)
            # Get alerts list
            stmt_alerts = (
                select(Alert)
                .where(Alert.student_id == student.id)
                .order_by(Alert.created_at.desc())
                .limit(20)
            )
            alerts_list = db.scalars(stmt_alerts).all()

    latest_state_data = None
    if latest_event:
        latest_state_data = ComputerEventResponse.model_validate(latest_event)
        if latest_state_data.screenshot_path:
            ts = int(datetime.now(timezone.utc).timestamp() * 1000)
            latest_state_data.screenshot_path = f"{latest_state_data.screenshot_path}?t={ts}"

    return {
        "computer_id": computer_id,
        "latest_state": latest_state_data,
        "student": student_data,
        "alerts": [
            {
                "id": str(a.id),
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "created_at": a.created_at.isoformat()
            } for a in alerts_list
        ]
    }


from pydantic import BaseModel
class ActionPayload(BaseModel):
    action: str

@router.post("/{computer_id}/action", status_code=status.HTTP_200_OK)
async def trigger_computer_action(
    computer_id: str,
    payload: ActionPayload,
    db: Session = Depends(get_db)
):
    """
    Executes administrative actions on a computer card (lock, unlock, logout, capture, flag, mark safe).
    """
    action = payload.action.lower()
    valid_actions = ["lock", "unlock", "logout", "screenshot", "safe", "suspicious"]
    if action not in valid_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action. Choose from: {valid_actions}"
        )

    # Fetch latest event for this computer to modify/refer
    stmt = (
        select(ComputerEvent)
        .where(ComputerEvent.computer_id == computer_id)
        .order_by(ComputerEvent.timestamp.desc())
        .limit(1)
    )
    latest_event = db.scalar(stmt)

    if action in ("safe", "suspicious"):
        if not latest_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No events registered for this computer yet."
            )
        
        # Modify DB state
        if action == "safe":
            latest_event.activity_type = "marked_safe"
            latest_event.confidence = 1.0
        else:
            latest_event.activity_type = "marked_suspicious"
            latest_event.confidence = 1.0

        try:
            db.commit()
            db.refresh(latest_event)
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database update failed."
            )

        # Broadcast the updated COMPUTER_EVENT
        await manager.broadcast({
            "event": "COMPUTER_EVENT",
            "timestamp": latest_event.timestamp.isoformat(),
            "data": {
                "id": str(latest_event.id),
                "computer_id": latest_event.computer_id,
                "student_name": latest_event.student_name,
                "active_application": latest_event.active_application,
                "active_website": latest_event.active_website,
                "cpu_usage": latest_event.cpu_usage,
                "ram_usage": latest_event.ram_usage,
                "screenshot_path": latest_event.screenshot_path,
                "activity_type": latest_event.activity_type,
                "confidence": latest_event.confidence,
                "timestamp": latest_event.timestamp.isoformat()
            }
        })
    else:
        # Broadcast the COMMAND_TRIGGERED action so any listening student agent or client behaves accordingly
        await manager.broadcast({
            "event": "COMMAND_TRIGGERED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "computer_id": computer_id,
                "command": action
            }
        })

    return {
        "status": "success",
        "computer_id": computer_id,
        "action": action
    }

