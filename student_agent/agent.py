"""
AI Lab System Monitoring — Student Agent
========================================
Runs silently in the background on each lab workstation.
Collects system events and forwards them to the backend API.
Listens to real-time administrative lock/capture commands from the console.
"""

import logging
import signal
import sys
import threading
import time
import os
import json
from datetime import datetime, timezone
from typing import Callable, Optional

# Try importing websocket-client safely
try:
    import websocket
except ImportError:
    websocket = None

# ── Logging Setup ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("agent.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("agent")

# ── Local imports ──────────────────────────────────────────────────
import config
from core.api_client  import APIClient
from core.event_queue import EventQueue
from collectors.system_monitor   import SystemMonitor
from collectors.app_monitor      import AppMonitor
from collectors.browser_monitor  import BrowserMonitor
from collectors.usb_monitor      import USBMonitor
from collectors.clipboard_monitor import ClipboardMonitor
from collectors.screenshot       import ScreenshotCollector


# ──────────────────────────────────────────────────────────────────
# Dispatcher
# ──────────────────────────────────────────────────────────────────

class EventDispatcher:
    """
    Routes collected events to the backend or the offline queue.
    Integrates system metrics, active app/website, and screenshot uploads.
    """

    def __init__(
        self,
        client: APIClient,
        queue: EventQueue,
        system_mon: SystemMonitor,
        app_mon: AppMonitor,
        browser_mon: BrowserMonitor
    ) -> None:
        self._client = client
        self._queue  = queue
        self._system_mon = system_mon
        self._app_mon = app_mon
        self._browser_mon = browser_mon
        self._online = True

    def dispatch(self, events: list) -> None:
        """Send events to the backend, queuing on failure."""
        for event in events:
            activity_type = event.get("activity_type", "unknown")
            confidence    = event.get("confidence", 1.0)

            # Determine if this is a screenshot event and upload first
            screenshot_path = None
            if "screenshot_taken" in activity_type:
                filename = None
                for part in activity_type.split(":"):
                    if part.startswith("file="):
                        filename = part.split("=")[1]
                if filename:
                    filepath = os.path.join("screenshots", filename)
                    if self._client.is_ready and self._online:
                        screenshot_path = self._client.upload_screenshot(filepath)

            # Get current system metrics and states
            snap = self._system_mon.snapshot()
            cpu = snap.get("cpu", 0.0)
            ram = snap.get("ram", 0.0)
            active_app = self._app_mon.current_app
            active_web = self._browser_mon.current_domain

            if self._client.is_ready and self._online:
                ok = self._client.post_computer_event(
                    activity_type=activity_type,
                    confidence=confidence,
                    active_app=active_app,
                    active_website=active_web,
                    cpu=cpu,
                    ram=ram,
                    screenshot_path=screenshot_path
                )
                if not ok:
                    self._online = False
                    logger.warning("Backend unreachable — switching to offline queue.")
                    self._queue.enqueue(activity_type, confidence)
            else:
                self._queue.enqueue(activity_type, confidence)

    def attempt_flush(self) -> None:
        """
        Try to reconnect and flush the offline queue.
        """
        if self._queue.size() == 0 and self._online:
            return

        reachable = self._client.is_backend_reachable()
        if not reachable:
            logger.debug("Backend still unreachable. Queue size: %d", self._queue.size())
            return

        if not self._online:
            logger.info("Backend reachable — reconnected. Flushing offline queue...")
            if not self._client.is_ready:
                if not self._client.login():
                    return
                self._client.resolve_student_id()
                self._client.resolve_session_id()
            self._online = True

        sent = self._queue.flush(self._client)
        if sent:
            logger.info("Flushed %d events. Remaining: %d", sent, self._queue.size())


# ──────────────────────────────────────────────────────────────────
# Admin WebSocket Command Listener
# ──────────────────────────────────────────────────────────────────

class CommandListener(threading.Thread):
    """
    Subscribes to live WebSocket command events.
    Executes lock, force-logout, and instant screenshot commands.
    """

    def __init__(self, agent) -> None:
        super().__init__(name="worker-cmd-listener", daemon=True)
        self._agent  = agent
        self._running = True

    def run(self) -> None:
        if not websocket:
            logger.warning("websocket-client not installed. Commands listener disabled.")
            return

        ws_url = config.BACKEND_URL.replace("http://", "ws://") + "/ws/live"
        logger.info("Connecting commands listener to %s...", ws_url)

        while self._running:
            try:
                ws = websocket.WebSocketApp(
                    ws_url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                ws.run_forever()
            except Exception as exc:
                logger.debug("Command listener reconnect error: %s", exc)
            time.sleep(5)

    def on_message(self, ws, message: str) -> None:
        try:
            payload = json.loads(message)
            if payload.get("event") == "COMMAND_TRIGGERED":
                cmd_data = payload.get("data", {})
                if cmd_data.get("computer_id") == config.COMPUTER_ID:
                    command = cmd_data.get("command", "").lower()
                    logger.info("Admin Action received: %s", command.upper())
                    self.execute_command(command)
        except Exception as exc:
            logger.error("Command parse error: %s", exc)

    def on_error(self, ws, error) -> None:
        logger.debug("Commands connection error: %s", error)

    def on_close(self, ws, code, msg) -> None:
        logger.debug("Commands stream closed: %s | %s", code, msg)

    def execute_command(self, command: str) -> None:
        if command == "lock":
            logger.warning("EXEC: LOCK WORKSTATION triggered.")
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.user32.LockWorkStation()
            else:
                logger.info("Lock command simulated (Windows only).")
        elif command == "unlock":
            logger.info("EXEC: UNLOCK simulated.")
        elif command == "logout":
            logger.warning("EXEC: FORCE LOGOUT triggered. Exiting agent.")
            self._agent.stop()
        elif command == "screenshot":
            logger.info("EXEC: CAPTURE SCREENSHOT triggered.")
            # Trigger instant screenshot capture worker
            events = self._agent._screenshot.collect()
            if events:
                self._agent._dispatcher.dispatch(events)


# ──────────────────────────────────────────────────────────────────
# Scheduled Collector Worker
# ──────────────────────────────────────────────────────────────────

class CollectorWorker(threading.Thread):
    """
    Runs a single collector on a repeating interval in a daemon thread.
    """

    def __init__(
        self,
        name: str,
        collector_fn: Callable[[], list],
        interval: float,
        dispatcher: EventDispatcher,
    ) -> None:
        super().__init__(name=f"worker-{name}", daemon=True)
        self._collector_fn = collector_fn
        self._interval     = interval
        self._dispatcher   = dispatcher
        self._stop_event   = threading.Event()

    def run(self) -> None:
        logger.debug("Worker started: %s (interval=%.1fs)", self.name, self._interval)
        while not self._stop_event.is_set():
            try:
                events = self._collector_fn()
                if events:
                    self._dispatcher.dispatch(events)
            except Exception as exc:
                logger.error("Worker %s error: %s", self.name, exc, exc_info=True)
            self._stop_event.wait(self._interval)

    def stop(self) -> None:
        self._stop_event.set()


# ──────────────────────────────────────────────────────────────────
# Main Agent
# ──────────────────────────────────────────────────────────────────

class MonitoringAgent:
    """
    Orchestrates all collectors, the API client, and the event queue.
    """

    FLUSH_INTERVAL    = 15
    RECONNECT_RETRIES = 5
    RECONNECT_DELAY   = 10

    def __init__(self) -> None:
        self._client     = APIClient()
        self._queue      = EventQueue()
        self._workers:   list[CollectorWorker] = []
        self._running    = False

        # Collectors
        self._system_mon    = SystemMonitor()
        self._app_mon       = AppMonitor()
        self._browser_mon   = BrowserMonitor()
        self._usb_mon       = USBMonitor()
        self._clipboard_mon = ClipboardMonitor()
        self._screenshot    = ScreenshotCollector()

        # Dispatcher with access to collector states
        self._dispatcher = EventDispatcher(
            self._client,
            self._queue,
            self._system_mon,
            self._app_mon,
            self._browser_mon
        )

        # Real-time Command listener
        self._cmd_listener = CommandListener(self)

    def start(self) -> None:
        logger.info("=" * 60)
        logger.info("AI Lab Monitoring Agent — %s", config.COMPUTER_ID)
        logger.info("Backend: %s", config.BACKEND_URL)
        logger.info("=" * 60)

        if not self._authenticate():
            logger.critical("Authentication failed. Check config.py credentials.")
            sys.exit(1)

        self._register_signal_handlers()
        self._start_collectors()
        self._start_flush_thread()
        
        # Start command listener
        self._cmd_listener.start()

        self._running = True
        logger.info("Agent running. Press Ctrl+C to stop.")

        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def _authenticate(self) -> bool:
        """Login and resolve identifiers with retry."""
        for attempt in range(1, self.RECONNECT_RETRIES + 1):
            logger.info("Authentication attempt %d/%d...", attempt, self.RECONNECT_RETRIES)
            if self._client.login():
                if self._client.resolve_student_id() and self._client.resolve_session_id():
                    logger.info(
                        "Ready. student_id=%s (%s) | session_id=%s",
                        self._client.student_id,
                        self._client.student_name,
                        self._client.session_id,
                    )
                    return True
                logger.warning("login OK but could not resolve student/session IDs.")
            time.sleep(self.RECONNECT_DELAY)
        return False

    def _start_collectors(self) -> None:
        """Start worker threads."""
        workers_config = [
            ("system",    self._system_mon.collect,    config.POLL_SYSTEM_INTERVAL),
            ("app",       self._app_mon.collect,        config.POLL_APP_INTERVAL),
            ("browser",   self._browser_mon.collect,    config.POLL_BROWSER_INTERVAL),
            ("usb",       self._usb_mon.collect,        config.POLL_USB_INTERVAL),
            ("clipboard", self._clipboard_mon.collect,  config.POLL_CLIPBOARD_INTERVAL),
            ("screenshot",self._screenshot.collect,     config.SCREENSHOT_INTERVAL),
        ]

        for name, fn, interval in workers_config:
            worker = CollectorWorker(name, fn, interval, self._dispatcher)
            worker.start()
            self._workers.append(worker)
            logger.info("  ✓ %-12s collector started (every %.0fs)", name, interval)

    def _start_flush_thread(self) -> None:
        def flush_loop():
            while self._running:
                try:
                    self._dispatcher.attempt_flush()
                except Exception as exc:
                    logger.debug("Flush loop error: %s", exc)
                time.sleep(self.FLUSH_INTERVAL)

        t = threading.Thread(target=flush_loop, name="flush-loop", daemon=True)
        t.start()

    def _register_signal_handlers(self) -> None:
        signal.signal(signal.SIGINT,  lambda *_: self.stop())
        signal.signal(signal.SIGTERM, lambda *_: self.stop())

    def stop(self) -> None:
        logger.info("Shutting down agent...")
        self._running = False
        
        # Stop command listener loop
        self._cmd_listener._running = False
        
        for worker in self._workers:
            worker.stop()
        remaining = self._queue.size()
        if remaining:
            logger.info("Flushing %d queued events before exit...", remaining)
            self._dispatcher.attempt_flush()
        self._queue.close()
        logger.info("Agent stopped cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    MonitoringAgent().start()
