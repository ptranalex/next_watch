"""Core FastAPI application factory and configuration.

This module contains the FastAPI application factory, lifespan management,
and global exception handling for the Next Watch Recommendation API service.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config.logging import get_logger
from recommendation_api.core.middleware import setup_middleware
from recommendation_api.routes.health import router as health_router
from recommendation_api.routes import api_v1_router
from recommendation_api.services.health_service import get_health_service, close_health_service
from recommendation_api.services.cache_service import (
    get_cache_service,
    close_cache_service,
    configure_recommendation_warming,
    start_background_warming,
    stop_background_warming,
)
from recommendation_api.services.backend_client import get_backend_client, close_backend_client
from recommendation_api.services.movie_adapter import get_movie_adapter
from recommendation_api.services.vector_service import get_vector_service, close_vector_service

logger = get_logger(__name__)

***REMOVED*** Module-level settings for lifespan access
_app_settings: Optional[Any] = None


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
    logger.info("Starting Recommendation API service", service="recommendation-api")
    if _app_settings:
        logger.info(
            "Recommendation API configuration loaded",
            service="recommendation-api",
            environment=getattr(_app_settings, "environment", "unknown"),
            backend_api_url=getattr(_app_settings, "backend_api_url", "unknown"),
            ml_api_url=getattr(_app_settings, "ml_api_url", "unknown"),
            debug_mode=getattr(_app_settings, "debug", False),
        )

    ***REMOVED*** Initialize cache service
    if getattr(_app_settings, "enable_caching", True):
        logger.info(
            "Initializing cache service", service="recommendation-api", component="cache_service"
        )
        try:
            ***REMOVED*** Get the global cache service instance
            cache_service = get_cache_service()

            ***REMOVED*** Check if cache is healthy
            is_healthy = await cache_service.health_check()
            logger.info(
                "Cache service initialized",
                service="recommendation-api",
                component="cache_service",
                healthy=is_healthy,
            )

            ***REMOVED*** Initialize cache warming if enabled
            if getattr(_app_settings, "enable_warming", True):
                try:
                    logger.info(
                        "Initializing cache warming",
                        service="recommendation-api",
                        component="warming_service",
                    )
                    ***REMOVED*** Configure warming service
                    configure_recommendation_warming()

                    ***REMOVED*** Start background warming if enabled
                    if getattr(_app_settings, "enable_background_warming", True):
                        await start_background_warming()
                        logger.info(
                            "Background warming service started",
                            service="recommendation-api",
                            component="warming_service",
                        )
                except Exception as e:
                    logger.error(
                        "Failed to initialize cache warming",
                        service="recommendation-api",
                        component="warming_service",
                        error=str(e),
                    )
                    ***REMOVED*** Continue without warming if initialization fails
        except Exception as e:
            logger.error(
                "Failed to initialize cache service",
                service="recommendation-api",
                component="cache_service",
                error=str(e),
            )
            ***REMOVED*** Continue without cache if initialization fails
    else:
        logger.info(
            "Caching is disabled by configuration",
            service="recommendation-api",
            component="cache_service",
        )

    ***REMOVED*** Initialize health service and store in app state
    logger.info(
        "Initializing health service", service="recommendation-api", component="health_service"
    )
    try:
        health_service = get_health_service()
        app.state.health_service = health_service
        logger.info(
            "Health service initialized successfully",
            service="recommendation-api",
            component="health_service",
        )
    except Exception as e:
        logger.error(
            "Failed to initialize health service",
            service="recommendation-api",
            component="health_service",
            error=str(e),
        )
        ***REMOVED*** Continue without health service if it fails
        app.state.health_service = None

    ***REMOVED*** Initialize backend client and movie adapter
    logger.info(
        "Initializing backend client", service="recommendation-api", component="backend_client"
    )
    try:
        ***REMOVED*** Initialize the global backend client
        backend_client = get_backend_client()
        logger.info(
            "Backend client initialized successfully",
            service="recommendation-api",
            component="backend_client",
        )
    except Exception as e:
        logger.error(
            "Failed to initialize backend client",
            service="recommendation-api",
            component="backend_client",
            error=str(e),
        )
        raise

    ***REMOVED*** Initialize movie adapter
    logger.info(
        "Initializing movie adapter", service="recommendation-api", component="movie_adapter"
    )
    try:
        ***REMOVED*** Initialize the global movie adapter
        movie_adapter = get_movie_adapter()
        logger.info(
            "Movie adapter initialized successfully",
            service="recommendation-api",
            component="movie_adapter",
        )
    except Exception as e:
        logger.error(
            "Failed to initialize movie adapter",
            service="recommendation-api",
            component="movie_adapter",
            error=str(e),
        )
        raise

    ***REMOVED*** Initialize vector service
    logger.info(
        "Initializing vector service", service="recommendation-api", component="vector_service"
    )
    try:
        ***REMOVED*** Initialize the global vector service
        vector_service = get_vector_service()
        logger.info(
            "Vector service initialized successfully",
            service="recommendation-api",
            component="vector_service",
        )
    except Exception as e:
        logger.error(
            "Failed to initialize vector service",
            service="recommendation-api",
            component="vector_service",
            error=str(e),
        )
        ***REMOVED*** Continue without vector service if it fails - some routes may still work

    yield

    ***REMOVED*** Shutdown
    logger.info(
        "Shutting down Recommendation API service", service="recommendation-api", phase="shutdown"
    )

    ***REMOVED*** Cleanup warming service
    if getattr(_app_settings, "enable_caching", True) and getattr(
        _app_settings, "enable_warming", True
    ):
        try:
            if getattr(_app_settings, "enable_background_warming", True):
                logger.info(
                    "Stopping background warming service",
                    service="recommendation-api",
                    component="warming_service",
                    phase="shutdown",
                )
                await stop_background_warming()
                logger.info(
                    "Background warming service stopped",
                    service="recommendation-api",
                    component="warming_service",
                )
        except Exception as e:
            logger.error(
                "Error stopping background warming service",
                service="recommendation-api",
                component="warming_service",
                error=str(e),
            )

    ***REMOVED*** Cleanup cache service
    if getattr(_app_settings, "enable_caching", True):
        try:
            logger.info(
                "Closing cache service",
                service="recommendation-api",
                component="cache_service",
                phase="shutdown",
            )
            await close_cache_service()
            logger.info(
                "Cache service closed successfully",
                service="recommendation-api",
                component="cache_service",
            )
        except Exception as e:
            logger.error(
                "Error closing cache service",
                service="recommendation-api",
                component="cache_service",
                error=str(e),
            )

    ***REMOVED*** Cleanup health service
    if hasattr(app.state, "health_service") and app.state.health_service:
        try:
            logger.info(
                "Closing health service",
                service="recommendation-api",
                component="health_service",
                phase="shutdown",
            )
            app.state.health_service.close()
            logger.info(
                "Health service closed successfully",
                service="recommendation-api",
                component="health_service",
            )
        except Exception as e:
            logger.error(
                "Error closing health service",
                service="recommendation-api",
                component="health_service",
                error=str(e),
            )

    ***REMOVED*** Close global health service
    await close_health_service()

    ***REMOVED*** Cleanup backend client
    try:
        logger.info(
            "Closing backend client",
            service="recommendation-api",
            component="backend_client",
            phase="shutdown",
        )
        await close_backend_client()
        logger.info(
            "Backend client closed successfully",
            service="recommendation-api",
            component="backend_client",
        )
    except Exception as e:
        logger.error(
            "Error closing backend client",
            service="recommendation-api",
            component="backend_client",
            error=str(e),
        )

    ***REMOVED*** Cleanup vector service
    try:
        logger.info(
            "Closing vector service",
            service="recommendation-api",
            component="vector_service",
            phase="shutdown",
        )
        await close_vector_service()
        logger.info(
            "Vector service closed successfully",
            service="recommendation-api",
            component="vector_service",
        )
    except Exception as e:
        logger.error(
            "Error closing vector service",
            service="recommendation-api",
            component="vector_service",
            error=str(e),
        )

    logger.info("Recommendation API service shutdown complete", service="recommendation-api")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions.

    Args:
        request: The incoming request
        exc: The unhandled exception

    Returns:
        JSONResponse with error details
    """
    logger.error(
        "Unhandled exception occurred", service="recommendation-api", error=str(exc), exc_info=True
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def create_app(settings: Optional[Any] = None) -> FastAPI:
    """Create and configure FastAPI application.

    Args:
        settings: Optional settings instance. If None, will import default settings.

    Returns:
        Configured FastAPI application instance
    """
    global _app_settings

    ***REMOVED*** Import settings only if not provided (for backward compatibility)
    if settings is None:
        from recommendation_api.config import settings as default_settings

        settings = default_settings

    _app_settings = settings

    ***REMOVED*** Create FastAPI app
    app = FastAPI(
        title="Recommendation API",
        description="AI-powered movie recommendation service for Next Watch platform",
        version="0.1.0",
        debug=getattr(settings, "debug", False),
        lifespan=lifespan,
    )

    ***REMOVED*** Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    ***REMOVED*** Setup middleware
    setup_middleware(app)

    ***REMOVED*** Include routers
    app.include_router(health_router, tags=["health"])
    app.include_router(api_v1_router, prefix="/reco", tags=["reco-v1"])

    ***REMOVED*** Add global exception handler
    app.add_exception_handler(Exception, global_exception_handler)

    return app
