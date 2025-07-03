"""Fast-Core configuration adapter for Recommendation API.

This module provides utilities to convert Recommendation API configuration to fast-core
compatible configuration using the enhanced FastAPIConfig.
"""

from typing import Optional
from fast_core import FastAPIConfig
from recommendation_api.config.app import RecommendationAPIConfig
from config.logging import get_logger

logger = get_logger(__name__)


def create_fast_core_config(reco_config: RecommendationAPIConfig) -> FastAPIConfig:
    """Convert Recommendation API configuration to fast-core configuration.

    Args:
        reco_config: Recommendation API configuration instance

    Returns:
        FastAPIConfig instance with recommendation-specific settings
    """
    logger.info("Converting Recommendation config to fast-core config")

    ***REMOVED*** Create fast-core config using enhanced configuration
    fast_core_config = FastAPIConfig(
        ***REMOVED*** Basic service configuration (inherited from ServiceConfig)
        service_name=reco_config.service_name,
        environment=reco_config.environment,
        debug=reco_config.debug,
        host=reco_config.host,
        port=reco_config.port,
        log_level=reco_config.log_level,
        ***REMOVED*** CORS configuration - recommendations API is public-facing
        cors_origins=["*"] if reco_config.environment == "development" else [],
        cors_allow_credentials=True,
        cors_allow_methods=["GET", "POST", "OPTIONS"],
        cors_allow_headers=["*"],
        ***REMOVED*** Service URLs for external services (filter out None values)
        service_urls={
            k: v
            for k, v in {
                "backend": reco_config.backend_api_url,
                "ml": reco_config.ml_api_url,
                "qdrant": reco_config.qdrant_url,
                "redis": reco_config.redis_url,
            }.items()
            if v is not None
        },
        ***REMOVED*** Service timeouts
        service_timeouts={
            "backend": reco_config.backend_api_timeout,
            "ml": reco_config.ml_api_timeout,
            "default": reco_config.request_timeout_seconds,
        },
        ***REMOVED*** Feature flags
        feature_flags={
            "collaborative_filtering": reco_config.enable_collaborative_filtering,
            "content_filtering": reco_config.enable_content_filtering,
            "trending_fallback": reco_config.enable_trending_fallback,
            "diversity_boost": reco_config.enable_diversity_boost,
            "caching": reco_config.enable_caching,
            "metrics": True,  ***REMOVED*** Always enabled for production observability
            "precompute_similarities": reco_config.precompute_similarities,
        },
        ***REMOVED*** Cache configuration
        cache_ttl=reco_config.cache_ttl_default,
        cache_prefix=reco_config.cache_key_prefix,
        ***REMOVED*** FastAPI-specific configuration
        docs_url="/docs" if reco_config.debug else None,
        redoc_url="/redoc" if reco_config.debug else None,
        openapi_url="/openapi.json" if reco_config.debug else None,
        ***REMOVED*** Security settings
        trusted_hosts=["*"] if reco_config.environment == "development" else ["localhost"],
    )

    ***REMOVED*** Set monitoring configuration (MonitoringConfigMixin fields)
    ***REMOVED*** Note: Pydantic doesn't support mixin fields in constructor, so we set them post-creation
    fast_core_config.enable_tracing = reco_config.enable_tracing
    fast_core_config.tracing_endpoint = reco_config.tracing_endpoint
    fast_core_config.tracing_sample_rate = reco_config.tracing_sample_rate
    fast_core_config.enable_performance_metrics = reco_config.enable_performance_metrics
    fast_core_config.enable_deep_health_checks = reco_config.enable_deep_health_checks
    fast_core_config.enable_error_tracking = reco_config.enable_error_tracking

    logger.info("Fast-core config created successfully")
    return fast_core_config


def get_service_url(config: FastAPIConfig, service_name: str) -> Optional[str]:
    """Get service URL from fast-core config.

    Args:
        config: Fast-core configuration
        service_name: Name of the service (backend, ml, qdrant, redis)

    Returns:
        Service URL or None if not configured
    """
    return config.get_service_url(service_name)


def get_service_timeout(config: FastAPIConfig, service_name: str) -> int:
    """Get service timeout from fast-core config.

    Args:
        config: Fast-core configuration
        service_name: Name of the service

    Returns:
        Timeout in seconds (default 30)
    """
    return config.get_service_timeout(service_name)


def is_feature_enabled(config: FastAPIConfig, feature_name: str) -> bool:
    """Check if a feature is enabled in fast-core config.

    Args:
        config: Fast-core configuration
        feature_name: Name of the feature

    Returns:
        True if feature is enabled, False otherwise
    """
    return config.is_feature_enabled(feature_name)
