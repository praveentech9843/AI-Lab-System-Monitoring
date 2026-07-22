"""
Browser Monitor — Extracts the active domain/tab from browser window titles.
Supports Chrome, Firefox, Edge, Opera, Brave.

Strategy:
  Browser window titles follow predictable patterns:
    Chrome:  "<Page Title> - Google Chrome"
    Firefox: "<Page Title> — Mozilla Firefox"
    Edge:    "<Page Title> - Microsoft​ Edge"

  We extract the page title, then attempt to parse a domain from it.
  If the page title itself looks like a URL, we extract directly.
  Otherwise we check if any known blocked domain appears in the title.
"""
import logging
import platform
import re
from typing import Optional, Tuple
from urllib.parse import urlparse

import config

logger = logging.getLogger("agent.browser_monitor")


# ── Window title retrieval (shared with app_monitor) ───────────────

def _get_active_window_title() -> Optional[str]:
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


# ── Browser patterns ───────────────────────────────────────────────

_BROWSER_PATTERNS = [
    # (browser_name, regex to strip suffix from title)
    ("Chrome",  re.compile(r"\s[-–]\s*Google Chrome\s*$", re.IGNORECASE)),
    ("Chrome",  re.compile(r"\s[-–]\s*Chromium\s*$", re.IGNORECASE)),
    ("Firefox", re.compile(r"\s[—-]\s*Mozilla Firefox\s*$", re.IGNORECASE)),
    ("Edge",    re.compile(r"\s[-–]\s*Microsoft[\u200b\s]*Edge\s*$", re.IGNORECASE)),
    ("Opera",   re.compile(r"\s[-–]\s*Opera\s*$", re.IGNORECASE)),
    ("Brave",   re.compile(r"\s[-–]\s*Brave\s*$", re.IGNORECASE)),
]

_DOMAIN_FROM_TITLE = re.compile(
    r"(?:https?://)?(?:www\.)?([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z]{2,})+)"
)


def _parse_browser_and_domain(title: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (browser_name, domain) from a window title.
    Returns (None, None) if the title is not from a known browser.
    """
    for browser_name, pattern in _BROWSER_PATTERNS:
        if pattern.search(title):
            page_title = pattern.sub("", title).strip()
            domain = _extract_domain(page_title)
            return browser_name, domain
    return None, None


def _extract_domain(page_title: str) -> Optional[str]:
    """
    Try to extract a domain/hostname from a page title.
    Checks blocked domains explicitly for maximum detection rate.
    """
    # Direct URL match in title
    match = _DOMAIN_FROM_TITLE.search(page_title)
    if match:
        return match.group(1).lower()

    # Check if any blocked domain keyword appears in the title
    title_lower = page_title.lower()
    for domain in config.BLOCKED_DOMAINS:
        # Strip TLD for fuzzy matching (e.g., "chatgpt" from "chatgpt.com")
        keyword = domain.split(".")[0]
        if keyword and keyword in title_lower:
            return domain

    return None


class BrowserMonitor:
    """
    Monitors browser tab switches and detects blocked website visits.
    Emits events on tab changes and blocked domain access.
    """

    def __init__(self) -> None:
        self._prev_browser: Optional[str] = None
        self._prev_domain:  Optional[str] = None
        self._prev_title:   Optional[str] = None

    def collect(self) -> list:
        """Return events if browser tab changed or blocked site detected."""
        title = _get_active_window_title()
        if not title or title == self._prev_title:
            return []

        browser, domain = _parse_browser_and_domain(title)
        if not browser:
            return []

        events = []
        self._prev_title = title

        # Tab switch detection
        if domain != self._prev_domain or browser != self._prev_browser:
            domain_label = domain or "unknown"
            events.append({
                "activity_type": f"tab_switch:browser={browser}:domain={domain_label}",
                "confidence": 0.92,
            })
            logger.debug("Tab switch: %s → %s on %s", self._prev_domain, domain_label, browser)

            # Blocked website detection
            if domain and self._is_blocked(domain):
                events.append({
                    "activity_type": f"blocked_website:domain={domain}:browser={browser}",
                    "confidence": 0.97,
                })
                logger.warning("BLOCKED WEBSITE DETECTED: %s on %s", domain, browser)

            self._prev_browser = browser
            self._prev_domain  = domain

        return events

    @staticmethod
    def _is_blocked(domain: str) -> bool:
        domain_lower = domain.lower()
        return any(
            blocked in domain_lower or domain_lower in blocked
            for blocked in config.BLOCKED_DOMAINS
        )

    @property
    def current_domain(self) -> Optional[str]:
        return self._prev_domain

    @property
    def current_browser(self) -> Optional[str]:
        return self._prev_browser
