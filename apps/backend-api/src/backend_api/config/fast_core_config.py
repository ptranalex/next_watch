"""Fast-Core configuration adapter for Backend API.

This module provides utilities to convert Backend API configuration to fast-core
compatible configuration using the enhanced FastAPIConfig.
"""

from typing import Optional

from config.logging import get_logger
from fast_core import FastAPIConfig

from backend_api.config.app import BackendAPIConfig

logger = get_logger(__name__)


def create_fast_core_config(backend_config: BackendAPIConfig) -> FastAPIConfig:
    """Convert Backend API config to fast-core FastAPIConfig.

    Args:
        backend_config: Backend API configuration

    Returns:
        FastAPIConfig: Fast-core compatible configuration
    """
    logger.info("Converting Backend API config to fast-core config")

    # Create fast-core config with backend-specific settings
    fast_core_config = FastAPIConfig(
        # Basic service configuration (inherited from ServiceConfig)
        service_name=getattr(backend_config, "service_name", "Next Watch Backend API"),
        environment=backend_config.environment,
        debug=backend_config.debug,
        host=backend_config.host,
        port=backend_config.port,
        log_level=backend_config.log_level,
        # CORS configuration - backend API serves frontend and other services
        cors_origins=getattr(backend_config, "cors_origins", ["*"]),
        cors_allow_credentials=True,
        cors_allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        cors_allow_headers=["*"],
        # No external service URLs - backend API is independent
        service_urls={},
        # No external service timeouts needed
        service_timeouts={
            "default": 30,
        },
        # Feature flags for backend API functionality
        feature_flags={
            "health_checks": True,
            "user_interactions": True,
            "advanced_search": True,
            "movie_details": True,
            "cast_information": True,
            "movie_trailers": True,
            "bulk_operations": True,
        },
        # FastAPI-specific configuration
        docs_url="/docs" if backend_config.debug else None,
        redoc_url="/redoc" if backend_config.debug else None,
        openapi_url="/openapi.json" if backend_config.debug else None,
    )

    # Set monitoring configuration (MonitoringConfigMixin fields)
    # Note: Pydantic doesn't support mixin fields in constructor, so we set them post-creation
    fast_core_config.enable_tracing = backend_config.enable_tracing
    fast_core_config.tracing_endpoint = backend_config.tracing_endpoint
    fast_core_config.tracing_sample_rate = backend_config.tracing_sample_rate
    fast_core_config.enable_performance_metrics = backend_config.enable_performance_metrics
    fast_core_config.enable_deep_health_checks = backend_config.enable_deep_health_checks
    fast_core_config.enable_error_tracking = backend_config.enable_error_tracking

    logger.info("Fast-core config created successfully")
    return fast_core_config


def get_service_url(config: FastAPIConfig, service_name: str) -> Optional[str]:
    """Get service URL from fast-core config.

    Args:
        config: Fast-core configuration
        service_name: Name of the service (auth, recommendation, ml)

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
