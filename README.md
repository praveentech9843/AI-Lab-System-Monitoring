# 🖥️ AI Lab System Monitoring

> **24-Hour Hackathon Prototype**

Centralized real-time desktop streaming and AI anomaly detection system for university computer laboratories.

## 📁 Project Structure

```text
AI-Lab-System-Monitoring/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entrypoint & REST routes
│   │   ├── websocket_hub.py   # Connection manager for agents & dashboard
│   │   ├── database.py        # SQLite alert log database
│   │   └── routes.py          # API route definitions
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # React UI components (GridView, StudentCard, AlertModal)
│   │   ├── hooks/             # Custom WebSocket hook (useWebSocket.js)
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── agent/
│   ├── screen_agent.py        # Screen capture & JPEG WebSocket client
│   ├── config.py              # Station configuration
│   └── requirements.txt
├── ai/
│   ├── detector.py            # OpenCV & YOLO anomaly rule checks
│   ├── model.py               # YOLO model wrapper
│   └── yolov8n.pt             # YOLO weights
└── README.md
```

## 🚀 Quick Setup

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Agent (Run on Student PC)
```bash
cd agent
pip install -r requirements.txt
python screen_agent.py
```
