# 🖥️ AI Lab System Monitoring

> **24-Hour Hackathon Prototype**

Centralized real-time desktop streaming and AI anomaly detection system for university computer laboratories.

## 📁 Project Structure

```text
AI-Lab-System-Monitoring/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── websocket_hub.py
│   │   ├── database.py
│   │   └── routes.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── agent/
│   ├── screen_agent.py
│   ├── config.py
│   └── requirements.txt
├── ai/
│   ├── detector.py
│   ├── model.py
│   └── yolov8n.pt
└── README.md
```

## 🚀 Quick Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Agent

```bash
cd agent
pip install -r requirements.txt
python screen_agent.py
```