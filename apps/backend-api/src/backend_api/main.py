"""Main FastAPI application for the Next Watch Backend API service."""

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI

***REMOVED*** Import configuration after environment variables are loaded
from backend_api.config.app import settings

***REMOVED*** Lazy app initialization - only create when needed
_app: Optional[FastAPI] = None


def get_app() -> FastAPI:
    """Get or create the FastAPI application instance with full logging."""
    global _app
    if _app is None:
        ***REMOVED*** Configure logging for web server mode
        from config.logging import configure_logging, get_logger

        ***REMOVED*** Configure logging with enhanced settings
        log_dir = None
        if settings.logs_dir:
            log_dir = Path(settings.logs_dir)

        configure_logging(
            log_level=settings.log_level,
            log_dir=log_dir,
            verbose=settings.debug,
            quiet=False,
            use_coloredlogs=settings.debug,  ***REMOVED*** Only use colors in debug mode
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

        logger = get_logger("backend_api.main")

        ***REMOVED*** Log main application startup
        logger.info(
            "Initializing Next Watch Backend Service with Fast Core integration",
            service="backend-api",
        )
        logger.info("Environment configuration", environment=settings.environment)

        ***REMOVED*** Import and create app using fast-core integration
        from backend_api.core.app_fast_core import create_backend_app

        _app = create_backend_app(settings)
        logger.info(
            "Backend Service initialized successfully with Fast Core", service="backend-api"
        )

    return _app


***REMOVED*** Create app instance for direct import (web server use)
app = get_app()


if __name__ == "__main__":
    ***REMOVED*** Use the proper main function with full production/development configuration
    from backend_api.__main__ import main

    main()
