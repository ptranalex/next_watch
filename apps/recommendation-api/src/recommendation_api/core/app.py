"""Core FastAPI application factory and configuration."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from recommendation_api.config import settings
from recommendation_api.core.middleware import setup_middleware
from recommendation_api.routes.meta import router as meta_router
from recommendation_api.routes.health import router as health_router
from recommendation_api.routes import api_v1_router
from recommendation_api.services.health_service import get_health_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown of the FastAPI application including
    service initialization and cleanup.

    Args:
        app: FastAPI application instance

    Yields:
        None: Application runs between startup and shutdown
    """
    ***REMOVED*** Startup
    logger.info(f"Starting Recommendation API service with config: {settings}")

    ***REMOVED*** Initialize health service and store in app state
    logger.info("Initializing health service")
    app.state.health_service = get_health_service()

    ***REMOVED*** Initialize any other required services/clients here
    ***REMOVED*** For example: database connections, ML model loading, etc.

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down Recommendation API service")

    ***REMOVED*** Cleanup health service
    if hasattr(app.state, "health_service") and app.state.health_service:
        logger.info("Closing health service")
        app.state.health_service.close()

    ***REMOVED*** Cleanup any other resources here


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
        title="Recommendation API",
        description="AI-powered movie recommendation service for Next Watch platform",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    ***REMOVED*** Setup middleware
    setup_middleware(app)

    ***REMOVED*** Include routers
    app.include_router(meta_router, tags=["meta"])
    app.include_router(health_router, tags=["health"])
    app.include_router(api_v1_router, prefix="/reco", tags=["reco-v1"])

    ***REMOVED*** Add global exception handler
    app.add_exception_handler(Exception, global_exception_handler)

    return app
