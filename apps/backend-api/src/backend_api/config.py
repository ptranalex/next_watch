"""
Configuration module for the backend API.
"""

import os
from typing import Optional


class Settings:
    """
    Application settings loaded from environment variables
    with reasonable defaults for development.
    """

    ***REMOVED*** Default to PostgreSQL configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/next_watch"
    )
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


***REMOVED*** Create a singleton instance to be imported elsewhere
settings = Settings()
