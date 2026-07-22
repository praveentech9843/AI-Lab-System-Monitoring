import asyncio
import sys
from websocket_client import AgentWebSocketClient

async def main():
    print("Starting Student Agent...")
    sys.stdout.flush()
    
    # Create WebSocket Client
    client = AgentWebSocketClient()
    
    # Connect and Register (runs in background)
    client_task = asyncio.create_task(client.start())
    
    # Brief sleep to allow the connection log to print first if the server is responsive/instant
    await asyncio.sleep(0.2)
    
    print("Waiting...")
    sys.stdout.flush()
    
    try:
        # Keep running and wait for client task
        await client_task
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        await client.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAgent stopped.")
