"""Main FastAPI application for Search service."""

import os
from typing import Optional
from pathlib import Path

from fastapi import FastAPI

***REMOVED*** Import configuration after environment variables are loaded
from search_api.config.app import settings

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
            logger_name="search_api",
            color_theme="modern",
            http_verbose=False,  ***REMOVED*** Keep HTTP logs quiet unless debugging
            component_levels={
                "redis": "INFO",  ***REMOVED*** Redis operations
                "middlewares": "INFO",  ***REMOVED*** Middleware logs
                "routes": "INFO",  ***REMOVED*** Route logs
                "health": "WARNING",  ***REMOVED*** Keep health checks quiet
                "search": "INFO",  ***REMOVED*** Search operations
                "suggestions": "INFO",  ***REMOVED*** Suggestion operations
            },
        )

        logger = get_logger("search_api.main")

        ***REMOVED*** Log main application startup
        logger.info("Initializing Next Watch Search Service", service="search-api")
        logger.info("Environment configuration", environment=settings.environment)

        ***REMOVED*** Import and create app using fast-core integration
        from search_api.core.app_fast_core import create_search_app

        _app = create_search_app(settings)
        logger.info("Search Service initialized successfully", service="search-api")

    return _app


***REMOVED*** Create app instance for direct import (web server use)
app = get_app()


if __name__ == "__main__":
    ***REMOVED*** Use the proper main function with full production/development configuration
    from search_api.__main__ import main

    main()
