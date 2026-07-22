"""
Screenshot Collector — Captures periodic screenshots and optionally
uploads them or stores them locally for proctoring review.

Currently stores screenshots locally as JPEG files.
Each file is named: <COMPUTER_ID>_<ISO_timestamp>.jpg
"""
import io
import logging
import os
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger("agent.screenshot")

SCREENSHOTS_DIR = Path("screenshots")


def _capture_screenshot() -> Optional[bytes]:
    """Capture a full-screen screenshot and return JPEG bytes."""
    try:
        import pyautogui
        from PIL import Image

        img = pyautogui.screenshot()

        # Resize if larger than configured max width
        if img.width > config.SCREENSHOT_MAX_WIDTH:
            ratio  = config.SCREENSHOT_MAX_WIDTH / img.width
            height = int(img.height * ratio)
            img    = img.resize((config.SCREENSHOT_MAX_WIDTH, height), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=config.SCREENSHOT_QUALITY)
        return buf.getvalue()

    except ImportError:
        logger.debug("pyautogui or Pillow not installed — screenshots disabled.")
    except Exception as exc:
        logger.warning("Screenshot capture failed: %s", exc)
    return None


class ScreenshotCollector:
    """
    Captures periodic screenshots and saves them locally.
    Emits a screenshot_taken activity event on success.
    """

    def __init__(self) -> None:
        if config.SCREENSHOT_ENABLED:
            SCREENSHOTS_DIR.mkdir(exist_ok=True)
            logger.info("Screenshots will be saved to: %s", SCREENSHOTS_DIR.resolve())

    def collect(self) -> list:
        """Capture screenshot, save to disk, return activity event."""
        if not config.SCREENSHOT_ENABLED:
            return []

        data = _capture_screenshot()
        if not data:
            return []

        # Save locally
        ts   = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        name = f"{config.COMPUTER_ID}_{ts}.jpg"
        path = SCREENSHOTS_DIR / name
        try:
            path.write_bytes(data)
            logger.debug("Screenshot saved: %s (%d KB)", name, len(data) // 1024)
        except OSError as exc:
            logger.warning("Could not save screenshot: %s", exc)

        return [{
            "activity_type": f"screenshot_taken:file={name}:size={len(data)}",
            "confidence": 1.0,
        }]
