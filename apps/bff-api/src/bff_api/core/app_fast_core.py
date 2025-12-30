"""Fast-Core application factory for BFF API.

This module creates a FastAPI application using the fast-core library
with BFF-specific configuration and dependencies.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from config.logging import get_logger
from fast_core import AppOptions, create_app
from fast_core.middleware import MiddlewareConfig
from fastapi import FastAPI

from bff_api.config.app import BFFAPIConfig
from bff_api.config.fast_core_config import create_fast_core_config
from bff_api.dependencies import cleanup_service_clients, get_all_services_health
from bff_api.routes.api_v1 import api_v1_router
from bff_api.services.health_service import close_health_service

# Add BFF meta configuration constants after imports
BFF_FEATURES = [
    "Movie search and discovery",
    "User authentication and session management",
    "Personalized recommendations aggregation",
    "Multi-service data orchestration",
    "Frontend-optimized response formatting",
    "Real-time notifications and updates",
    "Caching and performance optimization",
    "API rate limiting and security",
]

BFF_ENDPOINTS = {
    "/bff/v1/movies": "Movie catalog with aggregated data",
    "/bff/v1/movies/{id}": "Movie details with recommendations",
    "/bff/v1/movies/{id}/similar": "Similar movies suggestions",
    "/bff/v1/search": "Unified search across all services",
    "/bff/v1/sidebar": "Sidebar widget data aggregation",
    "/bff/v1/auth/login": "User authentication endpoint",
    "/bff/v1/auth/register": "User registration endpoint",
    "/bff/v1/auth/profile": "User profile management",
    "/bff/v1/recommendations": "Personalized movie recommendations",
    "/bff/v1/notifications": "Real-time user notifications",
}


logger = get_logger(__name__)


@asynccontextmanager
async def bff_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for BFF API.

    Handles startup and shutdown events for the BFF API application.
    Now uses Service Client Factory for better lifecycle management.
    """
    # Startup
    logger.info("Starting BFF API application with Service Client Factory")
    settings = app.state.settings
    bff_config = app.state.bff_config

    # Log configuration summary
    logger.info(f"BFF API starting on {settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")

    # Legacy health service removed - now using Health Registry only

    # Setup new multi-endpoint health checks
    try:
        from fast_core.monitoring import setup_kubernetes_health_checks

        from bff_api.services.health_service import setup_bff_health_checks

        registry = setup_kubernetes_health_checks(app, settings)
        setup_bff_health_checks(registry)
        logger.info("Multi-endpoint health check system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize health check system: {e}", exc_info=True)

    # Initialize BFF-specific metrics (always enabled for observability)
    try:
        # First initialize the global metrics registry
        from fast_core.monitoring.metrics import initialize_metrics

        from bff_api.core.metrics import initialize_bff_metrics

        # Initialize global metrics registry with service name
        initialize_metrics("bff-api")
        logger.info("Global metrics registry initialized for service: bff-api")

        # Now initialize BFF-specific metrics
        metrics_instance = initialize_bff_metrics()
        if metrics_instance:
            logger.info("BFF metrics initialized successfully")
            app.state.metrics = metrics_instance
        else:
            logger.warning(
                "BFF metrics initialization returned None - metrics registry not available"
            )
    except ImportError as e:
        logger.error(f"Metrics dependencies not installed: {e}")
        logger.info("Install prometheus-client to enable metrics: pip install prometheus-client")
    except Exception as e:
        logger.error(f"Failed to initialize BFF metrics: {e}", exc_info=True)
        if bff_config.is_production:
            # In production, we want to know about metrics failures
            raise

    # Test service connections on startup
    if settings.debug:
        logger.debug("Testing service connections with Service Client Factory...")
        try:
            # Get health status for all registered services
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

    # Shutdown
    logger.info("Shutting down BFF API application")

    # Clean up health service
    try:
        await close_health_service()
        logger.info("Health service cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during health service cleanup: {e}")

    # Clean up all service clients managed by Service Client Factory
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

    # Configure CORS for BFF (frontend-facing API)
    middleware.cors(
        origins=config.cors_origins,
        credentials=True,  # BFF needs credentials for frontend auth
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        headers=["Content-Type", "Authorization", "X-Requested-With", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Process-Time", "X-Cache-Status"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )

    # Configure security headers for production
    if config.is_production:
        middleware.security_headers(
            hsts=True,
            hsts_max_age=63072000,  # 2 years
            hsts_include_subdomains=True,
            frame_options="DENY",  # Prevent iframe embedding
            content_type_options=True,
            xss_protection=True,
            csp="default-src 'self'; connect-src 'self' https://*.example.com; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'",
            referrer_policy="strict-origin-when-cross-origin",
            trusted_hosts=config.allowed_hosts,
        )
    else:
        # Development security headers (more permissive)
        middleware.security_headers(
            hsts=False,  # No HSTS in development
            frame_options="SAMEORIGIN",
            content_type_options=True,
            xss_protection=True,
            referrer_policy="strict-origin-when-cross-origin",
        )

    # Configure rate limiting for BFF protection
    rate_limit_config = {
        # General API rate limiting
        "/bff/v1/movies": "200/minute",
        "/bff/v1/movies/{movie_id}": "300/minute",
        "/bff/v1/sidebar": "100/minute",
        "/bff/v1/search": "50/minute",
        # Auth-related endpoints (more restrictive)
        "/bff/v1/auth/login": "10/minute",
        "/bff/v1/auth/register": "5/minute",
        "/bff/v1/auth/refresh": "30/minute",
        # Demo endpoints for testing middleware
        "/bff/v1/middleware-demo": "100/minute",
        "/bff/v1/rate-limit-test": "50/minute",
        # Health and meta endpoints (less restrictive)
        "/health": "1000/minute",
        "/meta": "1000/minute",
    }

    middleware.rate_limiting(
        default_limit="500/hour" if config.is_production else "1000/hour",
        endpoints=rate_limit_config,
        exempt_ips=["127.0.0.1", "::1"]
        + (["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"] if not config.is_production else []),
        headers=True,  # Include rate limit headers for debugging
        key_func="ip",  # Rate limit by IP address
    )

    # Configure logging for BFF
    log_level = "INFO" if config.is_production else "DEBUG"
    middleware.logging(
        level=log_level,
        include_request_body=not config.is_production,  # Only log bodies in development
        include_response_body=False,  # Never log response bodies (too verbose)
        max_body_size=2048,
        exclude_paths=["/health", "/docs", "/openapi.json", "/favicon.ico"],
        include_headers=True,
        exclude_headers=["authorization", "cookie", "x-api-key", "internal-api-key"],
        log_timing=True,
        log_user_agent=not config.is_production,  # Only in development
    )

    # Configure request processing for BFF
    middleware.request_processing(
        max_request_size=10 * 1024 * 1024,  # 10MB for file uploads
        timeout=60,  # BFF might aggregate multiple services
        include_request_id=True,
        request_id_header="X-Request-ID",
        include_process_time=True,
        process_time_header="X-Process-Time",
        gzip_compression=True,
        gzip_minimum_size=1000,
    )

    # Configure Prometheus metrics for BFF monitoring
    middleware.metrics(
        endpoint_path="/metrics",
        include_endpoint=True,
        exclude_paths=["/health", "/docs", "/openapi.json", "/favicon.ico"],
        exclude_methods=["OPTIONS"],
        track_request_size=True,
        track_response_size=True,
        enabled=True,  # Always enable metrics for production observability
    )

    logger.info(f"BFF middleware configured for {config.environment} environment")
    return middleware


def create_bff_app(config: BFFAPIConfig | None = None) -> FastAPI:
    """Create BFF API application using fast-core with enhanced middleware.

    Args:
        config: BFF API configuration (creates default if None)

    Returns:
        Configured FastAPI application
    """
    # Create or use provided configuration
    if config is None:
        config = BFFAPIConfig()

    logger.info("Creating BFF API application with fast-core and enhanced middleware")

    # Convert BFF config to fast-core config
    fast_core_config = create_fast_core_config(config)

    # Create BFF-specific middleware configuration
    middleware_config = create_bff_middleware_config(config)

    # Define routers for the application
    routers = [
        # health_router,  # Removed: Using new multi-endpoint health system
        api_v1_router,
    ]

    # Create app options with enhanced meta endpoint configuration
    app_options = AppOptions(
        exception_handlers=True,
        health_checks=False,  # CRITICAL: Disable to prevent conflicts
        docs=config.debug,
        meta_endpoints=True,  # ✅ Enable auto-setup with static config
        meta_features=BFF_FEATURES,
        meta_endpoints_map=BFF_ENDPOINTS,
    )

    # Create the FastAPI app using fast-core with enhanced middleware
    app = create_app(
        settings=fast_core_config,
        title="BFF API",
        description="Backend for Frontend API - Orchestrates calls to multiple services with enhanced middleware",
        version="1.0.0",
        options=app_options,
        middleware=middleware_config,  # Use the new Middleware Builder
        routers=routers,
        lifespan=bff_lifespan,
    )

    # Store the original BFF config for backward compatibility
    app.state.bff_config = config

    # Meta endpoints are now automatically configured with BFF-specific data
    logger.info("BFF API meta endpoints configured automatically with static config")
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


# Export the main functions
__all__ = [
    "create_bff_app",
    "get_bff_app",
    "bff_lifespan",
    "create_bff_middleware_config",
]
