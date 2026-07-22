"""
System Monitor — Collects CPU usage, RAM usage, and idle time.
Uses psutil for cross-platform system metrics.
"""
import logging
import platform
import time
from typing import Optional

import psutil

import config

logger = logging.getLogger("agent.system_monitor")

# Platform-specific idle detection
_IDLE_AVAILABLE = False
_idle_lib = None

if platform.system() == "Windows":
    try:
        import ctypes
        _IDLE_AVAILABLE = True

        class _LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        def _get_idle_seconds() -> float:
            lii = _LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(_LASTINPUTINFO)
            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
            millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
            return millis / 1000.0

    except Exception:
        _IDLE_AVAILABLE = False

elif platform.system() == "Linux":
    try:
        from Xlib import display as Xdisplay
        from Xlib.ext import screensaver
        _xdisplay = Xdisplay.Display()
        _IDLE_AVAILABLE = True

        def _get_idle_seconds() -> float:
            info = screensaver.query_info(_xdisplay.screen().root)
            return info.idle / 1000.0

    except Exception:
        _IDLE_AVAILABLE = False


def _get_idle_seconds_safe() -> Optional[float]:
    """Return idle time in seconds, or None if not supported."""
    if not _IDLE_AVAILABLE:
        return None
    try:
        return _get_idle_seconds()
    except Exception as exc:
        logger.debug("Idle detection error: %s", exc)
        return None


class SystemMonitor:
    """
    Monitors CPU, RAM usage, and user idle time.
    Emits activity events when thresholds are crossed.
    """

    def __init__(self) -> None:
        self._last_idle_event_at: float = 0.0
        self._last_cpu_spike_at: float = 0.0
        # Warm up psutil (first call always returns 0.0)
        psutil.cpu_percent(interval=None)

    def collect(self) -> list:
        """
        Return a list of event dicts to be dispatched.
        Each dict has keys: activity_type, confidence.
        """
        events = []
        cpu = self._get_cpu()
        ram = self._get_ram()
        idle_secs = _get_idle_seconds_safe()

        # CPU spike detection
        if cpu >= config.CPU_SPIKE_THRESHOLD:
            now = time.time()
            if now - self._last_cpu_spike_at >= 30:  # max 1 event per 30s
                events.append({
                    "activity_type": f"cpu_spike:cpu={cpu:.0f}%:ram={ram:.0f}%",
                    "confidence": round(min(cpu / 100, 1.0), 4),
                })
                self._last_cpu_spike_at = now
                logger.debug("CPU spike event: %.1f%%", cpu)

        # Idle detection
        if idle_secs is not None and idle_secs >= config.IDLE_THRESHOLD_SECONDS:
            now = time.time()
            if now - self._last_idle_event_at >= config.IDLE_THRESHOLD_SECONDS:
                events.append({
                    "activity_type": f"idle:duration={int(idle_secs)}s",
                    "confidence": 0.95,
                })
                self._last_idle_event_at = now
                logger.debug("Idle event: %.0fs", idle_secs)

        # Heartbeat — always include system metrics for the dashboard
        events.append({
            "activity_type": f"heartbeat:cpu={cpu:.0f}%:ram={ram:.0f}%:pc={config.COMPUTER_ID}",
            "confidence": 1.0,
        })

        return events

    @staticmethod
    def _get_cpu() -> float:
        return psutil.cpu_percent(interval=0.5)

    @staticmethod
    def _get_ram() -> float:
        return psutil.virtual_memory().percent

    @staticmethod
    def snapshot() -> dict:
        """Return a point-in-time snapshot dict (non-event)."""
        return {
            "cpu": psutil.cpu_percent(interval=0.1),
            "ram": psutil.virtual_memory().percent,
            "idle_secs": _get_idle_seconds_safe(),
        }
