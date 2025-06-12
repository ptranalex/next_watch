"""Main FastAPI application for BFF service."""

import os
from typing import Optional
from fastapi import FastAPI

***REMOVED*** Import configuration after environment variables are loaded
from bff_api.config.app import settings

***REMOVED*** Lazy app initialization - only create when needed
_app: Optional[FastAPI] = None


def get_app() -> FastAPI:
    """Get or create the FastAPI application instance with full logging."""
    global _app
    if _app is None:
        ***REMOVED*** Configure logging for web server mode
        from bff_api.core.logging import setup_logging
        from bff_api.config.logging import get_logger

        setup_logging(
            log_level=settings.log_level,
            verbose=settings.debug,
            quiet=False,
            color_theme="modern",
        )

        logger = get_logger("bff_api.main")

        ***REMOVED*** Log main application startup
        logger.info("Initializing Next Watch BFF API", service="bff")
        logger.info(
            "Application environment configured",
            environment=os.getenv("ENVIRONMENT", "development"),
        )

        ***REMOVED*** Import and create app using core module
        from bff_api.core.app import create_app

        _app = create_app(settings)
        logger.info("BFF API initialized successfully", service="bff")

    return _app


***REMOVED*** Create app instance for direct import (web server use)
app = get_app()


if __name__ == "__main__":
    import uvicorn

    ***REMOVED*** Use settings for all server parameters
    uvicorn.run(
        "bff_api.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
