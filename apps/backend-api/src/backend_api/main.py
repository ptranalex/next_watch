"""Main FastAPI application for the Next Watch Backend API service."""

import os
from pathlib import Path
from typing import Any, Optional

***REMOVED*** Import configuration after environment variables are loaded
from backend_api.config.app import settings

***REMOVED*** Global app variable - will be created after logging is configured
app: Optional[Any] = None


def create_application() -> Any:
    """Create and configure the FastAPI application.

    This function is called after logging has been properly configured
    to avoid permission errors during module import.
    """
    global app

    if app is not None:
        return app

    from backend_api.config.logging import configure_logging, get_logger

    ***REMOVED*** Configure logging with enhanced settings
    log_dir = None
    if settings.logs_dir:
        log_dir = Path(settings.logs_dir)

    configure_logging(
        log_level=settings.log_level,
        log_dir=log_dir,
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

    return app


def main() -> None:
    """Main entry point for running the server."""
    import uvicorn

    ***REMOVED*** Create the application (this will configure logging)
    application = create_application()

    ***REMOVED*** Get environment variables for production configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", settings.api_port))
    workers = int(os.getenv("WORKERS", 1))
    timeout = int(os.getenv("TIMEOUT", 120))
    log_level = os.getenv("LOG_LEVEL", settings.log_level).lower()
    reload = os.getenv("RELOAD", "false").lower() == "true" or settings.debug
    proxy_headers = os.getenv("PROXY_HEADERS", "true").lower() == "true"
    forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "*")
    limit_max_requests = int(os.getenv("LIMIT_MAX_REQUESTS", 10000))
    backlog = int(os.getenv("BACKLOG", 1024))

    ***REMOVED*** Use uvicorn with production-optimized settings
    uvicorn.run(
        application,
        host=host,
        port=port,
        workers=workers,
        timeout_keep_alive=timeout,
        log_level=log_level,
        access_log=False,  ***REMOVED*** Disable access logs for performance
        proxy_headers=proxy_headers,
        forwarded_allow_ips=forwarded_allow_ips,
        limit_max_requests=limit_max_requests,
        backlog=backlog,
        reload=reload,
    )


if __name__ == "__main__":
    main()


***REMOVED*** For uvicorn app loading - create app lazily when first accessed
def get_app() -> Any:
    """Get the FastAPI application instance, creating it if necessary."""
    return create_application()


***REMOVED*** Set up module-level app variable for uvicorn
app = get_app()
