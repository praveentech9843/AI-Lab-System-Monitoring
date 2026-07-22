import asyncio
from websocket_client import WebSocketClient

async def main():
    client = WebSocketClient()
    await client.connect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAgent stopped.")
