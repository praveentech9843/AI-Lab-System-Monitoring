import asyncio
import sys
from websocket_client import WebSocketClient
from startup import register_startup
from modules.heartbeat import Heartbeat
from modules.screen_stream import ScreenStream
from modules.active_window import ActiveWindow
from modules.process_monitor import ProcessMonitor
from modules.keyboard_monitor import KeyboardMonitor
from modules.clipboard_monitor import ClipboardMonitor

async def main():
    # Register to start automatically on Windows logon
    if register_startup():
        print("Successfully registered agent in Windows Startup registry.")
    else:
        print("Warning: Failed to register agent in Windows Startup registry.")
    sys.stdout.flush()

    # Create the single WebSocketClient instance
    client = WebSocketClient()

    # Instantiate modules
    heartbeat = Heartbeat(client)
    screen_stream = ScreenStream(client)
    active_window = ActiveWindow(client)
    process_monitor = ProcessMonitor(client)
    keyboard_monitor = KeyboardMonitor(client)
    clipboard_monitor = ClipboardMonitor(client)

    # Launch websocket client connection loop as background task
    client_task = asyncio.create_task(client.connect())

    # Wait briefly for connection setup
    await asyncio.sleep(1.0)

    # Start all monitor modules
    heartbeat.start()
    screen_stream.start()
    active_window.start()
    process_monitor.start()
    
    # Pass running event loop to keyboard monitor for thread-safe dispatches
    keyboard_monitor.loop = asyncio.get_running_loop()
    keyboard_monitor.start()
    
    clipboard_monitor.start()

    print("Student Agent fully started and monitoring active.")
    sys.stdout.flush()

    try:
        # Run indefinitely until connection task is canceled or client halts
        await client_task
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("\nStopping Agent...")
        sys.stdout.flush()
    finally:
        # Stop all monitoring tasks cleanly
        heartbeat.stop()
        screen_stream.stop()
        active_window.stop()
        process_monitor.stop()
        keyboard_monitor.stop()
        clipboard_monitor.stop()
        
        await client.stop()
        print("Agent stopped cleanly.")
        sys.stdout.flush()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
