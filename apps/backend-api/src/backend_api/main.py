"""Main FastAPI application for the Next Watch Backend API service."""

from pathlib import Path

from fastapi import FastAPI

# Import configuration after environment variables are loaded
from backend_api.config.app import settings

# Lazy app initialization - only create when needed
_app: FastAPI | None = None


def create_app() -> FastAPI:
    """Factory function for creating the FastAPI app.

    This is the function that should be called by Uvicorn to avoid
    double initialization issues with module-level app creation.
    """
    global _app
    if _app is None:
        # Configure logging for web server mode
        from config.logging import configure_logging, get_logger

        # Configure logging with enhanced settings
        log_dir = None
        if settings.logs_dir:
            log_dir = Path(settings.logs_dir)

        configure_logging(
            log_level=settings.log_level,
            log_dir=log_dir,
            verbose=settings.debug,
            quiet=False,
            use_coloredlogs=settings.debug,  # Only use colors in debug mode
            logger_name="backend_api",
            color_theme="modern",
            http_verbose=False,  # Keep HTTP logs quiet unless debugging
            component_levels={
                "db": "INFO",  # Database queries
                "middlewares": "INFO",  # Middleware logs
                "routes": "INFO",  # Route logs
                "health": "WARNING",  # Keep health checks quiet
            },
        )

        logger = get_logger("backend_api.main")

        # Log main application startup
        logger.info(
            "Initializing Next Watch Backend Service with Fast Core integration",
            service="backend-api",
        )
        logger.info("Environment configuration", environment=settings.environment)

        # Import and create app using fast-core integration
        from backend_api.core.app_fast_core import create_backend_app

        _app = create_backend_app(settings)
        logger.info(
            "Backend Service initialized successfully with Fast Core",
            service="backend-api",
        )

    return _app


if __name__ == "__main__":
    # Use the proper main function with full production/development configuration
    from backend_api.__main__ import main

    main()
