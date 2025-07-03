"""Application factory for FastAPI services.

This module provides a standardized way to create FastAPI applications
with consistent configuration, middleware, and error handling.
"""

import structlog
from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    Union,
    TYPE_CHECKING,
)

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

if TYPE_CHECKING:
    from fast_core.middleware import MiddlewareConfig

logger = structlog.get_logger(__name__)


class AppOptions:
    """Configuration options for the FastAPI application."""

    def __init__(
        self,
        *,
        exception_handlers: bool = True,
        health_checks: bool = True,
        docs: bool = True,
        meta_endpoints: bool = True,
        meta_features: Optional[List[str]] = None,
        meta_endpoints_map: Optional[Dict[str, str]] = None,
        meta_debug_provider: Optional[Callable] = None,
    ):
        self.exception_handlers = exception_handlers
        self.health_checks = health_checks
        self.docs = docs
        self.meta_endpoints = meta_endpoints
        self.meta_features = meta_features
        self.meta_endpoints_map = meta_endpoints_map
        self.meta_debug_provider = meta_debug_provider


@asynccontextmanager
async def default_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Default lifespan manager for FastAPI applications.

    Provides standard startup and shutdown logic.

    Args:
        app: FastAPI application instance

    Yields:
        None: Application runs between startup and shutdown
    """
    ***REMOVED*** Startup
    logger.info("Starting application")

    ***REMOVED*** Get settings if available
    settings = getattr(app.state, "settings", None)
    if settings:
        environment = getattr(settings, "environment", "unknown")
        debug = getattr(settings, "debug", False)
        logger.info(f"Application configuration - environment: {environment}, debug: {debug}")

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down application")


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


def create_app(
    settings: Any,
    title: Optional[str] = None,
    description: Optional[str] = None,
    version: str = "0.1.0",
    options: Optional[AppOptions] = None,
    middleware: Optional["MiddlewareConfig"] = None,
    routers: Optional[List[APIRouter]] = None,
    lifespan: Optional[Callable] = None,
    on_startup: Optional[List[Callable]] = None,
    on_shutdown: Optional[List[Callable]] = None,
) -> FastAPI:
    """Create a FastAPI application with standard configuration.

    Args:
        settings: Service configuration object
        title: API title (defaults to service_name from settings)
        description: API description
        version: API version
        options: Application options for non-middleware features
        middleware: Middleware configuration using the new MiddlewareConfig system
        routers: List of routers to include
        lifespan: Custom lifespan manager (overrides default)
        on_startup: Startup event handlers
        on_shutdown: Shutdown event handlers

    Returns:
        Configured FastAPI application

    Example:
        ***REMOVED*** Create middleware configuration
        middleware_config = MiddlewareConfig()
        middleware_config.cors(origins=["https://app.example.com"]).security_headers()

        ***REMOVED*** Create app
        app = create_app(
            settings=settings,
            middleware=middleware_config,
            routers=[api_router]
        )
    """
    options = options or AppOptions()

    ***REMOVED*** Get values from settings
    service_name = getattr(settings, "service_name", "FastAPI Service")
    debug_mode = getattr(settings, "debug", False)

    ***REMOVED*** Configure FastAPI application
    app = FastAPI(
        title=title or service_name,
        description=description or f"API for {service_name}",
        version=version,
        debug=debug_mode,
        docs_url="/docs" if options.docs else None,
        redoc_url="/redoc" if options.docs else None,
        openapi_url="/openapi.json" if options.docs else None,
        lifespan=lifespan or default_lifespan,
    )

    ***REMOVED*** Store settings in app state
    app.state.settings = settings

    ***REMOVED*** Setup tracing (before other middleware)
    try:
        from fast_core.middleware.tracing import setup_tracing

        setup_tracing(app, settings)
    except ImportError:
        logger.warning("Tracing module not available, skipping tracing setup")
    except Exception as e:
        logger.warning("Failed to setup tracing", error=str(e))

    ***REMOVED*** Setup middleware using the new system
    if middleware is not None:
        try:
            from fast_core.middleware import setup_middleware

            setup_middleware(app, middleware)
        except ImportError:
            logger.warning("Middleware module not available, skipping middleware setup")

    ***REMOVED*** Setup exception handlers
    if options.exception_handlers:
        ***REMOVED*** For now, just use the global exception handler
        ***REMOVED*** In the future, we can add more sophisticated error handling
        app.add_exception_handler(Exception, global_exception_handler)

    ***REMOVED*** Setup health checks
    if options.health_checks:
        ***REMOVED*** BREAKING CHANGE: Old health check system removed
        ***REMOVED*** Services must now use setup_kubernetes_health_checks() directly
        ***REMOVED*** and set health_checks=False in AppOptions
        raise RuntimeError(
            "Built-in health_checks=True is no longer supported. "
            "Set health_checks=False and use setup_kubernetes_health_checks() directly in your service."
        )

    ***REMOVED*** Setup standardized meta endpoints (optional)
    meta_endpoints = getattr(options, "meta_endpoints", True)
    if meta_endpoints:
        try:
            from fast_core.meta import setup_meta_endpoints

            ***REMOVED*** Extract service description from title or use default
            service_description = description or f"API service for {service_name}"

            setup_meta_endpoints(
                app=app,
                settings=settings,
                service_description=service_description,
                features=options.meta_features,
                endpoints=options.meta_endpoints_map,
                debug_info_provider=options.meta_debug_provider,
            )
        except ImportError:
            logger.warning("Meta endpoints module not available, skipping meta endpoint setup")

    ***REMOVED*** Include routers
    if routers:
        for router in routers:
            app.include_router(router)

    ***REMOVED*** Add startup event handlers
    if on_startup:
        for handler in on_startup:
            app.add_event_handler("startup", handler)

    ***REMOVED*** Add shutdown event handlers
    if on_shutdown:
        for handler in on_shutdown:
            app.add_event_handler("shutdown", handler)

    return app
