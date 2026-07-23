"""
Browser Monitor Module.
Detects the active browser window URL by reading the address bar via Windows Accessibility API (UI Automation).
Falls back to window title parsing for browsers that block automation access.
"""
import asyncio
import re
import sys
import config
from message_builder import build_message

# Browser process names and their title-to-domain parsing patterns
BROWSER_PROCESSES = {
    "chrome.exe", "msedge.exe", "firefox.exe", "opera.exe",
    "brave.exe", "vivaldi.exe", "chromium.exe"
}# Blocked domain keywords to extract from browser window titles (mutable list)
BLOCKED_DOMAINS = [
    "youtube.com",
    "chatgpt.com",
    "deepseek.com",
    "gemini.google.com",
    "reddit.com",
    "facebook.com",
    "instagram.com",
    "tiktok.com",
    "twitter.com",
    "x.com",
    "whatsapp.com",
    "telegram.org",
]

def update_blocked_domains(domains: list):
    """Updates the blocked domains list in-place."""
    BLOCKED_DOMAINS.clear()
    BLOCKED_DOMAINS.extend(domains)
    print(f"[BrowserMonitor] Updated blocked domains list to: {BLOCKED_DOMAINS}")
    sys.stdout.flush()

if sys.platform == "win32":
    try:
        import win32gui
        import win32process
        import psutil
        win32_available = True
    except ImportError:
        win32_available = False
else:
    win32_available = False


def extract_domain_from_title(title: str, exe: str) -> str | None:
    """
    Extracts a domain from a browser window title.
    Browser window titles are formatted like:
      "YouTube - Google Chrome"
      "ChatGPT - Mozilla Firefox"
      "reddit.com/r/python - Brave"
    Returns the matched blocked domain if found, else None.
    """
    if not title or not exe:
        return None

    exe_lower = exe.lower()
    if exe_lower not in BROWSER_PROCESSES:
        return None

    title_lower = title.lower()

    # Direct domain match in title
    for domain in BLOCKED_DOMAINS:
        if domain in title_lower:
            return domain

    # Dynamic site name to domain mapping derived from domains
    name_map = {}
    for domain in BLOCKED_DOMAINS:
        parts = domain.split('.')
        if parts:
            kw = parts[0]
            if kw and len(kw) > 3:
                name_map[kw] = domain

    for name, domain in name_map.items():
        if name in title_lower:
            return domain

    return None
def try_get_browser_url_uia(hwnd: int) -> str | None:
    """
    Attempts to read the actual URL from a browser's address bar
    using Windows UI Automation (comtypes). Falls back gracefully.
    """
    try:
        import comtypes.client
        import comtypes.gen.UIAutomationClient as UIA

        uia = comtypes.client.CreateObject(
            "{ff48dba4-60ef-4201-aa87-54103eef594e}",
            interface=UIA.IUIAutomation
        )
        element = uia.ElementFromHandle(hwnd)
        # Look for Edit control (address bar) with ControlType 50004
        condition = uia.CreatePropertyCondition(
            UIA.UIA_ControlTypePropertyId, UIA.UIA_EditControlTypeId
        )
        edit = element.FindFirst(UIA.TreeScope_Descendants, condition)
        if edit:
            val_pattern = edit.GetCurrentPattern(UIA.UIA_ValuePatternId)
            if val_pattern:
                val = val_pattern.QueryInterface(UIA.IUIAutomationValuePattern)
                return val.CurrentValue
    except Exception:
        pass
    return None


class BrowserMonitor:
    def __init__(self, client):
        self.client = client
        self.running = False
        self.task = None
        self.last_url = None
        self.last_domain = None

    def start(self):
        """Starts the browser monitoring loop as a background task."""
        if win32_available:
            self.running = True
            self.task = asyncio.create_task(self.scan_loop())

    async def scan_loop(self):
        """Monitors the foreground window for browser activity and URL changes."""
        while self.running:
            if self.client.connected:
                try:
                    hwnd = win32gui.GetForegroundWindow()
                    title = win32gui.GetWindowText(hwnd)

                    if hwnd and title:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        try:
                            proc = psutil.Process(pid)
                            exe = proc.name()
                        except Exception:
                            exe = ""

                        # Try to get exact URL via UI Automation
                        url = try_get_browser_url_uia(hwnd)

                        if url:
                            # Extract domain from URL
                            domain_match = re.search(r"(?:https?://)?(?:www\.)?([^/\s?#]+)", url)
                            domain = domain_match.group(1).lower() if domain_match else None
                        else:
                            # Fall back to title-based domain extraction
                            domain = extract_domain_from_title(title, exe)

                        if domain and domain != self.last_domain:
                            self.last_domain = domain
                            message = build_message(
                                msg_type="browser",
                                data={
                                    "url": url or f"https://{domain}",
                                    "domain": domain,
                                    "title": title,
                                    "executable": exe,
                                }
                            )
                            await self.client.send(message)

                except Exception:
                    pass

            await asyncio.sleep(config.WINDOW_SCAN_INTERVAL)

    def stop(self):
        """Stops the browser monitor loop."""
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
