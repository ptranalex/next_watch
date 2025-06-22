"""Fast-Core application factory for BFF API.

This module creates a FastAPI application using the fast-core library
with BFF-specific configuration and dependencies.
"""

from typing import List, Optional, AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fast_core import create_app, AppOptions
from fast_core.middleware import MiddlewareConfig

from bff_api.config.app import BFFAPIConfig
from bff_api.config.fast_core_config import create_fast_core_config
from bff_api.dependencies import cleanup_service_clients, get_all_services_health
from config.logging import get_logger

***REMOVED*** Import BFF routes
from bff_api.routes.health import router as health_router
from bff_api.routes.meta import router as meta_router
from bff_api.routes.api_v1 import api_v1_router

logger = get_logger(__name__)


@asynccontextmanager
async def bff_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for BFF API.

    Handles startup and shutdown events for the BFF API application.
    Now uses Service Client Factory for better lifecycle management.
    """
    ***REMOVED*** Startup
    logger.info("Starting BFF API application with Service Client Factory")
    settings = app.state.settings

    ***REMOVED*** Log configuration summary
    logger.info(f"BFF API starting on {settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")

    ***REMOVED*** Test service connections on startup
    if settings.debug:
        logger.debug("Testing service connections with Service Client Factory...")
        try:
            ***REMOVED*** Get health status for all registered services
            health_status = await get_all_services_health()
            for service_name, status in health_status.items():
                if status.get("status") == "healthy":
                    logger.debug(f"✓ {service_name}: {status.get('url')} - healthy")
                else:
                    logger.warning(
                        f"⚠ {service_name}: {status.get('url')} - {status.get('status')}"
                    )
        except Exception as e:
            logger.warning(f"Could not test service connections during startup: {e}")

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down BFF API application")

    ***REMOVED*** Clean up all service clients managed by Service Client Factory
    try:
        await cleanup_service_clients()
        logger.info("All service clients cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during service client cleanup: {e}")


def create_bff_middleware_config(config: BFFAPIConfig) -> MiddlewareConfig:
    """Create BFF-specific middleware configuration using the Middleware Builder.

    Args:
        config: BFF API configuration

    Returns:
        Configured middleware with BFF-specific settings
    """
    middleware = MiddlewareConfig()

    ***REMOVED*** Configure CORS for BFF (frontend-facing API)
    middleware.cors(
        origins=config.cors_origins,
        credentials=True,  ***REMOVED*** BFF needs credentials for frontend auth
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

    ***REMOVED*** Configure rate limiting for BFF protection
    rate_limit_config = {
        ***REMOVED*** General API rate limiting
        "/bff/v1/movies": "200/minute",
        "/bff/v1/movies/{movie_id}": "300/minute",
        "/bff/v1/sidebar": "100/minute",
        "/bff/v1/search": "50/minute",
        ***REMOVED*** Auth-related endpoints (more restrictive)
        "/bff/v1/auth/login": "10/minute",
        "/bff/v1/auth/register": "5/minute",
        "/bff/v1/auth/refresh": "30/minute",
        ***REMOVED*** Demo endpoints for testing middleware
        "/bff/v1/middleware-demo": "100/minute",
        "/bff/v1/rate-limit-test": "50/minute",
        ***REMOVED*** Health and meta endpoints (less restrictive)
        "/health": "1000/minute",
        "/meta": "1000/minute",
    }

    middleware.rate_limiting(
        default_limit="500/hour" if config.is_production else "1000/hour",
        endpoints=rate_limit_config,
        exempt_ips=["127.0.0.1", "::1"]
        + (["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"] if not config.is_production else []),
        headers=True,  ***REMOVED*** Include rate limit headers for debugging
        key_func="ip",  ***REMOVED*** Rate limit by IP address
    )

    ***REMOVED*** Configure logging for BFF
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

    ***REMOVED*** Configure request processing for BFF
    middleware.request_processing(
        max_request_size=10 * 1024 * 1024,  ***REMOVED*** 10MB for file uploads
        timeout=60,  ***REMOVED*** BFF might aggregate multiple services
        include_request_id=True,
        request_id_header="X-Request-ID",
        include_process_time=True,
        process_time_header="X-Process-Time",
        gzip_compression=True,
        gzip_minimum_size=1000,
    )

    logger.info(f"BFF middleware configured for {config.environment} environment")
    return middleware


def create_bff_app(config: Optional[BFFAPIConfig] = None) -> FastAPI:
    """Create BFF API application using fast-core with enhanced middleware.

    Args:
        config: BFF API configuration (creates default if None)

    Returns:
        Configured FastAPI application
    """
    ***REMOVED*** Create or use provided configuration
    if config is None:
        config = BFFAPIConfig()

    logger.info("Creating BFF API application with fast-core and enhanced middleware")

    ***REMOVED*** Convert BFF config to fast-core config
    fast_core_config = create_fast_core_config(config)

    ***REMOVED*** Create BFF-specific middleware configuration
    middleware_config = create_bff_middleware_config(config)

    ***REMOVED*** Define routers for the application
    routers = [
        meta_router,
        health_router,
        api_v1_router,
    ]

    ***REMOVED*** Create app options (disable middleware since we're using MiddlewareConfig)
    app_options = AppOptions(
        exception_handlers=True,
        health_checks=True,
        docs=True,
    )

    ***REMOVED*** Create the FastAPI app using fast-core with enhanced middleware
    app = create_app(
        settings=fast_core_config,
        title="BFF API",
        description="Backend for Frontend API - Orchestrates calls to multiple services with enhanced middleware",
        version="1.0.0",
        options=app_options,
        middleware=middleware_config,  ***REMOVED*** Use the new Middleware Builder
        routers=routers,
        lifespan=bff_lifespan,
    )

    ***REMOVED*** Store the original BFF config for backward compatibility
    app.state.bff_config = config

    logger.info("BFF API application created successfully with enhanced middleware")
    return app


def get_bff_app() -> FastAPI:
    """Get BFF API application instance.

    This is a convenience function for getting the application instance
    with default configuration.

    Returns:
        Configured FastAPI application
    """
    return create_bff_app()


***REMOVED*** Export the main functions
__all__ = ["create_bff_app", "get_bff_app", "bff_lifespan", "create_bff_middleware_config"]
