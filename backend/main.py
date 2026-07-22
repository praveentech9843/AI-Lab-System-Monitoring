"""
Main entrypoint for the AI Lab System Monitoring FastAPI backend application.
Configures application lifecycle, CORS middleware, REST API routes, and WebSocket endpoints.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.activity_log import router as activity_log_router
from api.alert import router as alert_router
from api.auth import router as auth_router
from api.exam_session import router as exam_session_router
from api.faculty import router as faculty_router
from api.student import router as student_router
from config import settings
import database.models  # Ensures all SQLAlchemy models are registered with Base metadata
from database.base import Base
from database.database import engine
from websocket.routes import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application lifespan context manager.
    Creates all database tables on application startup.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_TITLE,
    version=settings.PROJECT_VERSION,
    description="Centralized real-time student desktop monitoring and AI anomaly detection backend system.",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST API Routers
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(faculty_router)
app.include_router(exam_session_router)
app.include_router(activity_log_router)
app.include_router(alert_router)

# Register WebSocket Router
app.include_router(websocket_router)


@app.get(
    "/",
    tags=["Root"],
    response_description="Return system status message"
)
async def root_endpoint():
    """
    Root endpoint verifying backend system operational status.
    """
    return {
        "message": "AI Lab System Monitoring API",
        "status": "running"
    }


@app.get(
    "/health",
    tags=["Health"],
    response_description="Return application health status"
)
async def health_check():
    """
    Health check endpoint for container probes and uptime monitoring.
    """
    return {
        "status": "healthy"
    }
