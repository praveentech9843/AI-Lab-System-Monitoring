import asyncio
import sys
from utils.helpers import build_message

async def heartbeat_loop(client):
    """Sends periodic heartbeat messages every 10 seconds while connected."""
    while client.connected:
        try:
            # Build and send heartbeat message
            message = build_message(type="heartbeat", data={})
            await client.send(message)
            print("Heartbeat Sent")
            sys.stdout.flush()
            
            # Wait 10 seconds before next heartbeat
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            break
        except Exception:
            break
