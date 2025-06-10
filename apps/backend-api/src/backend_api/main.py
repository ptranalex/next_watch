"""Main FastAPI application for the Next Watch Backend API service."""

import os
import logging

***REMOVED*** Import configuration after environment variables are loaded
from backend_api.config.app import settings
from backend_api.core.logging import setup_logging

***REMOVED*** Configure logging early
setup_logging(
    log_level=settings.log_level,
    verbose=settings.debug,
    quiet=False,
)

***REMOVED*** Get logger for this module
logger = logging.getLogger(__name__)

***REMOVED*** Log main application startup
logger.info("Initializing Next Watch Backend Service")
logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

***REMOVED*** Import and create app using core module
from backend_api.core.app import create_app

***REMOVED*** Create the FastAPI application with injected settings
app = create_app(settings)

logger.info("Backend Service initialized successfully")

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
