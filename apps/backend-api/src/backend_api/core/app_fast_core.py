"""Fast-Core application factory for Backend API.

This module creates a FastAPI application using the fast-core library
with Backend-specific configuration and dependencies.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from config.logging import get_logger
from fast_core import AppOptions, create_app  # pyright: ignore[reportUnknownVariableType]
from fast_core.middleware import MiddlewareConfig
from fastapi import FastAPI

from backend_api.config.app import BackendAPIConfig
from backend_api.config.fast_core_config import create_fast_core_config
from backend_api.db.database import init_database

# Import Backend routes
from backend_api.routes.api_v1 import api_v1_router
from backend_api.services.health_service import close_health_service

logger = get_logger(__name__)

# Backend API focuses on core movie data operations

# Simple meta configuration constants
BACKEND_FEATURES: list[str] = [
    "Movie search and browsing",
    "User authentication and profiles",
    "Personalized recommendations",
    "Rating and review system",
    "Watchlist management",
    "Social features and interactions",
    "Bulk data operations",
    "Advanced movie filtering",
]

BACKEND_ENDPOINTS: dict[str, str] = {
    "/api/v1/movies": "Movie catalog browsing and search",
    "/api/v1/movies/{id}": "Individual movie details",
    "/api/v1/movies/{id}/cast": "Movie cast and crew information",
    "/api/v1/movies/{id}/trailers": "Movie trailers and media",
    "/api/v1/movies/search": "Advanced movie search with filters",
    "/api/v1/movies/bulk": "Bulk movie data operations",
    "/api/v1/user/movies": "User movie interactions and preferences",
    "/api/v1/user/movies/{id}": "User-specific movie data",
    "/db-health": "Legacy database health check",
}


@asynccontextmanager
async def backend_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for Backend API.

    Handles startup and shutdown events for the Backend API application.
    Uses Service Client Factory for better lifecycle management.
    """
    # Startup
    logger.info("Starting Backend API application with Fast Core integration")
    settings = app.state.settings

    # Log configuration summary
    logger.info(f"Backend API starting on {settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")

    # Initialize database
    logger.info("Initializing database connection")
    try:
        init_database()
        logger.info("Database connection established successfully")
        if hasattr(settings, "get_database_url_masked"):
            logger.debug(f"Database configuration: {settings.get_database_url_masked()}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    # Legacy health service removed - now using Health Registry only

    # Setup new multi-endpoint health checks
    try:
        from fast_core.monitoring import setup_kubernetes_health_checks

        from backend_api.services.health_service import setup_backend_health_checks

        registry = setup_kubernetes_health_checks(app, settings)
        setup_backend_health_checks(registry)
        logger.info("Multi-endpoint health check system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize health check system: {e}", exc_info=True)

    # Backend API focuses on core movie data - no suggestion engine needed
    logger.info("Backend API handles core movie data operations")

    # Initialize Backend-specific metrics (always enabled for observability)
    backend_config = app.state.settings
    try:
        # First initialize the global metrics registry
        from fast_core.monitoring.metrics import initialize_metrics

        from backend_api.core.metrics import initialize_backend_metrics

        # Initialize global metrics registry with service name
        initialize_metrics("backend-api")
        logger.info("Global metrics registry initialized for service: backend-api")

        # Now initialize Backend-specific metrics
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
            # In production, we want to know about metrics failures
            raise

    # Backend API is independent - no external service registrations needed
    logger.info("Backend API runs independently without external service dependencies")

    yield

    # Shutdown
    logger.info("Shutting down Backend API application")

    # Shutdown health service
    if hasattr(app.state, "health_service") and app.state.health_service is not None:
        try:
            logger.info("Shutting down health service")
            app.state.health_service.close()
            logger.info("Health service shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down health service: {e}")

    # No suggestion engine to shutdown - Backend API is focused on core data

    # Close global health service
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

    # Configure CORS for Backend API (serves frontend and other services)
    middleware.cors(
        origins=config.cors_origins,
        credentials=True,  # Backend needs credentials for auth
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

    # Configure rate limiting for Backend API protection
    rate_limit_config = {
        # Core movie data endpoints
        "/api/v1/movies": "300/minute",
        "/api/v1/movies/{movie_id}": "500/minute",
        "/api/v1/movies/search": "100/minute",
        "/api/v1/movies/bulk": "500/minute",
        "/api/v1/movies/{movie_id}/cast": "200/minute",
        "/api/v1/movies/{movie_id}/trailers": "200/minute",
        # User interaction endpoints (managed by BFF auth)
        "/api/v1/user/movies": "200/minute",
        "/api/v1/user/movies/{movie_id}": "100/minute",
        # Health and meta endpoints (less restrictive)
        "/health": "1000/minute",
        "/meta": "1000/minute",
    }

    middleware.rate_limiting(
        default_limit="1000/hour" if config.is_production else "2000/hour",
        endpoints=rate_limit_config,
        exempt_ips=["127.0.0.1", "::1"]
        + (["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"] if not config.is_production else []),
        headers=True,  # Include rate limit headers for debugging
        key_func="ip",  # Rate limit by IP address
    )

    # Configure logging for Backend API
    log_level = "INFO" if config.is_production else "DEBUG"
    middleware.logging(
        level=log_level,
        include_request_body=not config.is_production,  # Only log bodies in development
        include_response_body=False,  # Never log response bodies (too verbose)
        max_body_size=2048,
        exclude_additional=[
            "/docs",
            "/openapi.json",
            "/favicon.ico",
        ],  # Add to defaults
        include_headers=True,
        exclude_headers=["authorization", "cookie", "x-api-key", "internal-api-key"],
        log_timing=True,
        log_user_agent=not config.is_production,  # Only in development
    )

    # Configure request processing for Backend API
    middleware.request_processing(
        max_request_size=10 * 1024 * 1024,  # 10MB for file uploads
        timeout=60,  # Backend might handle complex queries
        include_request_id=True,
        request_id_header="X-Request-ID",
        include_process_time=True,
        process_time_header="X-Process-Time",
        gzip_compression=True,
        gzip_minimum_size=1000,
    )

    # Configure Prometheus metrics for Backend monitoring
    middleware.metrics(
        endpoint_path="/metrics",
        include_endpoint=True,
        exclude_additional=["/favicon.ico"],  # Only favicon.ico (docs/openapi already in defaults)
        exclude_methods=["OPTIONS"],
        track_request_size=True,
        track_response_size=True,
        enabled=True,  # Always enable metrics for production observability
    )

    # Note: Context middleware is automatically enabled when tracing is configured
    # No need for manual middleware.context() call - fast-core handles this automatically
    # based on the enable_tracing setting in the configuration

    logger.info(
        f"Backend middleware configured for {config.environment} environment with automatic tracing"
    )
    return middleware


def create_backend_app(config: BackendAPIConfig | None = None) -> FastAPI:
    """Create Backend API application using fast-core with enhanced middleware.

    Args:
        config: Backend API configuration (creates default if None)

    Returns:
        Configured FastAPI application
    """
    # Create or use provided configuration
    if config is None:
        from backend_api.config.app import settings

        config = settings

    logger.info("Creating Backend API application with fast-core and enhanced middleware")

    # Convert Backend config to fast-core config
    fast_core_config = create_fast_core_config(config)

    # Create Backend-specific middleware configuration
    middleware_config = create_backend_middleware_config(config)

    # Define routers for the application
    routers = [
        # health_router,  # Removed: Using new multi-endpoint health system
        api_v1_router,
    ]

    # Create app options with simple configuration-based meta endpoints
    app_options = AppOptions(
        exception_handlers=True,
        health_checks=False,  # CRITICAL: Disable to prevent conflicts
        docs=config.debug,
        meta_endpoints=True,  # ✅ Enable auto-setup with static config
        meta_features=BACKEND_FEATURES,
        meta_endpoints_map=BACKEND_ENDPOINTS,
        # No complex debug provider needed - fast-core provides sensible defaults
    )

    # Create FastAPI app using fast-core with automatic meta endpoint setup
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

    # Meta endpoints are now automatically configured with simple static configuration
    logger.info("Backend API meta endpoints configured automatically with static config")

    logger.info("Backend API application created with fast-core integration")
    return app


def get_backend_app() -> FastAPI:
    """Get Backend API application instance.

    Returns:
        FastAPI application instance
    """
    return create_backend_app()
