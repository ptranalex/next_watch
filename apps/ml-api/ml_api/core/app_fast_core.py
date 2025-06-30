"""Fast-Core application factory for ML API.

This module creates a FastAPI application using the fast-core library
with ML-specific configuration and dependencies.
"""

from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fast_core import create_app, AppOptions
from fast_core.middleware import MiddlewareConfig

from ml_api.config.app import MLAPIConfig
from ml_api.config.fast_core_config import create_fast_core_config
from config.logging import get_logger

***REMOVED*** Import ML routes
from ml_api.routes.embeddings import router as embeddings_router  ***REMOVED*** type: ignore
from ml_api.routes.health import router as health_router  ***REMOVED*** type: ignore

logger = get_logger(__name__)


@asynccontextmanager
async def ml_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for ML API.

    Handles startup and shutdown events for the ML API application.
    """
    ***REMOVED*** Startup
    logger.info("Starting ML API application")
    settings = app.state.settings
    ml_config = app.state.ml_config

    ***REMOVED*** Log configuration summary
    logger.info(f"ML API starting on {settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")

    ***REMOVED*** Initialize ML model if enabled
    if ml_config.enable_embeddings:
        try:
            from ml_api.services import embedding_service  ***REMOVED*** type: ignore

            logger.info("Loading embedding model...")
            embedding_service.load_model()
            logger.info("Embedding model loaded successfully")

            ***REMOVED*** Store service in app state for access
            app.state.embedding_service = embedding_service
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            if ml_config.is_production:
                ***REMOVED*** In production, we want to know about model loading failures
                raise
            else:
                logger.warning("Continuing with mock embeddings in development")

    ***REMOVED*** Initialize ML-specific metrics (always enabled for observability)
    try:
        from ml_api.core.metrics import initialize_ml_metrics

        metrics_instance = initialize_ml_metrics()
        if metrics_instance:
            logger.info("ML metrics initialized successfully")
            app.state.metrics = metrics_instance
        else:
            logger.warning(
                "ML metrics initialization returned None - metrics registry not available"
            )
    except ImportError as e:
        logger.error(f"Metrics dependencies not installed: {e}")
        logger.info("Install prometheus-client to enable metrics: pip install prometheus-client")
    except Exception as e:
        logger.error(f"Failed to initialize ML metrics: {e}", exc_info=True)
        if ml_config.is_production:
            ***REMOVED*** In production, we want to know about metrics failures
            raise

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down ML API application")

    ***REMOVED*** Clean up ML resources
    try:
        if hasattr(app.state, "embedding_service"):
            logger.info("Cleaning up embedding service resources")
            ***REMOVED*** Add any cleanup logic here if needed
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

    ***REMOVED*** Configure CORS for ML API (internal service)
    middleware.cors(
        origins=config.cors_origins,
        credentials=False,  ***REMOVED*** ML API typically doesn't need credentials
        methods=["GET", "POST", "OPTIONS"],
        headers=["Content-Type", "X-Requested-With", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
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

    ***REMOVED*** Configure rate limiting for ML API protection
    rate_limit_config = {
        ***REMOVED*** Embedding endpoints (more restrictive due to compute cost)
        "/embeddings": "100/minute",
        "/embeddings/batch": "20/minute",
        ***REMOVED*** Health endpoints (less restrictive)
        "/health": "1000/minute",
        "/health/model": "500/minute",
        "/ping": "1000/minute",
    }

    middleware.rate_limiting(
        default_limit="200/hour" if config.is_production else "500/hour",
        endpoints=rate_limit_config,
        exempt_ips=["127.0.0.1", "::1"]
        + (["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"] if not config.is_production else []),
        headers=True,  ***REMOVED*** Include rate limit headers for debugging
        key_func="ip",  ***REMOVED*** Rate limit by IP address
    )

    ***REMOVED*** Configure logging for ML API
    log_level = "INFO" if config.is_production else "DEBUG"
    middleware.logging(
        level=log_level,
        include_request_body=not config.is_production,  ***REMOVED*** Only log bodies in development
        include_response_body=False,  ***REMOVED*** Never log response bodies (too verbose)
        max_body_size=2048,
        exclude_paths=["/health", "/ping", "/docs", "/openapi.json", "/favicon.ico"],
        include_headers=True,
        exclude_headers=["authorization", "x-api-key", "internal-api-key"],
        log_timing=True,
        log_user_agent=not config.is_production,  ***REMOVED*** Only in development
    )

    ***REMOVED*** Configure request processing for ML API
    middleware.request_processing(
        max_request_size=5 * 1024 * 1024,  ***REMOVED*** 5MB for batch embedding requests
        timeout=120,  ***REMOVED*** ML operations can take longer
        include_request_id=True,
        request_id_header="X-Request-ID",
        include_process_time=True,
        process_time_header="X-Process-Time",
        gzip_compression=True,
        gzip_minimum_size=1000,
    )

    ***REMOVED*** Configure Prometheus metrics for ML monitoring
    middleware.metrics(
        endpoint_path="/metrics",
        include_endpoint=True,
        exclude_paths=["/health", "/ping", "/docs", "/openapi.json", "/favicon.ico"],
        exclude_methods=["OPTIONS"],
        custom_buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0],
        track_request_size=True,
        track_response_size=True,
        enabled=True,  ***REMOVED*** Always enable metrics for production observability
    )

    return middleware


def create_ml_app(config: Optional[MLAPIConfig] = None) -> FastAPI:
    """Create ML API application using fast-core.

    Args:
        config: ML API configuration (optional, will create default if not provided)

    Returns:
        Configured FastAPI application
    """
    ***REMOVED*** Use provided config or create default
    if config is None:
        from ml_api.config.app import get_ml_settings

        config = get_ml_settings()

    ***REMOVED*** Convert to fast-core config
    fast_core_config = create_fast_core_config(config)

    ***REMOVED*** Create middleware configuration
    middleware_config = create_ml_middleware_config(config)

    ***REMOVED*** Create app using fast-core with ML-specific options
    app_options = AppOptions(
        title="ML API",
        description="Machine Learning API for Next Watch platform",
        version="1.0.0",
        lifespan=ml_lifespan,
        middleware=middleware_config,
    )

    app = create_app(config=fast_core_config, options=app_options)

    ***REMOVED*** Store configurations in app state for access in lifespan and routes
    app.state.settings = fast_core_config
    app.state.ml_config = config

    ***REMOVED*** Include routers
    app.include_router(health_router)  ***REMOVED*** Health endpoints at root level
    app.include_router(embeddings_router, prefix="/embeddings", tags=["embeddings"])

    logger.info("ML API application created successfully with fast-core")
    return app


def get_ml_app() -> FastAPI:
    """Get ML API application instance.

    Returns:
        ML API FastAPI application
    """
    return create_ml_app()
