"""Application factory for the BFF service.

This module contains the FastAPI application factory, lifespan management,
and global exception handling for the Next Watch BFF service.
"""

import datetime
import logging
import os
import traceback
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

***REMOVED*** Import services
from bff_api.services.backend_client import BackendClient
from bff_api.services.auth_client import AuthClient
from bff_api.services.health_service import HealthService, close_health_service

logger = logging.getLogger(__name__)

***REMOVED*** Module-level settings for lifespan access
_app_settings: Optional[Any] = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown of the FastAPI application including
    backend client, auth client, health service, and other service initialization.

    Args:
        app: FastAPI application instance

    Yields:
        None: Application runs between startup and shutdown
    """
    ***REMOVED*** Startup
    logger.info("Starting BFF service")
    if _app_settings:
        logger.info(f"Environment: {getattr(_app_settings, 'environment', 'unknown')}")
        logger.info(f"Backend API URL: {getattr(_app_settings, 'backend_api_url', 'unknown')}")
        logger.info(f"Recommendation API URL: {getattr(_app_settings, 'reco_api_url', 'unknown')}")
        logger.info(f"Auth API URL: {getattr(_app_settings, 'auth_api_url', 'unknown')}")
        logger.info(f"Debug mode: {getattr(_app_settings, 'debug', False)}")

    ***REMOVED*** Initialize backend client
    logger.info("Initializing backend client")
    try:
        if _app_settings is None:
            raise ValueError("Settings not initialized")
        backend_client = BackendClient(_app_settings)
        app.state.backend_client = backend_client
        logger.info("Backend client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize backend client: {e}")
        raise

    ***REMOVED*** Initialize auth client
    logger.info("Initializing auth client")
    try:
        if _app_settings is None:
            raise ValueError("Settings not initialized")
        auth_client = AuthClient(_app_settings)
        app.state.auth_client = auth_client
        logger.info("Auth client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize auth client: {e}")
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

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down BFF service")

    ***REMOVED*** Shutdown health service
    if hasattr(app.state, "health_service") and app.state.health_service is not None:
        try:
            logger.info("Shutting down health service")
            await app.state.health_service.close()
            logger.info("Health service shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down health service: {e}")

    ***REMOVED*** Shutdown backend client
    if hasattr(app.state, "backend_client") and app.state.backend_client is not None:
        try:
            logger.info("Shutting down backend client")
            await app.state.backend_client.close()
            logger.info("Backend client shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down backend client: {e}")

    ***REMOVED*** Shutdown auth client
    if hasattr(app.state, "auth_client") and app.state.auth_client is not None:
        try:
            logger.info("Shutting down auth client")
            await app.state.auth_client.close()
            logger.info("Auth client shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down auth client: {e}")

    ***REMOVED*** Close global health service
    await close_health_service()


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
        from bff_api.config.app import settings as default_settings

        settings = default_settings

    _app_settings = settings

    from .middleware import setup_middleware
    from bff_api.routes.api_v1 import api_v1_router
    from bff_api.routes.meta import router as meta_router
    from bff_api.routes.health import router as health_router

    ***REMOVED*** Create FastAPI application
    app = FastAPI(
        title="Next Watch BFF",
        description="Backend for Frontend aggregation layer for Next Watch movie platform",
        version="0.1.0",
        debug=getattr(settings, "debug", False),
        lifespan=lifespan,
    )

    ***REMOVED*** Setup middleware
    setup_middleware(app)

    ***REMOVED*** Register routers (following backend-api pattern)
    app.include_router(meta_router)
    app.include_router(health_router)
    app.include_router(api_v1_router, prefix="/bff")

    ***REMOVED*** Add global exception handler
    app.add_exception_handler(Exception, global_exception_handler)

    return app
