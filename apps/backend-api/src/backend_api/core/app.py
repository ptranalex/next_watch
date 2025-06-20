"""Application factory for the Backend API service.

from config.logging import get_logger
This module contains the FastAPI application factory, lifespan management,
and global exception handling for the Next Watch Backend API service.
"""

import datetime
import os
import traceback
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from config.logging import get_logger

***REMOVED*** Import database initialization
from backend_api.db.database import get_db, init_database

***REMOVED*** Import services
from backend_api.services.health_service import HealthService, close_health_service

try:
    from backend_api.services.suggestion_engine import SuggestionEngine

    suggestion_service_enabled = True
except ImportError:
    suggestion_service_enabled = False

logger = get_logger(__name__)

***REMOVED*** Module-level settings for lifespan access
_app_settings: Optional[Any] = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown of the FastAPI application including
    database initialization, health service, and suggestion engine setup.

    Args:
        app: FastAPI application instance

    Yields:
        None: Application runs between startup and shutdown
    """
    ***REMOVED*** Startup
    logger.info("Starting Backend API service")
    if _app_settings:
        logger.info(f"Environment: {getattr(_app_settings, 'environment', 'unknown')}")
        logger.info(f"Debug mode: {getattr(_app_settings, 'debug', False)}")

    ***REMOVED*** Initialize database
    logger.info("Initializing database connection")
    try:
        init_database()
        logger.info("Database connection established successfully")
        if _app_settings:
            logger.debug(f"Using database URL: {_app_settings.get_database_url_masked()}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    ***REMOVED*** Initialize health service
    logger.info("Initializing health service")
    try:
        health_service = HealthService()
        app.state.health_service = health_service
        logger.info("Health service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize health service: {e}")
        ***REMOVED*** Continue without health service if it fails
        app.state.health_service = None

    ***REMOVED*** Initialize suggestion engine
    suggestion_engine = None
    if suggestion_service_enabled:
        try:
            ***REMOVED*** Get Redis URL with priority:
            ***REMOVED*** 1. SUGGESTION_REDIS_URL (specific to suggestion engine)
            ***REMOVED*** 2. CACHE_REDIS_URL (general cache configuration)
            ***REMOVED*** 3. settings.redis_url (fallback)
            redis_url = os.getenv("SUGGESTION_REDIS_URL")
            if not redis_url:
                redis_url = os.getenv("CACHE_REDIS_URL")
            if not redis_url and _app_settings:
                redis_url = _app_settings.redis_url

            if not redis_url:
                raise ValueError("Redis URL not configured")

            ***REMOVED*** Log with masking for security
            masked_url = (
                redis_url.replace(":" + redis_url.split(":")[-2], ":***")
                if ":" in redis_url and "@" in redis_url
                else redis_url
            )
            logger.info(f"Initializing Redis suggestion engine with URL: {masked_url}")

            suggestion_engine = SuggestionEngine(redis_url)
            await suggestion_engine.initialize()
            app.state.suggestion_engine = suggestion_engine

            logger.info("Redis suggestion engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis suggestion engine: {e}")
            logger.error(traceback.format_exc())
            ***REMOVED*** Don't raise - application should still start without suggestion service
    else:
        logger.warning("Suggestion service not enabled - Redis dependencies missing")

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down Backend API service")

    ***REMOVED*** Shutdown health service
    if hasattr(app.state, "health_service") and app.state.health_service is not None:
        try:
            logger.info("Shutting down health service")
            app.state.health_service.close()
            logger.info("Health service shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down health service: {e}")

    ***REMOVED*** Shutdown suggestion engine
    if hasattr(app.state, "suggestion_engine") and app.state.suggestion_engine is not None:
        try:
            logger.info("Shutting down Redis suggestion engine")
            await app.state.suggestion_engine.shutdown()
            logger.info("Redis suggestion engine shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down Redis suggestion engine: {e}")
            logger.error(traceback.format_exc())

    ***REMOVED*** Close global health service
    close_health_service()


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions.

    Args:
        request: The incoming request
        exc: The unhandled exception

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def create_app(settings: Optional[Any] = None) -> FastAPI:
    """Create and configure FastAPI application.

    Args:
        settings: Optional settings instance. If None, will import default settings.

    Returns:
        Configured FastAPI application with all middleware and routes
    """
    global _app_settings

    ***REMOVED*** Import settings only if not provided (for backward compatibility)
    if settings is None:
        from backend_api.config.app import settings as default_settings

        settings = default_settings

    _app_settings = settings

    from backend_api.routes.api_v1 import api_v1_router
    from backend_api.routes.health import router as health_router
    from backend_api.routes.meta import router as meta_router

    from .middleware import setup_middleware

    ***REMOVED*** Create FastAPI application
    app = FastAPI(
        title="Next Watch Backend API",
        description="Backend for Frontend API for serving movie data and user interactions",
        version="0.1.0",
        debug=getattr(settings, "debug", False),
        lifespan=lifespan,
    )

    ***REMOVED*** Setup middleware
    setup_middleware(app)

    ***REMOVED*** Register routers
    app.include_router(meta_router, tags=["meta"])
    app.include_router(health_router, tags=["health"])
    app.include_router(api_v1_router, tags=["api_v1"])

    ***REMOVED*** Add global exception handler
    app.add_exception_handler(Exception, global_exception_handler)

    return app
