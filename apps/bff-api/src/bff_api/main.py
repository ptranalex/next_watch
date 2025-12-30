"""Main FastAPI application for BFF service."""

from pathlib import Path

from fastapi import FastAPI

# Import configuration after environment variables are loaded
from bff_api.config.app import settings

# Factory pattern - no global app instance


def create_app() -> FastAPI:
    """Create FastAPI application instance using factory pattern."""
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
        logger_name="bff_api",
        color_theme="modern",
        http_verbose=False,  # Keep HTTP logs quiet unless debugging
        component_levels={
            "db": "INFO",  # Database queries
            "middlewares": "INFO",  # Middleware logs
            "routes": "INFO",  # Route logs
            "health": "WARNING",  # Keep health checks quiet
        },
    )

    logger = get_logger("bff_api.main")

    # Log main application startup
    logger.info("Initializing Next Watch BFF Service", service="bff-api")
    logger.info("Environment configuration", environment=settings.environment)

    # Import and create app using fast-core integration
    from bff_api.core.app_fast_core import create_bff_app

    app = create_bff_app(settings)
    logger.info("BFF Service initialized successfully", service="bff-api")

    return app


# Cached app instance for test/runtime convenience
_app: FastAPI | None = None


def get_app() -> FastAPI:
    """Return a cached FastAPI app instance.

    This keeps backwards compatibility with older code/tests that used
    `get_app()` instead of the factory-style `create_app()`.
    """
    global _app
    if _app is None:
        _app = create_app()
    return _app


if __name__ == "__main__":
    # Use the proper main function with full production/development configuration
    from bff_api.__main__ import main

    main()
