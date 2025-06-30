"""Fast-Core configuration adapter for BFF API.

This module provides utilities to convert BFF API configuration to fast-core
compatible configuration using the enhanced FastAPIConfig.
"""

from typing import Optional
from fast_core import FastAPIConfig
from bff_api.config.app import BFFAPIConfig
from config.logging import get_logger

logger = get_logger(__name__)


def create_fast_core_config(bff_config: BFFAPIConfig) -> FastAPIConfig:
    """Convert BFF API configuration to fast-core configuration.

    Args:
        bff_config: BFF API configuration instance

    Returns:
        FastAPIConfig instance with BFF-specific settings
    """
    logger.info("Converting BFF config to fast-core config")

    ***REMOVED*** Create fast-core config using enhanced configuration
    fast_core_config = FastAPIConfig(
        ***REMOVED*** Basic service configuration (inherited from ServiceConfig)
        service_name=bff_config.service_name,
        environment=bff_config.environment,
        debug=bff_config.debug,
        host=bff_config.host,
        port=bff_config.port,
        log_level=bff_config.log_level,
        ***REMOVED*** CORS configuration
        cors_origins=bff_config.cors_origins,
        cors_allow_credentials=True,
        cors_allow_methods=["*"],
        cors_allow_headers=["*"],
        ***REMOVED*** Service URLs for external services (filter out None values)
        service_urls={
            k: v
            for k, v in {
                "backend": bff_config.backend_api_url,
                "auth": bff_config.auth_api_url,
                "recommendation": bff_config.reco_api_url,
                "ml": bff_config.ml_api_url,
            }.items()
            if v is not None
        },
        ***REMOVED*** Service timeouts
        service_timeouts={
            "backend": bff_config.backend_api_timeout,
            "auth": bff_config.auth_api_timeout,
            "recommendation": bff_config.recommendation_api_timeout,
            "ml": bff_config.ml_api_timeout,
        },
        ***REMOVED*** Feature flags
        feature_flags={
            "recommendations": bff_config.enable_recommendations,
            "ml_features": bff_config.enable_ml_features,
            "auth_service": bff_config.enable_auth_service,
            "performance_metrics": bff_config.enable_performance_metrics,
            "metrics": True,  ***REMOVED*** Always enabled for production observability
            "cache_metrics": bff_config.cache_enable_metrics,
        },
        ***REMOVED*** FastAPI-specific configuration
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    logger.info("Fast-core config created successfully")
    return fast_core_config


def get_service_url(config: FastAPIConfig, service_name: str) -> Optional[str]:
    """Get service URL from fast-core config.

    Args:
        config: Fast-core configuration
        service_name: Name of the service (backend, auth, recommendation, ml)

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
