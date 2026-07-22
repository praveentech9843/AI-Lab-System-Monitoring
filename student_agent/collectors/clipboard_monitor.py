"""
Clipboard Monitor — Detects copy/paste events by polling the system clipboard.
Emits an event when clipboard content changes (indicates Ctrl+C was used).
"""
import hashlib
import logging
import platform
from typing import Optional

logger = logging.getLogger("agent.clipboard_monitor")


def _get_clipboard_text() -> Optional[str]:
    """Return current clipboard text, or None if unavailable."""
    system = platform.system()
    try:
        if system == "Windows":
            import ctypes
            import ctypes.wintypes

            CF_UNICODETEXT = 13
            if not ctypes.windll.user32.OpenClipboard(None):
                return None
            try:
                handle = ctypes.windll.user32.GetClipboardData(CF_UNICODETEXT)
                if not handle:
                    return None
                ptr = ctypes.windll.kernel32.GlobalLock(handle)
                if not ptr:
                    return None
                try:
                    text = ctypes.wstring_at(ptr)
                    return text
                finally:
                    ctypes.windll.kernel32.GlobalUnlock(handle)
            finally:
                ctypes.windll.user32.CloseClipboard()

        elif system == "Darwin":
            import subprocess
            result = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=1)
            return result.stdout or None

        elif system == "Linux":
            import subprocess
            result = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True, text=True, timeout=1,
            )
            return result.stdout or None

    except Exception as exc:
        logger.debug("Clipboard read error: %s", exc)
    return None


def _hash(text: str) -> str:
    """Return MD5 hash of clipboard text for change detection."""
    return hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()


class ClipboardMonitor:
    """
    Detects copy/paste activity by polling clipboard content.
    Only emits an event when the clipboard hash changes and content
    is non-trivial (> 5 characters), to avoid noise.
    """

    MIN_CONTENT_LENGTH = 5    # Ignore trivial clipboard changes
    MAX_LOG_LENGTH     = 80   # Max chars logged (privacy)

    def __init__(self) -> None:
        initial = _get_clipboard_text()
        self._last_hash: Optional[str] = _hash(initial) if initial else None

    def collect(self) -> list:
        """Return a copy_paste event if clipboard content changed."""
        text = _get_clipboard_text()
        if not text or len(text.strip()) < self.MIN_CONTENT_LENGTH:
            return []

        current_hash = _hash(text)
        if current_hash == self._last_hash:
            return []

        self._last_hash = current_hash
        preview = text.strip().replace("\n", " ")[:self.MAX_LOG_LENGTH]
        logger.debug("Clipboard change detected (len=%d): %s…", len(text), preview)

        return [{
            "activity_type": f"copy_paste:length={len(text)}",
            "confidence": 0.88,
        }]
