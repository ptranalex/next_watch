"""Main FastAPI application for BFF service."""

from pathlib import Path

from fastapi import FastAPI

***REMOVED*** Import configuration after environment variables are loaded
from auth_api.config.app import settings

***REMOVED*** Factory pattern - no global app instance


def create_app() -> FastAPI:
    """Create FastAPI application instance using factory pattern."""
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
        logger_name="auth_api",
        color_theme="modern",
        http_verbose=False,  ***REMOVED*** Keep HTTP logs quiet unless debugging
        component_levels={
            "db": "INFO",  ***REMOVED*** Database queries
            "middlewares": "INFO",  ***REMOVED*** Middleware logs
            "routes": "INFO",  ***REMOVED*** Route logs
            "health": "WARNING",  ***REMOVED*** Keep health checks quiet
        },
    )

    logger = get_logger("auth_api.main")

    ***REMOVED*** Log main application startup
    logger.info("Initializing Next Watch Auth Service", service="auth-api")
    logger.info("Environment configuration", environment=settings.environment)

    ***REMOVED*** Import and create app using fast-core integration
    from auth_api.core.app_fast_core import create_auth_app

    app = create_auth_app(settings)
    logger.info("Auth Service initialized successfully", service="auth-api")

    return app


if __name__ == "__main__":
    ***REMOVED*** Use the proper main function with full production/development configuration
    from auth_api.__main__ import main

    main()
