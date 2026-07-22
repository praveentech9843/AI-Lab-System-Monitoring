"""
Main entrypoint for the AI Lab System Monitoring FastAPI backend application.
Provides the primary application instance and health check endpoint.
"""
from fastapi import FastAPI
from config import settings

app = FastAPI(
    title=settings.PROJECT_TITLE,
    version=settings.PROJECT_VERSION,
    description="Centralized real-time student desktop monitoring and AI anomaly detection backend system."
)


@app.get(
    "/",
    tags=["Health"],
    response_description="Return health status message"
)
async def health_check():
    """
    Root health check endpoint to verify backend operational status.
    """
    return {
        "message": "AI Lab Monitoring Backend Running"
    }
