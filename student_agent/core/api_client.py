"""
API Client — Handles authentication, JWT token management,
retry logic, screenshot uploads, and posting computer monitoring events.
"""
import logging
import time
import os
from typing import Optional

import requests

import config

logger = logging.getLogger("agent.api_client")


class APIClient:
    """
    HTTP client wrapping the FastAPI backend.
    Manages JWT tokens and posts computer state events and file uploads.
    """

    def __init__(self) -> None:
        self._token: Optional[str] = None
        self._student_id: Optional[str] = None
        self._student_name: Optional[str] = None
        self._session_id: Optional[str] = None
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    # ── Auth ────────────────────────────────────────────────────────

    def login(self) -> bool:
        """Authenticate with the backend and store JWT token."""
        url = f"{config.BACKEND_URL}/auth/student/login"
        payload = {"email": config.STUDENT_EMAIL, "password": config.STUDENT_PASS}
        try:
            resp = self._session.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                self._token = data.get("access_token")
                self._session.headers.update({"Authorization": f"Bearer {self._token}"})
                logger.info("Authentication successful.")
                return True
            logger.warning("Login failed: HTTP %s — %s", resp.status_code, resp.text)
        except requests.RequestException as exc:
            logger.error("Login request error: %s", exc)
        return False

    def resolve_student_id(self) -> bool:
        """Fetch student profile to extract student_id and student_name."""
        url = f"{config.BACKEND_URL}/students/?skip=0&limit=200"
        try:
            resp = self._session.get(url, timeout=config.REQUEST_TIMEOUT)
            if resp.status_code == 200:
                for student in resp.json():
                    if student.get("email", "").lower() == config.STUDENT_EMAIL.lower():
                        self._student_id = str(student["id"])
                        self._student_name = student.get("name", "Student")
                        logger.info("Resolved student_id: %s | name: %s", self._student_id, self._student_name)
                        return True
            logger.warning("Could not resolve student_id from /students endpoint.")
        except requests.RequestException as exc:
            logger.error("resolve_student_id error: %s", exc)
        return False

    def resolve_session_id(self) -> bool:
        """
        Resolve the active exam session_id.
        """
        if config.SESSION_ID:
            self._session_id = config.SESSION_ID
            logger.info("Using configured session_id: %s", self._session_id)
            return True

        url = f"{config.BACKEND_URL}/sessions/?skip=0&limit=100"
        try:
            resp = self._session.get(url, timeout=config.REQUEST_TIMEOUT)
            if resp.status_code == 200:
                sessions = resp.json()
                active = [s for s in sessions if s.get("status") == "active"]
                chosen = active[-1] if active else (sessions[-1] if sessions else None)
                if chosen:
                    self._session_id = str(chosen["id"])
                    logger.info("Resolved session_id: %s", self._session_id)
                    return True
            logger.warning("No sessions found on backend.")
        except requests.RequestException as exc:
            logger.error("resolve_session_id error: %s", exc)
        return False

    # ── Upload Screenshot ────────────────────────────────────────────

    def upload_screenshot(self, filepath: str) -> Optional[str]:
        """
        Uploads a screenshot file. Returns the remote filename or None.
        """
        if not os.path.exists(filepath):
            return None

        url = f"{config.BACKEND_URL}/computers/upload-screenshot/{config.COMPUTER_ID}"
        # We need to temporarily remove JSON Content-Type headers for multipart upload
        headers = {"Authorization": f"Bearer {self._token}"} if self._token else {}

        try:
            with open(filepath, "rb") as f:
                files = {"file": (os.path.basename(filepath), f, "image/jpeg")}
                resp = requests.post(url, files=files, headers=headers, timeout=config.REQUEST_TIMEOUT * 2)
                if resp.status_code in (200, 201):
                    remote_filename = resp.json().get("filename")
                    logger.info("Screenshot uploaded successfully: %s", remote_filename)
                    return remote_filename
                logger.warning("Screenshot upload failed: HTTP %s", resp.status_code)
        except Exception as exc:
            logger.warning("Failed to upload screenshot: %s", exc)
        return None

    # ── Event Posting ────────────────────────────────────────────────

    def post_computer_event(
        self,
        activity_type: str,
        confidence: float,
        active_app: Optional[str],
        active_website: Optional[str],
        cpu: float,
        ram: float,
        screenshot_path: Optional[str] = None
    ) -> bool:
        """
        POST a complete monitoring state event to /computers/event.
        """
        payload = {
            "computer_id": config.COMPUTER_ID,
            "student_name": self._student_name or "Unknown Student",
            "active_application": active_app or "None",
            "active_website": active_website or "None",
            "cpu_usage": round(cpu, 1),
            "ram_usage": round(ram, 1),
            "screenshot_path": screenshot_path,
            "activity_type": activity_type,
            "confidence": round(min(max(confidence, 0.0), 1.0), 2),
        }

        url = f"{config.BACKEND_URL}/computers/event"
        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                resp = self._session.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)
                if resp.status_code in (200, 201):
                    logger.debug("Computer event posted: %s", activity_type)
                    return True
                if resp.status_code == 401:
                    logger.warning("Token expired — re-authenticating...")
                    if self.login():
                        continue
                logger.warning("Event post failed (attempt %d): HTTP %s", attempt, resp.status_code)
            except requests.RequestException as exc:
                logger.warning("Event post error (attempt %d): %s", attempt, exc)
            if attempt < config.MAX_RETRIES:
                time.sleep(config.RETRY_BACKOFF * attempt)
        return False

    def post_activity(self, activity_type: str, confidence: float = 1.0) -> bool:
        """
        Legacy wrapper redirecting to post_computer_event with snapshot data.
        """
        # Default snapshot parameters
        from collectors.system_monitor import SystemMonitor
        snap = SystemMonitor.snapshot()
        return self.post_computer_event(
            activity_type=activity_type,
            confidence=confidence,
            active_app="Agent",
            active_website="None",
            cpu=snap.get("cpu", 0.0),
            ram=snap.get("ram", 0.0)
        )

    # ── Health ───────────────────────────────────────────────────────

    def is_backend_reachable(self) -> bool:
        """Quick health check against GET /health."""
        try:
            resp = self._session.get(f"{config.BACKEND_URL}/health", timeout=config.REQUEST_TIMEOUT)
            return resp.status_code == 200 and resp.json().get("status") == "healthy"
        except requests.RequestException:
            return False

    # ── Properties ───────────────────────────────────────────────────

    @property
    def student_id(self) -> Optional[str]:
        return self._student_id

    @property
    def student_name(self) -> Optional[str]:
        return self._student_name

    @property
    def session_id(self) -> Optional[str]:
        return self._session_id

    @property
    def is_ready(self) -> bool:
        return bool(self._token and self._student_id)
