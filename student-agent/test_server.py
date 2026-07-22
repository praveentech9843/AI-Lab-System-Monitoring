from fastapi import FastAPI, WebSocket
import uvicorn
import json

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[OK] System Connected!", flush=True)

    while True:
        try:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "window":
                print(f"Active Window: {message['data'].get('title')}", flush=True)
            elif message["type"] == "screen":
                print("Screen frame received", flush=True)
            else:
                print(f"Received: {message['type']}", flush=True)

        except Exception as e:
            print("Disconnected:", e, flush=True)
            break

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)