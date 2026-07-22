"""
App Monitor — Detects the currently active foreground application.
Uses pygetwindow (Windows/macOS) with psutil process name fallback.
"""
import logging
import platform
import re
from typing import Optional, Tuple

logger = logging.getLogger("agent.app_monitor")

# ── Platform-specific active window detection ──────────────────────

def _get_active_window_title() -> Optional[str]:
    """Return the title of the currently focused window, or None."""
    system = platform.system()
    try:
        if system == "Windows":
            import ctypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return None
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            return buf.value.strip() or None

        elif system == "Darwin":
            from AppKit import NSWorkspace
            app = NSWorkspace.sharedWorkspace().activeApplication()
            return app.get("NSApplicationName")

        elif system == "Linux":
            import subprocess
            result = subprocess.run(
                ["xdotool", "getwindowfocus", "getwindowname"],
                capture_output=True, text=True, timeout=2,
            )
            return result.stdout.strip() or None

    except Exception as exc:
        logger.debug("Window title error: %s", exc)
    return None


class AppMonitor:
    """
    Monitors the active foreground application.
    Emits an event only when the application changes.
    """

    KNOWN_APPS = {
        "chrome":     "Chrome",
        "firefox":    "Firefox",
        "msedge":     "Edge",
        "opera":      "Opera",
        "brave":      "Brave",
        "code":       "VS Code",
        "pycharm":    "PyCharm",
        "jupyter":    "Jupyter",
        "notepad":    "Notepad",
        "notepad++":  "Notepad++",
        "word":       "MS Word",
        "excel":      "MS Excel",
        "powerpnt":   "PowerPoint",
        "winword":    "MS Word",
        "vlc":        "VLC",
        "zoom":       "Zoom",
        "teams":      "Teams",
        "slack":      "Slack",
        "discord":    "Discord",
        "cmd":        "Command Prompt",
        "powershell": "PowerShell",
        "terminal":   "Terminal",
    }

    def __init__(self) -> None:
        self._prev_title: Optional[str] = None
        self._prev_app:   Optional[str] = None

    def collect(self) -> list:
        """Return events if the active application changed."""
        title = _get_active_window_title()
        if not title:
            return []

        app_name = self._parse_app_name(title)

        if app_name != self._prev_app:
            events = [{
                "activity_type": f"app_switch:from={self._prev_app or 'none'}:to={app_name}",
                "confidence": 1.0,
            }]
            logger.debug("App switch: %s → %s", self._prev_app, app_name)
            self._prev_title = title
            self._prev_app   = app_name
            return events

        return []

    def _parse_app_name(self, title: str) -> str:
        """Extract a clean app name from a window title."""
        title_lower = title.lower()
        for key, label in self.KNOWN_APPS.items():
            if key in title_lower:
                return label
        # Fallback: take the last segment after " - " or " — "
        for sep in (" - ", " — ", " | "):
            parts = title.rsplit(sep, 1)
            if len(parts) == 2:
                return parts[-1].strip()[:40]
        return title[:40]

    @property
    def current_app(self) -> Optional[str]:
        return self._prev_app
