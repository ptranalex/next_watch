"""Fast-Core application factory for Backend API.

This module creates a FastAPI application using the fast-core library
with Backend-specific configuration and dependencies.
"""

import os
from typing import List, Optional, AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fast_core import create_app, AppOptions
from fast_core.middleware import MiddlewareConfig

from backend_api.config.app import BackendAPIConfig
from backend_api.config.fast_core_config import create_fast_core_config
from backend_api.db.database import init_database
from backend_api.services.health_service import HealthService, close_health_service
from config.logging import get_logger

***REMOVED*** Import Backend routes
from backend_api.routes.health import router as health_router
from backend_api.routes.meta import router as meta_router
from backend_api.routes.api_v1 import api_v1_router

logger = get_logger(__name__)

***REMOVED*** Backend API focuses on core movie data operations


@asynccontextmanager
async def backend_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for Backend API.

    Handles startup and shutdown events for the Backend API application.
    Uses Service Client Factory for better lifecycle management.
    """
    ***REMOVED*** Startup
    logger.info("Starting Backend API application with Fast Core integration")
    settings = app.state.settings

    ***REMOVED*** Log configuration summary
    logger.info(f"Backend API starting on {settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")

    ***REMOVED*** Initialize database
    logger.info("Initializing database connection")
    try:
        init_database()
        logger.info("Database connection established successfully")
        if hasattr(settings, "get_database_url_masked"):
            logger.debug(f"Database configuration: {settings.get_database_url_masked()}")
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
        app.state.health_service = None

    ***REMOVED*** Backend API focuses on core movie data - no suggestion engine needed
    logger.info("Backend API handles core movie data operations")

    ***REMOVED*** Initialize Backend-specific metrics (if enabled)
    backend_config = app.state.settings
    ***REMOVED*** Initialize Backend-specific metrics (always enabled for observability)
    try:
        from backend_api.core.metrics import initialize_backend_metrics

        metrics_instance = initialize_backend_metrics()
        if metrics_instance:
            logger.info("Backend metrics initialized successfully")
            app.state.metrics = metrics_instance
        else:
            logger.warning(
                "Backend metrics initialization returned None - metrics registry not available"
            )
    except ImportError as e:
        logger.error(f"Metrics dependencies not installed: {e}")
        logger.info("Install prometheus-client to enable metrics: pip install prometheus-client")
    except Exception as e:
        logger.error(f"Failed to initialize Backend metrics: {e}", exc_info=True)
        if getattr(backend_config, "is_production", False):
            ***REMOVED*** In production, we want to know about metrics failures
            raise

    ***REMOVED*** Backend API is independent - no external service registrations needed
    logger.info("Backend API runs independently without external service dependencies")

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down Backend API application")

    ***REMOVED*** Shutdown health service
    if hasattr(app.state, "health_service") and app.state.health_service is not None:
        try:
            logger.info("Shutting down health service")
            app.state.health_service.close()
            logger.info("Health service shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down health service: {e}")

    ***REMOVED*** No suggestion engine to shutdown - Backend API is focused on core data

    ***REMOVED*** Close global health service
    close_health_service()

    logger.info("Backend API service shutdown complete")


def create_backend_middleware_config(config: BackendAPIConfig) -> MiddlewareConfig:
    """Create Backend-specific middleware configuration using the Middleware Builder.

    Args:
        config: Backend API configuration

    Returns:
        Configured middleware with Backend-specific settings
    """
    middleware = MiddlewareConfig()

    ***REMOVED*** Configure CORS for Backend API (serves frontend and other services)
    middleware.cors(
        origins=config.cors_origins,
        credentials=True,  ***REMOVED*** Backend needs credentials for auth
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        headers=["Content-Type", "Authorization", "X-Requested-With", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Process-Time", "X-Cache-Status"],
        max_age=3600,  ***REMOVED*** Cache preflight requests for 1 hour
    )

    ***REMOVED*** Configure security headers for production
    if config.is_production:
        middleware.security_headers(
            hsts=True,
            hsts_max_age=63072000,  ***REMOVED*** 2 years
            hsts_include_subdomains=True,
            frame_options="DENY",  ***REMOVED*** Prevent iframe embedding
            content_type_options=True,
            xss_protection=True,
            csp="default-src 'self'; connect-src 'self' https://*.example.com; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'",
            referrer_policy="strict-origin-when-cross-origin",
            trusted_hosts=config.allowed_hosts,
        )
    else:
        ***REMOVED*** Development security headers (more permissive)
        middleware.security_headers(
            hsts=False,  ***REMOVED*** No HSTS in development
            frame_options="SAMEORIGIN",
            content_type_options=True,
            xss_protection=True,
            referrer_policy="strict-origin-when-cross-origin",
        )

    ***REMOVED*** Configure rate limiting for Backend API protection
    rate_limit_config = {
        ***REMOVED*** Core movie data endpoints
        "/api/v1/movies": "300/minute",
        "/api/v1/movies/{movie_id}": "500/minute",
        "/api/v1/movies/search": "100/minute",
        "/api/v1/movies/bulk": "500/minute",
        "/api/v1/movies/{movie_id}/cast": "200/minute",
        "/api/v1/movies/{movie_id}/trailers": "200/minute",
        ***REMOVED*** User interaction endpoints (managed by BFF auth)
        "/api/v1/user/movies": "200/minute",
        "/api/v1/user/movies/{movie_id}": "100/minute",
        ***REMOVED*** Health and meta endpoints (less restrictive)
        "/health": "1000/minute",
        "/meta": "1000/minute",
    }

    middleware.rate_limiting(
        default_limit="1000/hour" if config.is_production else "2000/hour",
        endpoints=rate_limit_config,
        exempt_ips=["127.0.0.1", "::1"]
        + (["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"] if not config.is_production else []),
        headers=True,  ***REMOVED*** Include rate limit headers for debugging
        key_func="ip",  ***REMOVED*** Rate limit by IP address
    )

    ***REMOVED*** Configure logging for Backend API
    log_level = "INFO" if config.is_production else "DEBUG"
    middleware.logging(
        level=log_level,
        include_request_body=not config.is_production,  ***REMOVED*** Only log bodies in development
        include_response_body=False,  ***REMOVED*** Never log response bodies (too verbose)
        max_body_size=2048,
        exclude_paths=["/health", "/docs", "/openapi.json", "/favicon.ico"],
        include_headers=True,
        exclude_headers=["authorization", "cookie", "x-api-key", "internal-api-key"],
        log_timing=True,
        log_user_agent=not config.is_production,  ***REMOVED*** Only in development
    )

    ***REMOVED*** Configure request processing for Backend API
    middleware.request_processing(
        max_request_size=10 * 1024 * 1024,  ***REMOVED*** 10MB for file uploads
        timeout=60,  ***REMOVED*** Backend might handle complex queries
        include_request_id=True,
        request_id_header="X-Request-ID",
        include_process_time=True,
        process_time_header="X-Process-Time",
        gzip_compression=True,
        gzip_minimum_size=1000,
    )

    ***REMOVED*** Configure Prometheus metrics for Backend monitoring
    middleware.metrics(
        endpoint_path="/metrics",
        include_endpoint=True,
        exclude_paths=["/health", "/docs", "/openapi.json", "/favicon.ico"],
        exclude_methods=["OPTIONS"],
        track_request_size=True,
        track_response_size=True,
        enabled=True,  ***REMOVED*** Always enable metrics for production observability
    )

    logger.info(f"Backend middleware configured for {config.environment} environment")
    return middleware


def create_backend_app(config: Optional[BackendAPIConfig] = None) -> FastAPI:
    """Create Backend API application using fast-core with enhanced middleware.

    Args:
        config: Backend API configuration (creates default if None)

    Returns:
        Configured FastAPI application
    """
    ***REMOVED*** Create or use provided configuration
    if config is None:
        from backend_api.config.app import settings

        config = settings

    logger.info("Creating Backend API application with fast-core and enhanced middleware")

    ***REMOVED*** Convert Backend config to fast-core config
    fast_core_config = create_fast_core_config(config)

    ***REMOVED*** Create Backend-specific middleware configuration
    middleware_config = create_backend_middleware_config(config)

    ***REMOVED*** Define routers for the application
    routers = [
        meta_router,
        health_router,
        api_v1_router,
    ]

    ***REMOVED*** Create app options
    app_options = AppOptions(
        exception_handlers=True,
        health_checks=fast_core_config.is_feature_enabled("health_checks"),
        docs=config.debug,
    )

    ***REMOVED*** Create FastAPI app using fast-core
    app = create_app(
        settings=fast_core_config,
        title="Next Watch Backend API",
        description="Backend for Frontend API for serving movie data and user interactions",
        version="0.1.0",
        options=app_options,
        middleware=middleware_config,
        routers=routers,
        lifespan=backend_lifespan,
    )

    logger.info("Backend API application created with fast-core integration")
    return app


def get_backend_app() -> FastAPI:
    """Get Backend API application instance.

    Returns:
        FastAPI application instance
    """
    return create_backend_app()
