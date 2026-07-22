# 🖥️ AI Lab System Monitoring - Backend Service

Production-ready FastAPI backend scaffold for the AI Lab System Monitoring platform.

---

## 📌 Project Purpose
The backend serves as the core orchestration service for the AI Lab System Monitoring platform. It handles:
- Real-time desktop frame streaming via WebSockets from student workstations.
- AI anomaly detection and behavior risk evaluation.
- Faculty dashboard notifications and auto-fullscreen visual alerts.
- Data persistence for lab supervision history and alert logs.

---

## 🏛️ Project Architecture Diagram

```text
+------------------------+             +------------------------+
|   Student Workstation  |             |    Faculty Dashboard   |
|     (Windows Agent)    |             |     (React Frontend)   |
+-----------+------------+             +-----------^------------+
            |                                      |
            | WebSocket Frame Stream               | WebSocket Alerts
            v                                      | & REST APIs
+-----------+--------------------------------------+------------+
|                        FASTAPI BACKEND                        |
|                                                               |
|  [main.py]  ---> [api/]         REST Endpoints                |
|             ---> [websocket/]   Streaming Manager             |
|             ---> [risk_engine/] AI Anomaly Detector           |
|             ---> [database/]    Persistence Layer             |
|             ---> [auth/]        JWT Security                  |
+---------------------------------------------------------------+
```

---

## 📁 Folder Structure & Module Explanation

```text
backend/
├── main.py            # FastAPI application entrypoint & root health check
├── config.py          # Environment configuration loader
├── requirements.txt   # Core Python dependencies
├── .env.example       # Sample environment configuration template
├── .gitignore          # Version control ignore configuration
├── api/               # REST API endpoints & request/response schemas
├── websocket/         # WebSocket connection hub & streaming managers
├── database/          # Database configuration, sessions & ORM models
├── auth/              # Authentication & JWT security modules
├── risk_engine/       # AI anomaly detection & risk scoring handlers
├── reports/           # Analytics & report generation modules
├── utils/             # Common helper utilities
└── README.md          # Backend documentation
```

### Module Breakdown
- **`main.py`**: Initializes the FastAPI application instance, configures settings, and defines the root health check route.
- **`config.py`**: Loads environment variables using `python-dotenv` and exposes typed application settings.
- **`api/`**: Reserved for versioned REST API routers (endpoints for student stations, alerts, and settings).
- **`websocket/`**: Reserved for handling real-time frame streaming and pub/sub event broadcasting.
- **`database/`**: Reserved for database connections, sessions, Alembic migrations, and ORM models.
- **`auth/`**: Reserved for JWT authentication, password hashing, and role-based access control.
- **`risk_engine/`**: Reserved for desktop stream analysis, YOLO object detection invocation, and risk scoring.
- **`reports/`**: Reserved for generating session summary reports and anomaly logs.
- **`utils/`**: Reserved for shared formatting functions, logging configuration, and generic helper utilities.

---

## 🔗 API Endpoints

| Method | Endpoint | Tag | Description | Response Example |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | `Health` | Root health check to verify backend status | `{"message": "AI Lab Monitoring Backend Running"}` |

---

## 🚀 How to Run

### 1. Create and Activate Virtual Environment
```bash
cd backend
python -m venv venv
```

On Windows (PowerShell):
```powershell
.\venv\Scripts\activate
```

On Linux / macOS:
```bash
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4. Start Development Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Verify Server Health
Open browser or run:
```bash
curl http://localhost:8000/
```

Expected Response:
```json
{
  "message": "AI Lab Monitoring Backend Running"
}
```

Interactive OpenAPI Documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🔮 Future Roadmap (Upcoming Milestones)
- **Milestone 2**: WebSocket streaming hub implementation for agent & client frame multiplexing.
- **Milestone 3**: Database integration (SQLite/SQLAlchemy) for alert persistence and student records.
- **Milestone 4**: Risk Engine (YOLOv8 object detection & rule engine for phone/behavior alerts).
- **Milestone 5**: JWT authentication & faculty session management.
