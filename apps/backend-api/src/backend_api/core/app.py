"""Application factory for the Backend API service.

This module contains the FastAPI application factory, lifespan management,
and global exception handling for the Next Watch Backend API service.
"""

import datetime
import logging
import os
import traceback
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

***REMOVED*** Import database initialization
from backend_api.db.database import get_db, init_database
from backend_api.config.app import settings

***REMOVED*** Import services
from backend_api.services.health_service import HealthService, close_health_service

try:
    from backend_api.services.suggestion_engine import SuggestionEngine

    suggestion_service_enabled = True
except ImportError:
    suggestion_service_enabled = False

logger = logging.getLogger(__name__)


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

    ***REMOVED*** Initialize database
    logger.info("Initializing database connection")
    try:
        init_database()
        logger.info("Database connection established successfully")
        logger.debug(
            f"Using database URL: {settings._mask_database_password(settings.database_url)}"
        )
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
            ***REMOVED*** Get Redis URL from settings
            logger.info(f"Initializing Redis suggestion engine with URL: {settings.redis_url}")

            suggestion_engine = SuggestionEngine(settings.redis_url)
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


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application with all middleware and routes
    """
    from .middleware import setup_middleware
    from backend_api.routes.api_v1 import api_v1_router
    from backend_api.routes.meta import router as meta_router
    from backend_api.routes.health import router as health_router

    ***REMOVED*** Create FastAPI application
    app = FastAPI(
        title="Next Watch Backend API",
        description="Backend for Frontend API for serving movie data and user interactions",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    ***REMOVED*** Setup middleware
    setup_middleware(app)

    ***REMOVED*** Register routers
    app.include_router(meta_router)
    app.include_router(health_router)
    app.include_router(api_v1_router)

    ***REMOVED*** Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle uncaught exceptions globally.

        Args:
            request: FastAPI request object
            exc: Exception that was raised

        Returns:
            JSON error response
        """
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app
