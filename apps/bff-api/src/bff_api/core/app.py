"""Application factory for the BFF service.

This module contains the FastAPI application factory, lifespan management,
and global exception handling for the Next Watch BFF service.
"""

import datetime
import os
import traceback
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from config.logging import get_logger
from bff_api.services.auth_client import AuthClient

***REMOVED*** Import services
from bff_api.services.backend_client import BackendClient
from bff_api.services.cache_service import close_cache_service, get_cache_service
from bff_api.services.health_service import HealthService, close_health_service
from bff_api.services.cache_service.background_warming_service import (
    start_background_warming,
    stop_background_warming,
)

logger = get_logger(__name__)

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
    logger.info("Starting BFF service", service="bff")
    if _app_settings:
        logger.info(
            "BFF service configuration loaded",
            environment=getattr(_app_settings, "environment", "unknown"),
            backend_api_url=getattr(_app_settings, "backend_api_url", "unknown"),
            reco_api_url=getattr(_app_settings, "reco_api_url", "unknown"),
            auth_api_url=getattr(_app_settings, "auth_api_url", "unknown"),
            debug_mode=getattr(_app_settings, "debug", False),
        )

    ***REMOVED*** Initialize cache service
    logger.info("Initializing cache service", service="bff", component="cache_service")
    cache_service = get_cache_service()
    cache_healthy = await cache_service.health_check()
    logger.info(
        "Cache service initialized",
        service="bff",
        component="cache_service",
        healthy=cache_healthy,
    )

    ***REMOVED*** Initialize backend client
    logger.info("Initializing backend client", service="bff", component="backend_client")
    try:
        if _app_settings is None:
            raise ValueError("Settings not initialized")
        backend_client = BackendClient(_app_settings)
        app.state.backend_client = backend_client
        logger.info(
            "Backend client initialized successfully", service="bff", component="backend_client"
        )
    except Exception as e:
        logger.error(
            "Failed to initialize backend client",
            service="bff",
            component="backend_client",
            error=str(e),
        )
        raise

    ***REMOVED*** Initialize auth client
    logger.info("Initializing auth client", service="bff", component="auth_client")
    try:
        if _app_settings is None:
            raise ValueError("Settings not initialized")
        auth_client = AuthClient(_app_settings)
        app.state.auth_client = auth_client
        logger.info("Auth client initialized successfully", service="bff", component="auth_client")
    except Exception as e:
        logger.error(
            "Failed to initialize auth client", service="bff", component="auth_client", error=str(e)
        )
        raise

    ***REMOVED*** Initialize health service
    logger.info("Initializing health service", service="bff", component="health_service")
    try:
        health_service = HealthService()
        app.state.health_service = health_service
        logger.info(
            "Health service initialized successfully", service="bff", component="health_service"
        )
    except Exception as e:
        logger.error(
            "Failed to initialize health service",
            service="bff",
            component="health_service",
            error=str(e),
        )
        ***REMOVED*** Continue without health service if it fails
        app.state.health_service = None

    ***REMOVED*** Start background warming service
    logger.info(
        "Starting background warming service", service="bff", component="background_warming"
    )
    try:
        await start_background_warming()
        logger.info(
            "Background warming service started successfully",
            service="bff",
            component="background_warming",
        )
    except Exception as e:
        logger.error(
            "Failed to start background warming service",
            service="bff",
            component="background_warming",
            error=str(e),
        )
        ***REMOVED*** Continue without background warming if it fails
        pass

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down BFF service", service="bff", phase="shutdown")

    ***REMOVED*** Shutdown health service
    if hasattr(app.state, "health_service") and app.state.health_service is not None:
        try:
            logger.info(
                "Shutting down health service",
                service="bff",
                component="health_service",
                phase="shutdown",
            )
            await app.state.health_service.close()
            logger.info(
                "Health service shut down successfully", service="bff", component="health_service"
            )
        except Exception as e:
            logger.error(
                "Error shutting down health service",
                service="bff",
                component="health_service",
                error=str(e),
            )

    ***REMOVED*** Shutdown backend client
    if hasattr(app.state, "backend_client") and app.state.backend_client is not None:
        try:
            logger.info(
                "Shutting down backend client",
                service="bff",
                component="backend_client",
                phase="shutdown",
            )
            await app.state.backend_client.close()
            logger.info(
                "Backend client shut down successfully", service="bff", component="backend_client"
            )
        except Exception as e:
            logger.error(
                "Error shutting down backend client",
                service="bff",
                component="backend_client",
                error=str(e),
            )

    ***REMOVED*** Shutdown auth client
    if hasattr(app.state, "auth_client") and app.state.auth_client is not None:
        try:
            logger.info(
                "Shutting down auth client",
                service="bff",
                component="auth_client",
                phase="shutdown",
            )
            await app.state.auth_client.close()
            logger.info(
                "Auth client shut down successfully", service="bff", component="auth_client"
            )
        except Exception as e:
            logger.error(
                "Error shutting down auth client",
                service="bff",
                component="auth_client",
                error=str(e),
            )

    ***REMOVED*** Close global health service
    await close_health_service()

    ***REMOVED*** Stop background warming service
    try:
        logger.info(
            "Stopping background warming service",
            service="bff",
            component="background_warming",
            phase="shutdown",
        )
        await stop_background_warming()
        logger.info(
            "Background warming service stopped successfully",
            service="bff",
            component="background_warming",
        )
    except Exception as e:
        logger.error(
            "Error stopping background warming service",
            service="bff",
            component="background_warming",
            error=str(e),
        )

    ***REMOVED*** Close global cache service
    await close_cache_service()

    logger.info("BFF service shutdown complete", service="bff")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions.

    Args:
        request: The incoming request
        exc: The unhandled exception

    Returns:
        JSONResponse with error details
    """
    logger.error("Unhandled exception occurred", service="bff", error=str(exc), exc_info=True)
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

    from bff_api.routes.api_v1 import api_v1_router
    from bff_api.routes.health import router as health_router
    from bff_api.routes.meta import router as meta_router

    from .middleware import setup_middleware

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
