"""Fast-Core application factory for Auth API.

This module creates a FastAPI application using the fast-core library
with Auth-specific configuration and dependencies.
"""

import os
from typing import List, Optional, AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fast_core import create_app, AppOptions
from fast_core.middleware import MiddlewareConfig

from auth_api.config.app import AuthAPIConfig
from auth_api.db.database import init_database
from auth_api.dependencies import get_auth_service, get_current_user, get_db
from auth_api.services.health_service import get_health_service, close_health_service

***REMOVED*** Import Auth routes
from auth_api.routes.health import router as health_router
from auth_api.routes.meta import router as meta_router
from auth_api.routes.api_v1 import api_v1_router

from config.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def auth_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Auth API lifespan manager.

    Handles startup and shutdown of the FastAPI application including
    database initialization and health service management.

    Args:
        app: FastAPI application instance

    Yields:
        None: Application runs between startup and shutdown
    """
    ***REMOVED*** Startup
    logger.info("Starting Next Watch Authentication Service with Fast Core")
    settings = app.state.settings

    ***REMOVED*** Log configuration summary
    logger.info(f"Auth API starting on {settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")

    ***REMOVED*** Initialize Auth-specific metrics (if enabled)
    if getattr(settings, "enable_metrics", True):  ***REMOVED*** Default to enabled
        try:
            from auth_api.core.metrics import initialize_auth_metrics

            metrics_instance = initialize_auth_metrics()
            if metrics_instance:
                logger.info("Auth metrics initialized successfully")
                app.state.metrics = metrics_instance
            else:
                logger.warning(
                    "Auth metrics initialization returned None - metrics registry not available"
                )
        except ImportError as e:
            logger.error(f"Failed to import Auth metrics module: {e}")
        except Exception as e:
            logger.error(f"Error initializing Auth metrics: {e}")

    ***REMOVED*** Initialize database
    try:
        init_database()
        logger.info("Database connection established successfully")
        if hasattr(settings, "get_database_url_masked"):
            logger.debug(f"Database configuration: {settings.get_database_url_masked()}")
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

    logger.info("Auth API handles authentication and authorization for Next Watch platform")

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down Next Watch Authentication Service")

    ***REMOVED*** Close health service
    if hasattr(app.state, "health_service") and app.state.health_service is not None:
        try:
            logger.info("Shutting down health service")
            app.state.health_service.close()
            logger.info("Health service shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down health service: {e}")

        ***REMOVED*** Close global health service
        close_health_service()

    logger.info("Auth API service shutdown complete")


def create_auth_middleware_config(config: AuthAPIConfig) -> MiddlewareConfig:
    """Create Auth API specific middleware configuration.

    Args:
        config: Auth API configuration

    Returns:
        MiddlewareConfig instance with auth-specific settings
    """
    middleware = MiddlewareConfig()

    ***REMOVED*** CORS Configuration - restrictive for auth service
    middleware.cors(
        origins=config.cors_origins,
        credentials=True,  ***REMOVED*** Required for auth cookies/tokens
        methods=["POST", "GET", "PUT", "OPTIONS"],  ***REMOVED*** Limited to auth operations
        headers=["Content-Type", "Authorization", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
        max_age=300,  ***REMOVED*** Short cache for auth endpoints (5 minutes)
    )

    ***REMOVED*** Enhanced Security Headers for auth service
    if config.is_production:
        middleware.security_headers(
            hsts=True,  ***REMOVED*** Force HTTPS in production
            hsts_max_age=31536000,  ***REMOVED*** 1 year
            hsts_include_subdomains=True,
            frame_options="DENY",  ***REMOVED*** Prevent iframe attacks
            content_type_options=True,
            xss_protection=True,  ***REMOVED*** XSS prevention
            csp="default-src 'self'",  ***REMOVED*** Strict content policy
            referrer_policy="strict-origin-when-cross-origin",
            trusted_hosts=config.allowed_hosts,
        )
    else:
        ***REMOVED*** More permissive settings for development
        middleware.security_headers(
            hsts=False,  ***REMOVED*** No HSTS in development
            frame_options="SAMEORIGIN",  ***REMOVED*** Allow same origin iframes
            content_type_options=True,
            xss_protection=True,
            csp="default-src 'self' 'unsafe-inline' 'unsafe-eval'",
            referrer_policy="strict-origin-when-cross-origin",
        )

    ***REMOVED*** Auth-Specific Rate Limiting
    rate_limit_config = {
        "/auth/tokens": "10/minute",  ***REMOVED*** Login attempts
        "/auth/users": "5/minute",  ***REMOVED*** Registration attempts
        "/auth/tokens/verify": "100/minute",  ***REMOVED*** Token verification (used by BFF)
        "/health": "60/minute",  ***REMOVED*** Health checks
        "/meta": "60/minute",  ***REMOVED*** Meta endpoints
    }

    middleware.rate_limiting(
        default_limit="100/minute",
        endpoints=rate_limit_config,
        exempt_ips=["127.0.0.1", "::1"]
        + (["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"] if not config.is_production else []),
        headers=True,  ***REMOVED*** Include rate limit headers
        key_func="ip",  ***REMOVED*** Rate limit by IP address
    )

    ***REMOVED*** Configure logging for Auth API
    log_level = "INFO" if config.is_production else "DEBUG"
    middleware.logging(
        level=log_level,
        include_request_body=not config.is_production,  ***REMOVED*** Only log bodies in development
        include_response_body=False,  ***REMOVED*** Don't log sensitive auth responses
        max_body_size=1024,  ***REMOVED*** Smaller for auth requests
        exclude_paths=["/health", "/docs", "/openapi.json", "/favicon.ico"],
        include_headers=True,
        exclude_headers=["authorization", "cookie", "x-api-key"],  ***REMOVED*** Don't log sensitive headers
        log_timing=True,
        log_user_agent=not config.is_production,
    )

    ***REMOVED*** Request Processing
    middleware.request_processing(
        include_request_id=True,  ***REMOVED*** Track requests with correlation IDs
        include_process_time=True,  ***REMOVED*** Add processing time headers
        gzip_compression=True,  ***REMOVED*** Compress responses
        gzip_minimum_size=500,  ***REMOVED*** Only compress larger responses
        max_request_size=1024 * 1024,  ***REMOVED*** 1MB limit for auth requests
        timeout=30,  ***REMOVED*** Auth operations should be fast
    )

    ***REMOVED*** Configure metrics middleware for Auth API monitoring
    if getattr(config, "enable_metrics", True):  ***REMOVED*** Default to enabled
        middleware.metrics(
            endpoint_path="/metrics",
            include_endpoint=True,
            exclude_paths=["/health", "/metrics", "/docs", "/openapi.json", "/favicon.ico"],
            exclude_methods=["OPTIONS"],
            custom_buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
            track_request_size=True,
            track_response_size=True,
            enabled=True,
        )
        logger.info("Metrics middleware enabled for Auth API monitoring")

    logger.info(f"Auth middleware configured for {config.environment} environment")
    return middleware


def create_auth_app(config: Optional[AuthAPIConfig] = None) -> FastAPI:
    """Create Auth API application using fast-core with enhanced middleware.

    Args:
        config: Auth API configuration (creates default if None)

    Returns:
        Configured FastAPI application
    """
    ***REMOVED*** Create or use provided configuration
    if config is None:
        from auth_api.config.app import settings

        config = settings

    logger.info("Creating Auth API application with fast-core and enhanced middleware")

    ***REMOVED*** Create Auth-specific middleware configuration
    middleware_config = create_auth_middleware_config(config)

    ***REMOVED*** Define routers for the application
    routers = [
        meta_router,
        health_router,
        api_v1_router,  ***REMOVED*** V1 API routes with built-in prefix
    ]

    ***REMOVED*** Create app options
    app_options = AppOptions(
        exception_handlers=True,
        health_checks=True,  ***REMOVED*** Always enable health checks for auth service
        docs=config.debug,
    )

    ***REMOVED*** Create FastAPI app using fast-core
    app = create_app(
        settings=config,
        title="Next Watch Authentication API",
        description="Dedicated authentication service for Next Watch movie platform",
        version="0.1.0",
        options=app_options,
        middleware=middleware_config,
        routers=routers,
        lifespan=auth_lifespan,
    )

    ***REMOVED*** All routers now have their prefixes built-in, no manual configuration needed

    logger.info("Auth API application created with fast-core integration")
    return app


def get_auth_app() -> FastAPI:
    """Get Auth API application instance.

    Returns:
        FastAPI application instance
    """
    return create_auth_app()
