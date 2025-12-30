"""Fast-Core application factory for ML API.

This module creates a FastAPI application using the fast-core library
with ML-specific configuration and dependencies.
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from config.logging import get_logger
from fast_core import AppOptions, create_app
from fast_core.middleware import MiddlewareConfig
from fastapi import FastAPI

from ml_api.config.app import MLAPIConfig
from ml_api.config.fast_core_config import create_fast_core_config
from ml_api.routes.embeddings import router as embeddings_router

# Add ML meta configuration constants after imports
ML_FEATURES = [
    "Movie embedding generation and similarity",
    "Vector similarity search and matching",
    "Batch embedding processing for large datasets",
    "Pre-trained ML model serving and inference",
    "Real-time embedding computation",
    "Model health monitoring and diagnostics",
    "GPU-accelerated ML operations",
    "API rate limiting and resource management",
]

ML_ENDPOINTS = {
    "/embeddings": "Generate embeddings for movies or text",
    "/embeddings/batch": "Batch embedding generation for datasets",
    "/embeddings/similarity": "Calculate similarity between embeddings",
    "/models/info": "Information about loaded ML models",
    "/models/health": "ML model health and status check",
    "/ping": "Simple health ping endpoint",
}

logger = get_logger(__name__)


def _setup_health_check_system(app: FastAPI, settings: Any) -> None:
    """Initialize the fast-core multi-endpoint health check system."""
    from fast_core.monitoring import setup_kubernetes_health_checks

    from ml_api.services.health_service import setup_ml_health_checks

    registry = setup_kubernetes_health_checks(app, settings)
    setup_ml_health_checks(registry)


def _load_embedding_model(app: FastAPI, ml_config: MLAPIConfig) -> None:
    """Load embedding model and attach service to app state if enabled."""
    if not ml_config.enable_embeddings:
        return

    from ml_api.services import embedding_service

    logger.info("Loading embedding model...")
    embedding_service.load_model()
    logger.info("Embedding model loaded successfully")
    app.state.embedding_service = embedding_service


def _setup_metrics(app: FastAPI) -> None:
    """Initialize global and ML-specific metrics and attach to app state."""
    from fast_core.monitoring.metrics import initialize_metrics

    from ml_api.core.metrics import initialize_ml_metrics

    initialize_metrics("ml-api")
    logger.info("Global metrics registry initialized for service: ml-api")

    metrics_instance = initialize_ml_metrics()
    if metrics_instance:
        logger.info("ML metrics initialized successfully")
        app.state.metrics = metrics_instance
    else:
        logger.warning("ML metrics initialization returned None - metrics registry not available")


@asynccontextmanager
async def ml_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for ML API.

    Handles startup and shutdown events for the ML API application.
    """
    # Startup
    logger.info("Starting ML API application")
    settings = app.state.settings
    ml_config = app.state.ml_config

    # Log configuration summary
    logger.info(f"ML API starting on {settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")

    # Setup new multi-endpoint health checks
    try:
        _setup_health_check_system(app, settings)
        logger.info("Multi-endpoint health check system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize health check system: {e}", exc_info=True)

    # Initialize ML model if enabled
    try:
        _load_embedding_model(app, ml_config)
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        if ml_config.is_production:
            # In production, we want to know about model loading failures
            raise
        logger.warning("Continuing with mock embeddings in development")

    # Initialize ML-specific metrics (always enabled for observability)
    try:
        _setup_metrics(app)
    except ImportError as e:
        logger.error(f"Metrics dependencies not installed: {e}")
        logger.info("Install prometheus-client to enable metrics: pip install prometheus-client")
    except Exception as e:
        logger.error(f"Failed to initialize ML metrics: {e}", exc_info=True)
        if ml_config.is_production:
            # In production, we want to know about metrics failures
            raise

    yield

    # Shutdown
    logger.info("Shutting down ML API application")

    # Clean up ML resources
    try:
        if hasattr(app.state, "embedding_service"):
            logger.info("Cleaning up embedding service resources")
            # Add any cleanup logic here if needed
    except Exception as e:
        logger.error(f"Error during ML resource cleanup: {e}")


def create_ml_middleware_config(config: MLAPIConfig) -> MiddlewareConfig:
    """Create ML-specific middleware configuration using the Middleware Builder.

    Args:
        config: ML API configuration

    Returns:
        Configured middleware with ML-specific settings
    """
    middleware = MiddlewareConfig()

    # Configure CORS for ML API (internal service)
    middleware.cors(
        origins=config.cors_origins,
        credentials=False,  # ML API typically doesn't need credentials
        methods=["GET", "POST", "OPTIONS"],
        headers=["Content-Type", "X-Requested-With", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
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

    # Configure rate limiting for ML API protection
    rate_limit_config = {
        # Embedding endpoints (more restrictive due to compute cost)
        "/embeddings": "100/minute",
        "/embeddings/batch": "20/minute",
        # Health endpoints (less restrictive)
        "/health": "1000/minute",
        "/health/model": "500/minute",
        "/ping": "1000/minute",
    }

    middleware.rate_limiting(
        default_limit="200/hour" if config.is_production else "500/hour",
        endpoints=rate_limit_config,
        exempt_ips=["127.0.0.1", "::1"]
        + (["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"] if not config.is_production else []),
        headers=True,  # Include rate limit headers for debugging
        key_func="ip",  # Rate limit by IP address
    )

    # Configure logging for ML API
    log_level = "INFO" if config.is_production else "DEBUG"
    middleware.logging(
        level=log_level,
        include_request_body=not config.is_production,  # Only log bodies in development
        include_response_body=False,  # Never log response bodies (too verbose)
        max_body_size=2048,
        exclude_paths=["/health", "/ping", "/docs", "/openapi.json", "/favicon.ico"],
        include_headers=True,
        exclude_headers=["authorization", "x-api-key", "internal-api-key"],
        log_timing=True,
        log_user_agent=not config.is_production,  # Only in development
    )

    # Configure request processing for ML API
    middleware.request_processing(
        max_request_size=5 * 1024 * 1024,  # 5MB for batch embedding requests
        timeout=120,  # ML operations can take longer
        include_request_id=True,
        request_id_header="X-Request-ID",
        include_process_time=True,
        process_time_header="X-Process-Time",
        gzip_compression=True,
        gzip_minimum_size=1000,
    )

    # Configure Prometheus metrics for ML monitoring
    middleware.metrics(
        endpoint_path="/metrics",
        include_endpoint=True,
        exclude_paths=["/health", "/ping", "/docs", "/openapi.json", "/favicon.ico"],
        exclude_methods=["OPTIONS"],
        custom_buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0],
        track_request_size=True,
        track_response_size=True,
        enabled=True,  # Always enable metrics for production observability
    )

    # CRITICAL: Always enable context middleware for request ID correlation
    # This ensures logs and traces have consistent request IDs for debugging
    middleware.context(
        service_name=config.service_name,
        auto_generate_request_id=True,
        extract_user_id=False,  # ML API doesn't typically handle user auth
        trace_propagation=config.enable_tracing,  # Enable trace propagation if tracing is on
        include_w3c_trace_context=True,
        include_b3_headers=True,
        include_jaeger_headers=True,
        enabled=True,  # Always enabled for request correlation
    )

    return middleware


def create_ml_app(config: Optional[MLAPIConfig] = None) -> FastAPI:
    """Create ML API application using fast-core.

    Args:
        config: ML API configuration (optional, will create default if not provided)

    Returns:
        Configured FastAPI application
    """
    # Use provided config or create default
    if config is None:
        from ml_api.config.app import get_ml_settings

        config = get_ml_settings()

    # Convert to fast-core config
    fast_core_config = create_fast_core_config(config)

    # Create middleware configuration
    middleware_config = create_ml_middleware_config(config)

    # Define routers for the application
    routers = [
        # health_router,  # Removed: Using new multi-endpoint health system
        embeddings_router,
    ]

    # Create app options with enhanced meta endpoint configuration
    app_options = AppOptions(
        exception_handlers=True,
        health_checks=False,  # CRITICAL: Disable to prevent conflicts
        docs=True,
        meta_endpoints=True,  # ✅ Enable auto-setup with static config
        meta_features=ML_FEATURES,
        meta_endpoints_map=ML_ENDPOINTS,
    )

    # Create the FastAPI app using fast-core
    app = create_app(
        settings=fast_core_config,
        title="ML API",
        description="Machine Learning API for Next Watch platform",
        version="1.0.0",
        options=app_options,
        middleware=middleware_config,
        routers=routers,
        lifespan=ml_lifespan,
    )

    # Store configurations in app state for access in lifespan and routes
    app.state.settings = fast_core_config
    app.state.ml_config = config

    # Meta endpoints are now automatically configured with ML-specific data
    logger.info("ML API meta endpoints configured automatically with static config")
    logger.info("ML API application created successfully with fast-core")
    return app


def get_ml_app() -> FastAPI:
    """Get ML API application instance.

    Returns:
        ML API FastAPI application
    """
    return create_ml_app()
