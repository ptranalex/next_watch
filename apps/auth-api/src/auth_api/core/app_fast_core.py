"""Fast-Core application factory for Auth API.

This module creates a FastAPI application using the fast-core library
with Auth-specific configuration and dependencies.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from config.logging import get_logger
from fast_core import AppOptions, create_app
from fast_core.middleware import MiddlewareConfig
from fastapi import FastAPI

from auth_api.config.app import AuthAPIConfig
from auth_api.db.database import init_database

logger = get_logger(__name__)

# Add Auth meta configuration constants after imports
AUTH_FEATURES = [
    "JWT token-based authentication",
    "User registration and profile management",
    "Secure password hashing and validation",
    "Token verification and validation services",
    "Role-based access control (RBAC)",
    "Session management and lifecycle",
    "Security audit logging and monitoring",
    "API rate limiting and brute force protection",
]

AUTH_ENDPOINTS = {
    "/auth/tokens": "User authentication and login",
    "/auth/users": "User registration and management",
    "/auth/tokens/verify": "Token verification for other services",
    "/auth/tokens/refresh": "Token refresh and renewal",
    "/auth/users/{user_id}": "User profile management",
    "/auth/users/{user_id}/password": "Password change and reset",
    "/auth/health": "Authentication service health check",
}

# Import Auth routes

# Remove the router import from module level to avoid circular imports
# from auth_api.routes.api_v1 import api_v1_router


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
    # Startup
    logger.info("Starting Next Watch Authentication Service with Fast Core")
    settings = app.state.settings

    # Log configuration summary
    logger.info(f"Auth API starting on {settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")

    # Initialize Auth-specific metrics (always enabled for observability)
    try:
        # First initialize the global metrics registry
        from fast_core.monitoring.metrics import initialize_metrics

        from auth_api.core.metrics import initialize_auth_metrics

        # Initialize global metrics registry with service name
        _ = initialize_metrics("auth-api")
        logger.info("Global metrics registry initialized for service: auth-api")

        # Now initialize Auth-specific metrics
        metrics_instance = initialize_auth_metrics()
        if metrics_instance:
            logger.info("Auth metrics initialized successfully")
            app.state.metrics = metrics_instance
        else:
            logger.warning(
                "Auth metrics initialization returned None - metrics registry not available"
            )
    except ImportError as e:
        logger.error(f"Metrics dependencies not installed: {e}")
        logger.info("Install prometheus-client to enable metrics: pip install prometheus-client")
    except Exception as e:
        logger.error(f"Failed to initialize Auth metrics: {e}", exc_info=True)
        if settings.is_production:
            # In production, we want to know about metrics failures
            raise

    # Initialize database
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

        from auth_api.services.health_service import setup_auth_health_checks

        registry = setup_kubernetes_health_checks(app, settings)
        setup_auth_health_checks(registry)
        logger.info("Multi-endpoint health check system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize health check system: {e}", exc_info=True)

    logger.info("Auth API handles authentication and authorization for Next Watch platform")

    yield

    # Shutdown
    logger.info("Shutting down Next Watch Authentication Service")

    # Legacy health service cleanup removed - using Health Registry only

    logger.info("Auth API service shutdown complete")


def create_auth_middleware_config(config: AuthAPIConfig) -> MiddlewareConfig:
    """Create Auth API specific middleware configuration.

    Args:
        config: Auth API configuration

    Returns:
        MiddlewareConfig instance with auth-specific settings
    """
    middleware = MiddlewareConfig()

    # CORS Configuration - restrictive for auth service
    middleware.cors(
        origins=config.cors_origins,
        credentials=True,  # Required for auth cookies/tokens
        methods=["POST", "GET", "PUT", "OPTIONS"],  # Limited to auth operations
        headers=["Content-Type", "Authorization", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
        max_age=300,  # Short cache for auth endpoints (5 minutes)
    )

    # Enhanced Security Headers for auth service
    if config.is_production:
        middleware.security_headers(
            hsts=True,  # Force HTTPS in production
            hsts_max_age=31536000,  # 1 year
            hsts_include_subdomains=True,
            frame_options="DENY",  # Prevent iframe attacks
            content_type_options=True,
            xss_protection=True,  # XSS prevention
            csp="default-src 'self'",  # Strict content policy
            referrer_policy="strict-origin-when-cross-origin",
            trusted_hosts=config.allowed_hosts,
        )
    else:
        # More permissive settings for development
        middleware.security_headers(
            hsts=False,  # No HSTS in development
            frame_options="SAMEORIGIN",  # Allow same origin iframes
            content_type_options=True,
            xss_protection=True,
            csp="default-src 'self' 'unsafe-inline' 'unsafe-eval'",
            referrer_policy="strict-origin-when-cross-origin",
        )

    # Auth-Specific Rate Limiting
    rate_limit_config = {
        "/auth/tokens": "10/minute",  # Login attempts
        "/auth/users": "5/minute",  # Registration attempts
        "/auth/tokens/verify": "100/minute",  # Token verification (used by BFF)
        "/health": "60/minute",  # Health checks
        "/meta": "60/minute",  # Meta endpoints
    }

    middleware.rate_limiting(
        default_limit="100/minute",
        endpoints=rate_limit_config,
        exempt_ips=["127.0.0.1", "::1"]
        + (["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"] if not config.is_production else []),
        headers=True,  # Include rate limit headers
        key_func="ip",  # Rate limit by IP address
    )

    # Configure logging for Auth API - never log bodies due to sensitivity
    log_level = "INFO" if config.is_production else "DEBUG"
    middleware.logging(
        level=log_level,
        include_request_body=False,  # Never log request bodies
        include_response_body=False,  # Never log sensitive auth responses
        max_body_size=1024,
        exclude_additional=["/docs", "/openapi.json", "/favicon.ico"],
        include_headers=True,
        exclude_headers=["authorization", "cookie", "x-api-key"],
        log_timing=True,
        log_user_agent=not config.is_production,
    )

    # Request Processing
    middleware.request_processing(
        include_request_id=True,  # Track requests with correlation IDs
        include_process_time=True,  # Add processing time headers
        gzip_compression=True,  # Compress responses
        gzip_minimum_size=500,  # Only compress larger responses
        max_request_size=1024 * 1024,  # 1MB limit for auth requests
        timeout=30,  # Auth operations should be fast
    )

    # Configure metrics middleware for Auth API monitoring
    middleware.metrics(
        endpoint_path="/metrics",
        include_endpoint=True,
        exclude_additional=["/favicon.ico"],  # Only favicon.ico (docs/openapi already in defaults)
        exclude_methods=["OPTIONS"],
        custom_buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
        track_request_size=True,
        track_response_size=True,
        enabled=True,  # Always enable metrics for production observability
    )
    logger.info("Metrics middleware enabled for Auth API monitoring")

    logger.info(f"Auth middleware configured for {config.environment} environment")
    return middleware


def create_auth_app(config: AuthAPIConfig | None = None) -> FastAPI:
    """Create Auth API application using fast-core with enhanced middleware.

    Args:
        config: Auth API configuration (creates default if None)

    Returns:
        Configured FastAPI application
    """
    # Create or use provided configuration
    if config is None:
        from auth_api.config.app import settings

        config = settings

    logger.info("Creating Auth API application with fast-core and enhanced middleware")

    # Create Auth-specific middleware configuration
    middleware_config = create_auth_middleware_config(config)

    # Import routers locally to avoid circular imports
    from auth_api.routes.api_v1 import api_v1_router

    # Define routers for the application
    routers = [
        # health_router,  # Removed: Using new multi-endpoint health system
        api_v1_router,  # V1 API routes with built-in prefix
    ]

    # Create app options with enhanced meta endpoint configuration
    app_options = AppOptions(
        exception_handlers=True,
        health_checks=False,  # CRITICAL: Disable to prevent conflicts
        docs=config.debug,
        meta_endpoints=True,  # ✅ Enable auto-setup with static config
        meta_features=AUTH_FEATURES,
        meta_endpoints_map=AUTH_ENDPOINTS,
    )

    # Create FastAPI app using fast-core
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

    # All routers now have their prefixes built-in, no manual configuration needed

    # Meta endpoints are now automatically configured with Auth-specific data
    logger.info("Auth API meta endpoints configured automatically with static config")
    logger.info("Auth API application created with fast-core integration")
    return app


def get_auth_app() -> FastAPI:
    """Get Auth API application instance.

    Returns:
        FastAPI application instance
    """
    return create_auth_app()
