"""Main FastAPI application for the Next Watch Backend API service."""

import os
from pathlib import Path

***REMOVED*** Import configuration after environment variables are loaded
from backend_api.config.app import settings
from backend_api.config.logging import configure_logging, get_logger

***REMOVED*** Configure logging early with enhanced settings
from backend_api.config.logging import get_logger

***REMOVED*** Configure logging early with enhanced settings
configure_logging(
    log_level=settings.log_level,
    log_dir=settings.logs_dir if hasattr(settings, "logs_dir") else None,
    verbose=settings.debug,
    quiet=False,
    use_coloredlogs=True,
    logger_name="backend_api",
    color_theme="modern",
    http_verbose=False,  ***REMOVED*** Keep HTTP logs quiet unless debugging
    component_levels={
        "db": "INFO",  ***REMOVED*** Database queries
        "middlewares": "INFO",  ***REMOVED*** Middleware logs
        "routes": "INFO",  ***REMOVED*** Route logs
        "health": "WARNING",  ***REMOVED*** Keep health checks quiet
    },
)

***REMOVED*** Get logger for this module
logger = get_logger(__name__)

***REMOVED*** Log main application startup
logger.info("Initializing Next Watch Backend Service", service="backend-api")
logger.info("Environment configuration", environment=os.getenv("ENVIRONMENT", "development"))

***REMOVED*** Import and create app using core module
from backend_api.core.app import create_app

***REMOVED*** Create the FastAPI application with injected settings
app = create_app(settings)

logger.info("Backend Service initialized successfully", service="backend-api")

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
