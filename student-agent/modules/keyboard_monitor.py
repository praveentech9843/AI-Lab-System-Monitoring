import asyncio
import logging
import sys
import config
from message_builder import build_message

logger = logging.getLogger("KeyboardMonitor")

try:
    import keyboard
    keyboard_available = True
except ImportError:
    keyboard_available = False

class KeyboardMonitor:
    def __init__(self, client):
        self.client = client
        self.running = False
        self.loop = None

    def start(self):
        """Starts the keyboard hooking logic if enabled."""
        if config.KEYBOARD_ENABLED and keyboard_available:
            self.running = True
            # Keep track of the current event loop for thread-safe scheduling
            try:
                self.loop = asyncio.get_running_loop()
            except RuntimeError:
                self.loop = asyncio.get_event_loop()
            
            try:
                keyboard.hook(self.on_key_event)
            except Exception as e:
                logger.error(f"Failed to hook keyboard: {e}")

    def on_key_event(self, event):
        """Low-level OS hook callback that checks for specific system shortcuts."""
        if not self.running:
            return
        
        # Only process on key down to avoid duplicate logs on key release
        if event.event_type == keyboard.KEY_DOWN:
            # Alt+Tab detection
            if keyboard.is_pressed('alt') and event.name == 'tab':
                self.send_shortcut("Alt+Tab")
            # Ctrl+C detection
            elif keyboard.is_pressed('ctrl') and event.name == 'c':
                self.send_shortcut("Ctrl+C")
            # Ctrl+V detection
            elif keyboard.is_pressed('ctrl') and event.name == 'v':
                self.send_shortcut("Ctrl+V")
            # Windows key detection
            elif event.name in ('left windows', 'right windows', 'win'):
                self.send_shortcut("Windows")
            # Print Screen key detection
            elif event.name in ('print screen', 'prtscn', 'snapshot'):
                self.send_shortcut("PrintScreen")

    def send_shortcut(self, shortcut_name: str):
        """Thread-safely dispatches key shortcut detection payload to client."""
        if self.client.connected and self.loop:
            message = build_message(
                msg_type="keyboard",
                data={"shortcut": shortcut_name}
            )
            asyncio.run_coroutine_threadsafe(self.client.send(message), self.loop)

    def stop(self):
        """Stops the keyboard hooking logic."""
        self.running = False
        if keyboard_available:
            try:
                keyboard.unhook(self.on_key_event)
            except Exception:
                pass
