"""Core FastAPI application factory and configuration."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from auth_api.config.app import settings
from auth_api.core.middleware import setup_middleware
from auth_api.routes.auth import router as auth_router
from auth_api.routes.meta import router as meta_router
from auth_api.routes.health import router as health_router
from auth_api.db.database import init_database
from auth_api.services.health_service import get_health_service, close_health_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown of the FastAPI application including
    database initialization.

    Args:
        app: FastAPI application instance

    Yields:
        None: Application runs between startup and shutdown
    """
    ***REMOVED*** Startup
    logger.info("Starting Next Watch Authentication Service")
    logger.info(f"Configuration: {settings}")

    ***REMOVED*** Initialize database
    try:
        init_database()
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    ***REMOVED*** Initialize health service
    try:
        health_service = get_health_service()
        app.state.health_service = health_service
        logger.info("Health service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize health service: {e}")
        ***REMOVED*** Don't raise here - health service is not critical for startup
        app.state.health_service = None

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down Next Watch Authentication Service")

    ***REMOVED*** Close health service
    try:
        close_health_service()
        logger.info("Health service closed successfully")
    except Exception as e:
        logger.warning(f"Error closing health service: {e}")


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


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    ***REMOVED*** Create FastAPI app
    app = FastAPI(
        title="Next Watch Authentication API",
        description="Dedicated authentication service for Next Watch movie platform",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    ***REMOVED*** Setup middleware
    setup_middleware(app)

    ***REMOVED*** Include routers
    app.include_router(health_router, tags=["health"])
    app.include_router(meta_router, tags=["meta"])
    app.include_router(auth_router, prefix="/auth", tags=["auth"])

    ***REMOVED*** Add global exception handler
    app.add_exception_handler(Exception, global_exception_handler)

    return app
