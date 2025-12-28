"""Fast-Core configuration adapter for Search API.

This module converts SearchAPIConfig to FastAPIConfig for use with fast-core.
"""

from config.logging import get_logger
from fast_core.config import FastAPIConfig

from search_api.config.app import SearchAPIConfig

logger = get_logger(__name__)


def create_fast_core_config(search_config: SearchAPIConfig) -> FastAPIConfig:
    """Convert Search API config to fast-core FastAPIConfig.

    Args:
        search_config: Search API configuration

    Returns:
        FastAPIConfig: Fast-core compatible configuration
    """
    logger.info("Converting Search API config to fast-core config")

    ***REMOVED*** Create fast-core config with Search-specific settings
    fast_core_config = FastAPIConfig(
        ***REMOVED*** Basic service configuration (inherited from ServiceConfig)
        service_name=search_config.service_name,
        environment=search_config.environment,
        debug=search_config.debug,
        host=search_config.host,
        port=search_config.port,
        log_level=search_config.log_level,
        ***REMOVED*** CORS configuration
        cors_origins=search_config.cors_origins,
        cors_allow_credentials=True,
        cors_allow_methods=["*"],
        cors_allow_headers=["*"],
        ***REMOVED*** Service URLs for external services (filter out None values)
        service_urls={
            k: v
            for k, v in {
                "backend": search_config.backend_api_url,
                "ml": search_config.ml_api_url,
            }.items()
            if v is not None
        },
        ***REMOVED*** Service timeouts
        service_timeouts={
            "backend": search_config.backend_api_timeout,
            "ml": search_config.ml_api_timeout,
        },
        ***REMOVED*** Feature flags for search functionality
        feature_flags={
            "vector_search": True,
            "fuzzy_search": True,
            "search_analytics": True,
            "search_suggestions": True,
            "performance_metrics": search_config.enable_performance_metrics,
        },
        ***REMOVED*** FastAPI-specific configuration
        docs_url="/docs" if search_config.debug else None,
        redoc_url="/redoc" if search_config.debug else None,
        openapi_url="/openapi.json" if search_config.debug else None,
    )

    ***REMOVED*** Set monitoring configuration (MonitoringConfigMixin fields)
    ***REMOVED*** Note: Pydantic doesn't support mixin fields in constructor, so we set them post-creation
    fast_core_config.enable_tracing = search_config.enable_tracing
    fast_core_config.tracing_endpoint = search_config.tracing_endpoint
    fast_core_config.tracing_sample_rate = search_config.tracing_sample_rate
    fast_core_config.enable_performance_metrics = search_config.enable_performance_metrics
    fast_core_config.enable_deep_health_checks = search_config.enable_deep_health_checks
    fast_core_config.enable_error_tracking = search_config.enable_error_tracking

    logger.info("Fast-core config created successfully")
    return fast_core_config
