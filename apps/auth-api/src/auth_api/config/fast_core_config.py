"""Fast-Core configuration adapter for Auth API.

This module provides utilities to convert Auth API configuration to fast-core
compatible configuration using the enhanced FastAPIConfig.
"""

from typing import Optional
from fast_core import FastAPIConfig
from auth_api.config.app import AuthAPIConfig
from config.logging import get_logger

logger = get_logger(__name__)


def create_fast_core_config(auth_config: AuthAPIConfig) -> FastAPIConfig:
    """Convert Auth API configuration to fast-core configuration.

    Args:
        auth_config: Auth API configuration instance

    Returns:
        FastAPIConfig instance with auth-specific settings
    """
    logger.info("Converting Auth config to fast-core config")

    ***REMOVED*** Create fast-core config using enhanced configuration
    fast_core_config = FastAPIConfig(
        ***REMOVED*** Basic service configuration (inherited from ServiceConfig)
        service_name=getattr(auth_config, "service_name", "Next Watch Authentication API"),
        environment=auth_config.environment,
        debug=auth_config.debug,
        host=auth_config.host,
        port=auth_config.port,
        log_level=auth_config.log_level,
        ***REMOVED*** CORS configuration - restrictive for auth service
        cors_origins=getattr(auth_config, "cors_origins", ["*"]),
        cors_allow_credentials=True,  ***REMOVED*** Required for auth cookies/tokens
        cors_allow_methods=["POST", "GET", "OPTIONS"],  ***REMOVED*** Limited to auth operations
        cors_allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
        ***REMOVED*** No external service URLs - auth API is independent
        service_urls={},
        ***REMOVED*** No external service timeouts needed
        service_timeouts={
            "default": 30,
        },
        ***REMOVED*** Feature flags for auth API functionality
        feature_flags={
            "jwt_validation": True,
            "refresh_tokens": True,
            "password_reset": auth_config.enable_password_reset,
            "user_registration": auth_config.enable_user_registration,
            "session_management": auth_config.enable_session_management,
            "two_factor_auth": False,  ***REMOVED*** Future feature
            "social_login": False,  ***REMOVED*** Future feature
            "health_checks": True,
            "performance_metrics": auth_config.auth_performance_metrics,
        },
        ***REMOVED*** FastAPI-specific configuration
        docs_url="/docs" if auth_config.debug else None,
        redoc_url="/redoc" if auth_config.debug else None,
        openapi_url="/openapi.json" if auth_config.debug else None,
    )

    ***REMOVED*** Set monitoring configuration (MonitoringConfigMixin fields)
    ***REMOVED*** Note: Pydantic doesn't support mixin fields in constructor, so we set them post-creation
    fast_core_config.enable_tracing = auth_config.enable_tracing
    fast_core_config.tracing_endpoint = auth_config.tracing_endpoint
    fast_core_config.tracing_sample_rate = auth_config.tracing_sample_rate
    fast_core_config.enable_performance_metrics = auth_config.enable_performance_metrics
    fast_core_config.enable_deep_health_checks = auth_config.enable_deep_health_checks
    fast_core_config.enable_error_tracking = auth_config.enable_error_tracking

    logger.info("Fast-core config created successfully")
    return fast_core_config


def get_service_url(config: FastAPIConfig, service_name: str) -> Optional[str]:
    """Get service URL from fast-core config.

    Args:
        config: Fast-core configuration
        service_name: Name of the service (backend, recommendation, ml)

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
