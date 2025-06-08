"""Main FastAPI application for the Next Watch Backend API service."""

import os
from pathlib import Path

***REMOVED*** Load environment variables
try:
    from dotenv import load_dotenv

    ***REMOVED*** Only load .env files if we're not in production
    if os.getenv("ENVIRONMENT") != "production":
        ***REMOVED*** Try multiple locations to find .env files (prioritize current directory)
        possible_paths = [
            Path.cwd() / ".env",
            Path.cwd() / ".env.local",
            Path(__file__).resolve().parents[3] / ".env",
            Path(__file__).resolve().parents[3] / ".env.local",
        ]

        for path in possible_paths:
            if path.exists():
                load_dotenv(dotenv_path=path, override=True)
                break
except ImportError:
    pass  ***REMOVED*** Continue without dotenv if not installed

***REMOVED*** Setup logging early
from backend_api.core.logging import setup_logging

setup_logging()

***REMOVED*** Import and create the app
from backend_api.core.app import create_app
from backend_api.config.app import settings

***REMOVED*** Create the FastAPI application
app = create_app()


if __name__ == "__main__":
    import uvicorn

    ***REMOVED*** Use settings for all server parameters
    uvicorn.run(
        "backend_api.main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
