"""
Application Configuration Module.
Loads environment variables and exposes typed settings for the FastAPI application.
"""
import os

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Settings:
    """
    Application Settings class.

    Retrieves configuration values from environment variables with sensible defaults.
    Houses application metadata, network parameters, database connection strings, and JWT settings.
    """

    # Project Metadata
    PROJECT_TITLE: str = os.getenv("PROJECT_TITLE", "AI Lab System Monitoring")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Server Network Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Database Connection Settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/ai_lab_monitoring"
    )

    # JWT Authentication Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_jwt_key_change_in_production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))


# Global instantiated settings object for application-wide use
settings = Settings()
