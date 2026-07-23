import asyncio
import re
import sys
import config
from message_builder import build_message

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

# Browser executables that can have website URLs in their titles
BROWSER_PROCESSES = {
    "chrome.exe", "msedge.exe", "firefox.exe", "opera.exe",
    "brave.exe", "vivaldi.exe", "chromium.exe"
}

# Blocked sites to detect in window titles
BLOCKED_DOMAINS = [
    "youtube.com", "chatgpt.com", "deepseek.com", "gemini.google.com",
    "reddit.com", "facebook.com", "instagram.com", "tiktok.com",
    "twitter.com", "x.com", "whatsapp.com", "telegram.org",
]

def update_blocked_domains(domains: list):
    """Updates the blocked domains list in-place."""
    BLOCKED_DOMAINS.clear()
    BLOCKED_DOMAINS.extend(domains)
    print(f"[ActiveWindow] Updated blocked domains list to: {BLOCKED_DOMAINS}")
    sys.stdout.flush()


def extract_domain_from_title(title: str, exe: str) -> str | None:
    """Extract a domain from a browser window title string."""
    if not title or not exe:
        return None
    if exe.lower() not in BROWSER_PROCESSES:
        return None
    title_lower = title.lower()
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

    for keyword, domain in name_map.items():
        if keyword in title_lower:
            return domain
    return None


class ActiveWindow:
    def __init__(self, client):
        self.client = client
        self.running = False
        self.task = None
        self.last_window_info = None
        self.tick_counter = 0

    def start(self):
        """Starts the active window detection scan loop as a background task."""
        self.running = True
        self.task = asyncio.create_task(self.scan_loop())

    async def scan_loop(self):
        """Asynchronously monitors for foreground active window changes and sends periodic state updates."""
        while self.running:
            if self.client.connected:
                try:
                    self.tick_counter += 1
                    current_info = None

                    if win32_available:
                        hwnd = win32gui.GetForegroundWindow()
                        title = win32gui.GetWindowText(hwnd)

                        if hwnd and title:
                            try:
                                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                                proc = psutil.Process(pid)
                                executable = proc.name()
                            except Exception:
                                executable = "explorer.exe"

                            detected_domain = extract_domain_from_title(title, executable)

                            current_info = {
                                "title": title,
                                "executable": executable,
                                "pid": pid if 'pid' in locals() else 0,
                                "domain": detected_domain,
                            }
                    else:
                        # Fallback for non-windows / virtual environment
                        current_info = {
                            "title": "Visual Studio Code - AI Project",
                            "executable": "Code.exe",
                            "pid": 1234,
                            "domain": None,
                        }

                    if current_info:
                        # Send if window changed OR every 3rd scan loop (~3 seconds) to ensure state sync
                        should_send = (current_info != self.last_window_info) or (self.tick_counter % 3 == 0)

                        if should_send:
                            self.last_window_info = current_info

                            # Send window event
                            message = build_message(msg_type="window", data=current_info)
                            await self.client.send(message)

                            # If a domain was detected (blocked or normal), also send browser event
                            detected_domain = current_info.get("domain")
                            if detected_domain:
                                browser_msg = build_message(
                                    msg_type="browser",
                                    data={
                                        "url": f"https://{detected_domain}",
                                        "domain": detected_domain,
                                        "title": current_info.get("title", ""),
                                        "executable": current_info.get("executable", ""),
                                    }
                                )
                                await self.client.send(browser_msg)

                except Exception:
                    pass
            await asyncio.sleep(config.WINDOW_SCAN_INTERVAL)

    def stop(self):
        """Stops the active window scan loop."""
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
