"""
Optimized WebSocket REST/Streaming Router Module.

Key optimizations applied:
1. In-process student/session cache — eliminates per-event SELECT * FROM students
2. In-process latest-state cache — populates from DB fallback if uninitialized
3. State persistence — active_application & active_website are never cleared to "None"
4. Screenshot pipeline: writes file, persists ComputerEvent record, broadcasts with timestamp cache-buster
5. Live periodic window synchronization & rate-limited alerts
"""
from datetime import datetime, timezone
import json
import base64
import os
import time
import uuid as _uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from websocket.manager import manager
from database.session import SessionLocal
from database.models import ComputerEvent, Student, ExamSession, ActivityLog, Alert

router = APIRouter(tags=["WebSockets"])

BLOCKED_DOMAIN_SET = {
    "chatgpt.com", "deepseek.com", "gemini.google.com",
    "youtube.com", "reddit.com", "facebook.com",
    "instagram.com", "tiktok.com", "twitter.com",
    "x.com", "whatsapp.com", "telegram.org",
}

TITLE_KEYWORD_MAP = {
    "youtube": "youtube.com", "chatgpt": "chatgpt.com",
    "deepseek": "deepseek.com", "gemini": "gemini.google.com",
    "reddit": "reddit.com", "facebook": "facebook.com",
    "instagram": "instagram.com", "tiktok": "tiktok.com",
    "twitter": "twitter.com", "whatsapp": "whatsapp.com",
    "telegram": "telegram.org",
}

BROWSER_EXES = {
    "chrome.exe", "msedge.exe", "firefox.exe",
    "opera.exe", "brave.exe", "vivaldi.exe", "chromium.exe",
}

# In-process caches
_student_cache: dict = {}
_CACHE_TTL = 120  # seconds

_state_cache: dict = {}
_recent_alerts: dict = {}
_ALERT_COOLDOWN = 60  # seconds


def is_domain_blocked(domain: str) -> bool:
    if not domain:
        return False
    d = domain.lower().strip()
    d = d.replace("https://", "").replace("http://", "").replace("www.", "")
    if d in BLOCKED_DOMAIN_SET:
        return True
    for blocked in BLOCKED_DOMAIN_SET:
        if d.endswith("." + blocked) or d == blocked:
            return True
    return False


def extract_domain_from_title(title: str, exe: str = "") -> str | None:
    if not title:
        return None
    if exe and exe.lower() not in BROWSER_EXES:
        return None
    title_lower = title.lower()
    for blocked in BLOCKED_DOMAIN_SET:
        if blocked in title_lower:
            return blocked
    for keyword, domain in TITLE_KEYWORD_MAP.items():
        if keyword in title_lower:
            return domain
    return None


def _get_cached_student_session(computer_id: str, db):
    now = time.monotonic()
    cached = _student_cache.get(computer_id)
    if cached:
        student, session, expires = cached
        if now < expires:
            return student, session

    idx = -1
    try:
        idx = int(computer_id.replace("PC-", "")) - 1
    except Exception:
        pass

    student = None
    session = None

    if idx >= 0:
        students = db.scalars(select(Student)).all()
        if 0 <= idx < len(students):
            student = students[idx]
            stmt_sess = (
                select(ExamSession)
                .where(ExamSession.student_id == student.id)
                .where(ExamSession.status == "active")
                .order_by(ExamSession.start_time.desc())
                .limit(1)
            )
            session = db.scalar(stmt_sess)

    _student_cache[computer_id] = (student, session, now + _CACHE_TTL)
    return student, session


def _get_state(computer_id: str, db=None) -> dict:
    """Return the in-memory state dict for a PC, populating from DB if uninitialized."""
    state = _state_cache.get(computer_id)
    if state is None or not state.get("active_application"):
        if state is None:
            state = {}
        if db:
            try:
                latest = db.scalar(
                    select(ComputerEvent)
                    .where(ComputerEvent.computer_id == computer_id)
                    .order_by(ComputerEvent.timestamp.desc())
                    .limit(1)
                )
                if latest:
                    if not state.get("active_application"):
                        state["active_application"] = latest.active_application or "Visual Studio Code"
                    if not state.get("active_website"):
                        state["active_website"] = latest.active_website or "None"
                    if not state.get("screenshot_path"):
                        state["screenshot_path"] = latest.screenshot_path
                    if "cpu_usage" not in state:
                        state["cpu_usage"] = latest.cpu_usage or 0.0
                    if "ram_usage" not in state:
                        state["ram_usage"] = latest.ram_usage or 0.0
            except Exception:
                pass
        _state_cache[computer_id] = state
    return state


def _update_state(computer_id: str, **kwargs):
    """Merge kwargs into state cache. Never overwrite valid app/domain with None."""
    existing = _state_cache.get(computer_id, {})
    for k, v in kwargs.items():
        if k in ("active_application", "active_website") and (v is None or v == "None"):
            continue
        existing[k] = v
    _state_cache[computer_id] = existing


def _should_alert(computer_id: str, domain: str) -> bool:
    key = f"{computer_id}::{domain}"
    now = time.monotonic()
    last = _recent_alerts.get(key, 0)
    if now - last < _ALERT_COOLDOWN:
        return False
    _recent_alerts[key] = now
    return True


async def _store_and_broadcast_alert(db, student, session, alert_type, severity, message, timestamp):
    db_alert = None
    if student:
        if not session:
            any_sess = db.scalar(
                select(ExamSession)
                .where(ExamSession.student_id == student.id)
                .order_by(ExamSession.start_time.desc())
                .limit(1)
            )
            session = any_sess

        if session:
            db_alert = Alert(
                id=_uuid.uuid4(),
                student_id=student.id,
                session_id=session.id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                created_at=timestamp,
            )
            db.add(db_alert)
            db.commit()

    alert_id = str(db_alert.id) if db_alert else str(_uuid.uuid4())
    await manager.broadcast({
        "event": "ALERT_TRIGGERED",
        "timestamp": timestamp.isoformat(),
        "data": {
            "id": alert_id,
            "student_id": str(student.id) if student else None,
            "student_name": student.name if student else "Unknown",
            "session_id": str(session.id) if session else None,
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "created_at": timestamp.isoformat(),
        }
    })
    return db_alert


def _build_computer_event_payload(evt_id, computer_id, student_name, state: dict, session, student, screenshot_data: str = None) -> dict:
    screenshot = state.get("screenshot_path")
    ts_ms = state.get("screenshot_timestamp")
    if screenshot and not ts_ms:
        ts_ms = int(time.time() * 1000)
        state["screenshot_timestamp"] = ts_ms

    app = state.get("active_application")
    if not app or app == "None":
        app = "Visual Studio Code"
    website = state.get("active_website") or "None"

    return {
        "event": "COMPUTER_EVENT",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "id": str(evt_id),
            "computer_id": computer_id,
            "student_name": student_name,
            "active_application": app,
            "active_website": website,
            "cpu_usage": state.get("cpu_usage", 0.0),
            "ram_usage": state.get("ram_usage", 0.0),
            "screenshot_path": f"{screenshot}?t={ts_ms}" if (screenshot and ts_ms) else screenshot,
            "screenshot_data": screenshot_data,
            "activity_type": state.get("activity_type", "normal"),
            "confidence": state.get("confidence", 1.0),
            "timestamp": state.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "session_id": str(session.id) if session else None,
            "student_id": str(student.id) if student else None,
        }
    }


@router.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    _hb_counter = 0

    try:
        while True:
            data = await websocket.receive_text()

            payload = None
            try:
                payload = json.loads(data)
            except Exception:
                payload = None

            if not (payload and isinstance(payload, dict) and "system_id" in payload and "type" in payload):
                await manager.broadcast({
                    "event": "LIVE_MESSAGE",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data": {"message": data}
                })
                continue

            system_id = payload.get("system_id", "SYSTEM_01")
            computer_id = system_id.replace("SYSTEM_", "PC-")
            msg_type = payload.get("type")
            msg_data = payload.get("data", {}) or {}
            timestamp_str = payload.get("timestamp", "")
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except Exception:
                timestamp = datetime.now(timezone.utc)

            db = SessionLocal()
            try:
                student, session = _get_cached_student_session(computer_id, db)
                student_name = student.name if student else "Unknown Student"
                state = _get_state(computer_id, db)

                # ══════════════════════════════════════════════════════════════
                if msg_type == "screen":
                    base64_img = msg_data.get("image")
                    if base64_img:
                        try:
                            img_bytes = base64.b64decode(base64_img)
                            os.makedirs("./static/screenshots", exist_ok=True)
                            filename = f"{computer_id}_latest.jpg"
                            filepath = f"./static/screenshots/{filename}"
                            with open(filepath, "wb") as f:
                                f.write(img_bytes)

                            _update_state(computer_id, screenshot_path=filename, screenshot_timestamp=int(time.time() * 1000))

                            evt_id = _uuid.uuid4()
                            cur_state = _get_state(computer_id, db)

                            new_evt = ComputerEvent(
                                id=evt_id,
                                computer_id=computer_id,
                                student_name=student_name,
                                active_application=cur_state.get("active_application", "Visual Studio Code"),
                                active_website=cur_state.get("active_website", "None"),
                                cpu_usage=cur_state.get("cpu_usage", 0.0),
                                ram_usage=cur_state.get("ram_usage", 0.0),
                                screenshot_path=filename,
                                activity_type="screenshot_update",
                                confidence=1.0,
                                timestamp=timestamp,
                            )
                            db.add(new_evt)
                            db.commit()

                            _update_state(computer_id, last_event_id=str(evt_id))

                            await manager.broadcast(
                                _build_computer_event_payload(evt_id, computer_id, student_name, _get_state(computer_id, db), session, student, screenshot_data=base64_img)
                            )
                        except Exception as ex:
                            print(f"Screenshot error: {ex}")

                # ══════════════════════════════════════════════════════════════
                elif msg_type == "heartbeat":
                    _hb_counter += 1
                    cpu = msg_data.get("cpu", state.get("cpu_usage", 0.0))
                    ram = msg_data.get("ram", state.get("ram_usage", 0.0))
                    _update_state(computer_id, cpu_usage=cpu, ram_usage=ram, activity_type="heartbeat")

                    evt_id = _uuid.uuid4()
                    if _hb_counter % 3 == 0:
                        cur_state = _get_state(computer_id, db)
                        new_evt = ComputerEvent(
                            id=evt_id,
                            computer_id=computer_id,
                            student_name=student_name,
                            active_application=cur_state.get("active_application", "Visual Studio Code"),
                            active_website=cur_state.get("active_website", "None"),
                            cpu_usage=cpu,
                            ram_usage=ram,
                            screenshot_path=cur_state.get("screenshot_path"),
                            activity_type="heartbeat",
                            confidence=1.0,
                            timestamp=timestamp,
                        )
                        db.add(new_evt)
                        if student and session:
                            db.add(ActivityLog(
                                id=_uuid.uuid4(),
                                session_id=session.id,
                                student_id=student.id,
                                activity_type="heartbeat",
                                confidence=1.0,
                                timestamp=timestamp,
                            ))
                        db.commit()
                        _update_state(computer_id, last_event_id=str(evt_id))

                    await manager.broadcast(
                        _build_computer_event_payload(evt_id, computer_id, student_name, _get_state(computer_id, db), session, student)
                    )

                # ══════════════════════════════════════════════════════════════
                elif msg_type == "processes":
                    evt_id = _uuid.uuid4()
                    cur_state = _get_state(computer_id, db)
                    new_evt = ComputerEvent(
                        id=evt_id,
                        computer_id=computer_id,
                        student_name=student_name,
                        active_application=cur_state.get("active_application", "Visual Studio Code"),
                        active_website=cur_state.get("active_website", "None"),
                        cpu_usage=cur_state.get("cpu_usage", 0.0),
                        ram_usage=cur_state.get("ram_usage", 0.0),
                        screenshot_path=cur_state.get("screenshot_path"),
                        activity_type="processes_scan",
                        confidence=1.0,
                        timestamp=timestamp,
                    )
                    db.add(new_evt)
                    db.commit()
                    _update_state(computer_id, activity_type="processes_scan", last_event_id=str(evt_id))

                # ══════════════════════════════════════════════════════════════
                elif msg_type == "browser":
                    domain = msg_data.get("domain", "")
                    executable = msg_data.get("executable", "Browser")

                    is_blocked = is_domain_blocked(domain)
                    activity_type = f"blocked_website:{domain}" if is_blocked else "browser_activity"
                    confidence = 0.98 if is_blocked else 1.0

                    _update_state(computer_id,
                        active_application=executable,
                        active_website=domain,
                        activity_type=activity_type,
                        confidence=confidence,
                    )

                    evt_id = _uuid.uuid4()
                    cur_state = _get_state(computer_id, db)
                    new_evt = ComputerEvent(
                        id=evt_id,
                        computer_id=computer_id,
                        student_name=student_name,
                        active_application=executable or "Browser",
                        active_website=domain,
                        cpu_usage=cur_state.get("cpu_usage", 0.0),
                        ram_usage=cur_state.get("ram_usage", 0.0),
                        screenshot_path=cur_state.get("screenshot_path"),
                        activity_type=activity_type,
                        confidence=confidence,
                        timestamp=timestamp,
                    )
                    db.add(new_evt)

                    db_act = None
                    if student and session:
                        db_act = ActivityLog(
                            id=_uuid.uuid4(),
                            session_id=session.id,
                            student_id=student.id,
                            activity_type=activity_type,
                            confidence=confidence,
                            timestamp=timestamp,
                        )
                        db.add(db_act)

                    db.commit()
                    _update_state(computer_id, last_event_id=str(evt_id))

                    await manager.broadcast(
                        _build_computer_event_payload(evt_id, computer_id, student_name, _get_state(computer_id, db), session, student)
                    )

                    if db_act:
                        await manager.broadcast({
                            "event": "ACTIVITY_LOGGED",
                            "timestamp": timestamp.isoformat(),
                            "data": {
                                "id": str(db_act.id),
                                "session_id": str(db_act.session_id),
                                "student_id": str(db_act.student_id),
                                "activity_type": activity_type,
                                "confidence": confidence,
                                "timestamp": timestamp.isoformat(),
                            }
                        })

                    if is_blocked and _should_alert(computer_id, domain):
                        await _store_and_broadcast_alert(
                            db, student, session,
                            alert_type="blocked_website",
                            severity="CRITICAL",
                            message=f"Restricted website accessed: {domain} on {computer_id} ({student_name})",
                            timestamp=timestamp,
                        )

                # ══════════════════════════════════════════════════════════════
                elif msg_type in ("register", "window", "clipboard", "keyboard"):
                    cur_state = _get_state(computer_id, db)
                    active_app = cur_state.get("active_application", "Visual Studio Code")
                    active_website = cur_state.get("active_website", "None")
                    cpu_usage = cur_state.get("cpu_usage", 0.0)
                    ram_usage = cur_state.get("ram_usage", 0.0)
                    activity_type = "normal"
                    confidence = 1.0
                    generate_alert = False
                    alert_domain = None

                    if msg_type == "register":
                        activity_type = "agent_registered"

                    elif msg_type == "window":
                        active_app = msg_data.get("executable") or active_app
                        title = msg_data.get("title", "")
                        detected_domain = msg_data.get("domain")

                        if detected_domain:
                            active_website = detected_domain
                        elif title:
                            active_website = extract_domain_from_title(title, active_app) or active_website

                        activity_type = "normal_coding_activity"
                        website_to_check = detected_domain or active_website

                        if is_domain_blocked(website_to_check):
                            activity_type = f"blocked_website:{website_to_check}"
                            confidence = 0.98
                            if _should_alert(computer_id, website_to_check):
                                generate_alert = True
                                alert_domain = website_to_check
                        elif "code" in active_app.lower() or "vs" in active_app.lower():
                            activity_type = "coding_activity"

                    elif msg_type == "clipboard":
                        activity_type = "copy_paste"
                        confidence = 0.8

                    elif msg_type == "keyboard":
                        shortcut = msg_data.get("shortcut", "")
                        if shortcut == "Alt+Tab":
                            activity_type = "tab_switch"; confidence = 0.95
                        elif shortcut in ("Ctrl+C", "Ctrl+V"):
                            activity_type = "copy_paste"; confidence = 0.9
                        elif shortcut == "PrintScreen":
                            activity_type = "screenshot_key"; confidence = 0.85
                        else:
                            activity_type = f"keyboard_shortcut:{shortcut}"; confidence = 0.8

                    _update_state(computer_id,
                        active_application=active_app,
                        active_website=active_website,
                        cpu_usage=cpu_usage,
                        ram_usage=ram_usage,
                        activity_type=activity_type,
                        confidence=confidence,
                        timestamp=timestamp.isoformat(),
                    )

                    evt_id = _uuid.uuid4()
                    new_evt = ComputerEvent(
                        id=evt_id,
                        computer_id=computer_id,
                        student_name=student_name,
                        active_application=active_app,
                        active_website=active_website,
                        cpu_usage=cpu_usage,
                        ram_usage=ram_usage,
                        screenshot_path=cur_state.get("screenshot_path"),
                        activity_type=activity_type,
                        confidence=confidence,
                        timestamp=timestamp,
                    )
                    db.add(new_evt)

                    db_act = None
                    if student and session:
                        db_act = ActivityLog(
                            id=_uuid.uuid4(),
                            session_id=session.id,
                            student_id=student.id,
                            activity_type=activity_type,
                            confidence=confidence,
                            timestamp=timestamp,
                        )
                        db.add(db_act)

                    db.commit()
                    _update_state(computer_id, last_event_id=str(evt_id))

                    await manager.broadcast(
                        _build_computer_event_payload(evt_id, computer_id, student_name, _get_state(computer_id, db), session, student)
                    )

                    if db_act:
                        await manager.broadcast({
                            "event": "ACTIVITY_LOGGED",
                            "timestamp": timestamp.isoformat(),
                            "data": {
                                "id": str(db_act.id),
                                "session_id": str(db_act.session_id),
                                "student_id": str(db_act.student_id),
                                "activity_type": activity_type,
                                "confidence": confidence,
                                "timestamp": timestamp.isoformat(),
                            }
                        })

                    if generate_alert and alert_domain:
                        await _store_and_broadcast_alert(
                            db, student, session,
                            alert_type="blocked_website",
                            severity="CRITICAL",
                            message=f"Restricted website accessed: {alert_domain} on {computer_id} ({student_name})",
                            timestamp=timestamp,
                        )

            except Exception as db_ex:
                print(f"WS handler error [{msg_type}]: {db_ex}")
                import traceback
                traceback.print_exc()
            finally:
                db.close()

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
