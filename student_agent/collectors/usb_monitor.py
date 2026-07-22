"""
USB Monitor — Detects USB mass storage device connect/disconnect events.
Uses psutil disk partitions as a cross-platform proxy for USB drives.
On Windows, optionally uses WMI for richer event data.
"""
import logging
import platform
from typing import Set

import psutil

logger = logging.getLogger("agent.usb_monitor")


def _get_removable_drives() -> Set[str]:
    """
    Return a set of mount points for removable/USB drives.
    Uses psutil disk_partitions — opts=removable on Windows, /media/ on Linux.
    """
    drives = set()
    system = platform.system()
    try:
        for part in psutil.disk_partitions(all=False):
            opts = part.opts.lower()
            mount = part.mountpoint.lower()

            if system == "Windows":
                # On Windows, removable drives have 'removable' in opts
                if "removable" in opts:
                    drives.add(part.device)
            elif system == "Linux":
                # On Linux, removable media mounts under /media or /run/media
                if "/media/" in mount or "/run/media/" in mount:
                    drives.add(part.device)
            elif system == "Darwin":
                # On macOS, external drives mount under /Volumes
                if "/volumes/" in mount and mount != "/volumes/macintosh hd":
                    drives.add(part.device)
    except Exception as exc:
        logger.debug("Disk partitions error: %s", exc)
    return drives


class USBMonitor:
    """
    Detects USB mass storage connect/disconnect by comparing
    the set of removable drive mount points between polls.
    """

    def __init__(self) -> None:
        self._known_drives: Set[str] = _get_removable_drives()
        logger.debug("USB baseline: %s", self._known_drives)

    def collect(self) -> list:
        """Return events for newly connected or removed USB devices."""
        current = _get_removable_drives()
        events  = []

        connected    = current - self._known_drives
        disconnected = self._known_drives - current

        for device in connected:
            events.append({
                "activity_type": f"usb_connected:device={device}",
                "confidence": 1.0,
            })
            logger.warning("USB CONNECTED: %s", device)

        for device in disconnected:
            events.append({
                "activity_type": f"usb_disconnected:device={device}",
                "confidence": 1.0,
            })
            logger.info("USB disconnected: %s", device)

        self._known_drives = current
        return events
