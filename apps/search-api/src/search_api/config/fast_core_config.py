"""Fast-Core configuration adapter for Search API.

This module converts SearchAPIConfig to FastAPIConfig for use with fast-core.
"""

from fast_core.config import FastAPIConfig
from search_api.config.app import SearchAPIConfig
from config.logging import get_logger

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
        ***REMOVED*** Feature flags
        feature_flags={
            "semantic_search": search_config.enable_semantic_search,
            "search_analytics": search_config.enable_search_analytics,
            "fuzzy_matching": search_config.enable_fuzzy_matching,
            "typo_tolerance": search_config.enable_typo_tolerance,
            "performance_metrics": search_config.enable_performance_metrics,
            "metrics": True,  ***REMOVED*** Always enabled for production observability
            "cache_metrics": search_config.cache_enable_metrics,
        },
        ***REMOVED*** FastAPI-specific configuration
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    logger.info("Fast-core config created successfully")
    return fast_core_config
