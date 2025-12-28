"""Main FastAPI application for Search service."""

import os
import threading
from pathlib import Path

from fastapi import FastAPI

***REMOVED*** Import configuration after environment variables are loaded
from search_api.config.app import settings

***REMOVED*** Lazy app initialization - only create when needed
_app: FastAPI | None = None
_app_lock = threading.Lock()  ***REMOVED*** Thread-safe initialization
_initialized = False  ***REMOVED*** Additional flag to prevent re-initialization


def create_app() -> FastAPI:
    """Factory function for creating the FastAPI app.

    This is the function that should be called by Uvicorn to avoid
    double initialization issues with module-level app creation.
    """
    global _app, _initialized

    ***REMOVED*** Double-checked locking pattern for thread safety
    if _app is not None and _initialized:
        return _app

    with _app_lock:
        ***REMOVED*** Check again inside the lock
        if _app is not None and _initialized:
            return _app

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

        ***REMOVED*** Log main application startup with process ID for debugging
        process_id = os.getpid()
        logger.info(
            "Initializing Next Watch Search Service", service="search-api", process_id=process_id
        )
        logger.info("Environment configuration", environment=settings.environment)

        ***REMOVED*** Import and create app using fast-core integration
        from search_api.core.app_fast_core import create_search_app

        _app = create_search_app(settings)
        _initialized = True  ***REMOVED*** Mark as fully initialized
        logger.info(
            "Search Service initialized successfully", service="search-api", process_id=process_id
        )

    return _app


if __name__ == "__main__":
    ***REMOVED*** Use the proper main function with full production/development configuration
    from search_api.__main__ import main

    main()
