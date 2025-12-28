"""Main FastAPI application for the ML API."""

from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI

***REMOVED*** Import configuration after environment variables are loaded
from ml_api.config.app import settings


@lru_cache(maxsize=1)
def get_app() -> FastAPI:
    """Get or create the FastAPI application instance with full logging."""
    from config.logging import configure_logging, get_logger

    ***REMOVED*** Configure logging with enhanced settings
    log_dir = Path(settings.logs_dir) if settings.logs_dir else None

    configure_logging(
        log_level=settings.log_level,
        log_dir=log_dir,
        verbose=settings.debug,
        quiet=False,
        use_coloredlogs=settings.debug,  ***REMOVED*** Only use colors in debug mode
        logger_name="ml_api",
        color_theme="modern",
        http_verbose=False,  ***REMOVED*** Keep HTTP logs quiet unless debugging
        component_levels={
            "embeddings": "INFO",  ***REMOVED*** Embedding service logs
            "models": "INFO",  ***REMOVED*** Model loading logs
            "routes": "INFO",  ***REMOVED*** Route logs
            "health": "WARNING",  ***REMOVED*** Keep health checks quiet
        },
    )

    logger = get_logger("ml_api.main")

    ***REMOVED*** Log main application startup
    logger.info("Initializing Next Watch ML Service", service="ml-api")
    logger.info("Environment configuration", environment=settings.environment)

    ***REMOVED*** Import and create app using fast-core integration
    from ml_api.core.app_fast_core import create_ml_app

    app = create_ml_app(settings)
    logger.info("ML Service initialized successfully", service="ml-api")
    return app


***REMOVED*** Create app instance for direct import (web server use)
app = get_app()


if __name__ == "__main__":
    import uvicorn

    ***REMOVED*** Use settings for all server parameters
    uvicorn.run(
        "ml_api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
