from fastapi import FastAPI, WebSocket
import uvicorn
import json

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ System Connected!")

    while True:
        try:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "window":
                print(f"Active Window: {message['data'].get('title')}")
            elif message["type"] == "screen":
                print("📺 Screen frame received")
            else:
                print(f"Received: {message['type']}")

        except Exception as e:
            print("Disconnected:", e)
            break

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)