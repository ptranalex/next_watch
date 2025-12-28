"""Fast-Core application factory for Recommendation API.

This module creates a FastAPI application using the fast-core library
with recommendation-specific configuration and dependencies.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from config.logging import get_logger
from fast_core import AppOptions, create_app
from fast_core.middleware import MiddlewareConfig
from fastapi import FastAPI

from recommendation_api.config.app import RecommendationAPIConfig
from recommendation_api.config.fast_core_config import create_fast_core_config

***REMOVED*** Add Recommendation meta configuration constants after imports
RECOMMENDATION_FEATURES = [
    "ML-powered personalized movie recommendations",
    "Similar movies discovery and suggestions",
    "Trending and popular content algorithms",
    "User preference learning and adaptation",
    "Real-time recommendation caching",
    "Vector similarity and embedding search",
    "Content-based and collaborative filtering",
    "A/B testing and recommendation experiments",
]

RECOMMENDATION_ENDPOINTS = {
    "/api/v1/recommendations/trending": "Trending movies and popular content",
    "/api/v1/recommendations/popular": "Most popular movies across platform",
    "/api/v1/recommendations/similar/{movie_id}": "Movies similar to given movie",
    "/api/v1/recommendations/personalized/{user_id}": "Personalized recommendations for user",
    "/api/v1/recommendations/categories": "Recommendations by genre/category",
    "/api/v1/recommendations/analytics": "Recommendation performance analytics",
    "/api/v1/recommendations/feedback": "User feedback collection endpoint",
}

***REMOVED*** Import recommendation routes

***REMOVED*** from recommendation_api.routes import api_v1_router  ***REMOVED*** Move this import to avoid circular dependency

logger = get_logger(__name__)


@asynccontextmanager
async def recommendation_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Recommendation API lifespan manager with service-specific startup/shutdown.

    Args:
        app: FastAPI application instance

    Yields:
        None: Application runs between startup and shutdown
    """
    ***REMOVED*** Startup
    logger.info("Starting Recommendation API service with fast-core", service="recommendation-api")

    ***REMOVED*** Get settings from app state
    settings = getattr(app.state, "settings", None)

    ***REMOVED*** Setup new multi-endpoint health checks
    try:
        from fast_core.monitoring import setup_kubernetes_health_checks

        from recommendation_api.services.health_service import setup_recommendation_health_checks

        registry = setup_kubernetes_health_checks(app, settings)
        setup_recommendation_health_checks(registry)
        logger.info("Multi-endpoint health check system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize health check system: {e}", exc_info=True)

    ***REMOVED*** Initialize recommendation-specific services
    try:
        ***REMOVED*** Initialize Recommendation-specific metrics (always enabled for observability)
        try:
            ***REMOVED*** First initialize the global metrics registry
            from fast_core.monitoring.metrics import initialize_metrics

            from recommendation_api.core.metrics import initialize_recommendation_metrics

            ***REMOVED*** Initialize global metrics registry with service name
            initialize_metrics("recommendation-api")
            logger.info("Global metrics registry initialized for service: recommendation-api")

            ***REMOVED*** Now initialize Recommendation-specific metrics
            metrics_instance = initialize_recommendation_metrics()
            if metrics_instance:
                logger.info("Recommendation metrics initialized successfully")
                app.state.metrics = metrics_instance
            else:
                logger.warning(
                    "Recommendation metrics initialization returned None - metrics registry not available"
                )
        except ImportError as e:
            logger.error(f"Metrics dependencies not installed: {e}")
            logger.info(
                "Install prometheus-client to enable metrics: pip install prometheus-client"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Recommendation metrics: {e}", exc_info=True)
            if settings and getattr(settings, "is_production", False):
                ***REMOVED*** In production, we want to know about metrics failures
                raise

        ***REMOVED*** Initialize cache service if enabled
        config = getattr(app.state, "settings", None)
        if config and getattr(config, "enable_caching", True):
            logger.info("Initializing cache service", service="recommendation-api")
            from recommendation_api.services.cache_service import get_cache_service

            cache_service = get_cache_service()
            is_healthy = await cache_service.health_check()
            logger.info(
                "Cache service initialized", service="recommendation-api", healthy=is_healthy
            )

        ***REMOVED*** Initialize vector service
        logger.info("Initializing vector service", service="recommendation-api")
        from recommendation_api.services.vector_service import get_vector_service

        get_vector_service()
        logger.info("Vector service initialized", service="recommendation-api")

        ***REMOVED*** Initialize backend client
        logger.info("Initializing backend client", service="recommendation-api")
        from recommendation_api.services.backend_client import get_backend_client

        get_backend_client()
        logger.info("Backend client initialized", service="recommendation-api")

        ***REMOVED*** Initialize movie adapter
        logger.info("Initializing movie adapter", service="recommendation-api")
        from recommendation_api.services.movie_adapter import get_movie_adapter

        get_movie_adapter()
        logger.info("Movie adapter initialized", service="recommendation-api")

        logger.info(
            "All recommendation services initialized successfully", service="recommendation-api"
        )

    except Exception as e:
        logger.error(
            "Failed to initialize recommendation services",
            service="recommendation-api",
            error=str(e),
        )
        raise

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down Recommendation API service", service="recommendation-api")

    try:
        ***REMOVED*** Close recommendation-specific services
        from recommendation_api.services.backend_client import close_backend_client
        from recommendation_api.services.cache_service import close_cache_service
        from recommendation_api.services.vector_service import close_vector_service

        await close_cache_service()
        await close_vector_service()
        await close_backend_client()

        logger.info("Recommendation services closed successfully", service="recommendation-api")

    except Exception as e:
        logger.error(
            "Error during recommendation service shutdown",
            service="recommendation-api",
            error=str(e),
        )


def create_recommendation_middleware_config(config: RecommendationAPIConfig) -> MiddlewareConfig:
    """Create recommendation-specific middleware configuration.

    Args:
        config: Recommendation API configuration

    Returns:
        Configured MiddlewareConfig instance
    """
    logger.info("Creating recommendation-specific middleware configuration")

    middleware = MiddlewareConfig()

    ***REMOVED*** CORS - recommendations API is often accessed from web frontends
    cors_origins = ["*"] if config.environment == "development" else []
    middleware.cors(
        origins=cors_origins,
        credentials=True,
        methods=["GET", "POST", "OPTIONS"],
        headers=["*"],
    )

    ***REMOVED*** Security headers
    middleware.security_headers(
        hsts=config.environment == "production",
        csp="default-src 'self'" if config.environment == "production" else None,
        frame_options="DENY",
        content_type_options=True,
        xss_protection=True,
    )

    ***REMOVED*** Rate limiting - protect against abuse
    rate_limits = {
        "/api/v1/recommendations/trending": "60/minute",  ***REMOVED*** Popular endpoints
        "/api/v1/recommendations/popular": "60/minute",
        "/api/v1/recommendations/similar/*": "30/minute",  ***REMOVED*** More expensive operations
        "/api/v1/recommendations/personalized/*": "20/minute",  ***REMOVED*** Most expensive
    }

    middleware.rate_limiting(
        default_limit="100/minute",
        endpoints=rate_limits,
        storage_url=config.redis_url if config.enable_caching else None,
    )

    ***REMOVED*** Request logging - env-aware level; never log bodies
    log_level = "INFO" if config.is_production else "DEBUG"
    middleware.logging(
        level=log_level,
        exclude_additional=["/docs", "/redoc", "/openapi.json"],  ***REMOVED*** Add to defaults
        include_request_body=False,  ***REMOVED*** Never log request bodies
        include_response_body=False,  ***REMOVED*** Never log response bodies
        max_body_size=1024,
    )

    ***REMOVED*** Request processing - important for recommendation APIs
    middleware.request_processing(
        max_request_size=1024 * 1024,  ***REMOVED*** 1MB - recommendations don't need large payloads
        timeout=config.request_timeout_seconds,
        include_request_id=True,
        request_id_header="X-Request-ID",
        include_process_time=True,
        process_time_header="X-Process-Time",
        gzip_compression=True,
        gzip_minimum_size=1000,  ***REMOVED*** Compress recommendation lists
    )

    ***REMOVED*** Configure metrics middleware for Recommendation API monitoring
    middleware.metrics(
        endpoint_path="/metrics",
        include_endpoint=True,
        exclude_additional=["/favicon.ico"],  ***REMOVED*** Add to standard excludes
        exclude_methods=["OPTIONS"],
        custom_buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
        track_request_size=True,
        track_response_size=True,
        enabled=True,  ***REMOVED*** Always enable metrics for production observability
    )
    logger.info("Metrics middleware enabled for Recommendation API monitoring")

    logger.info("Recommendation middleware configuration created")
    return middleware


def create_recommendation_app(config: RecommendationAPIConfig | None = None) -> FastAPI:
    """Create Recommendation API application using fast-core with enhanced middleware.

    Args:
        config: Recommendation API configuration (creates default if None)

    Returns:
        Configured FastAPI application
    """
    ***REMOVED*** Create or use provided configuration
    if config is None:
        config = RecommendationAPIConfig()

    logger.info("Creating Recommendation API application with fast-core and enhanced middleware")

    ***REMOVED*** Convert recommendation config to fast-core config
    fast_core_config = create_fast_core_config(config)

    ***REMOVED*** Create recommendation-specific middleware configuration
    middleware_config = create_recommendation_middleware_config(config)

    ***REMOVED*** Create app options with enhanced meta endpoint configuration
    app_options = AppOptions(
        exception_handlers=True,
        health_checks=False,  ***REMOVED*** CRITICAL: Disable to prevent conflicts
        docs=True,
        meta_endpoints=True,  ***REMOVED*** ✅ Enable auto-setup with static config
        meta_features=RECOMMENDATION_FEATURES,
        meta_endpoints_map=RECOMMENDATION_ENDPOINTS,
    )

    ***REMOVED*** Create the FastAPI app using fast-core with enhanced middleware
    app = create_app(
        settings=fast_core_config,
        title="Recommendation API",
        description="Movie recommendation service for Next Watch platform with ML-powered suggestions",
        version="1.0.0",
        options=app_options,
        middleware=middleware_config,  ***REMOVED*** Use the new Middleware Builder
        routers=[],  ***REMOVED*** We'll add routers manually with proper configuration
        lifespan=recommendation_lifespan,
    )

    ***REMOVED*** Add routers with their specific configuration
    ***REMOVED*** app.include_router(health_router, tags=["health"])  ***REMOVED*** Removed: Using new multi-endpoint health system
    from recommendation_api.routes import api_v1_router

    app.include_router(api_v1_router, prefix="/reco", tags=["reco-v1"])

    ***REMOVED*** Store the original recommendation config for backward compatibility
    app.state.reco_config = config

    ***REMOVED*** Meta endpoints are now automatically configured with Recommendation-specific data
    logger.info("Recommendation API meta endpoints configured automatically with static config")
    logger.info("Recommendation API application created successfully with enhanced middleware")
    return app


def get_recommendation_app() -> FastAPI:
    """Get Recommendation API application instance.

    This is a convenience function for getting the application instance
    with default configuration.

    Returns:
        Configured FastAPI application
    """
    return create_recommendation_app()


***REMOVED*** Export the main functions
__all__ = [
    "create_recommendation_app",
    "get_recommendation_app",
    "recommendation_lifespan",
    "create_recommendation_middleware_config",
]
