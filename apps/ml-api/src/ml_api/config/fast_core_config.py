"""Fast-Core configuration adapter for ML API.

This module provides utilities to convert ML API configuration to fast-core
compatible configuration using the enhanced FastAPIConfig.
"""

from config.logging import get_logger
from fast_core import FastAPIConfig

from ml_api.config.app import MLAPIConfig

logger = get_logger(__name__)


def create_fast_core_config(ml_config: MLAPIConfig) -> FastAPIConfig:
    """Convert ML API configuration to fast-core configuration.

    Args:
        ml_config: ML API configuration instance

    Returns:
        FastAPIConfig instance with ML-specific settings
    """
    logger.info("Converting ML config to fast-core config")

    # Create fast-core config using enhanced configuration
    fast_core_config = FastAPIConfig(
        # Basic service configuration (inherited from ServiceConfig)
        service_name=ml_config.service_name,
        environment=ml_config.environment,
        debug=ml_config.debug,
        host=ml_config.host,
        port=ml_config.port,
        log_level=ml_config.log_level,
        # CORS configuration
        cors_origins=ml_config.cors_origins,
        cors_allow_credentials=True,
        cors_allow_methods=["*"],
        cors_allow_headers=["*"],
        # No external service URLs - ML API is independent
        service_urls={},
        # No external service timeouts needed
        service_timeouts={
            "default": 30,
        },
        # Feature flags
        feature_flags={
            "embeddings": ml_config.enable_embeddings,
            "batch_processing": ml_config.enable_batch_processing,
            "model_caching": ml_config.enable_model_caching,
            "metrics": True,  # Always enabled for production observability
        },
        # FastAPI-specific configuration
        docs_url="/docs" if ml_config.debug else None,
        redoc_url="/redoc" if ml_config.debug else None,
        openapi_url="/openapi.json" if ml_config.debug else None,
    )

    # Set monitoring configuration (MonitoringConfigMixin fields)
    # Note: Pydantic doesn't support mixin fields in constructor, so we set them post-creation
    fast_core_config.enable_tracing = ml_config.enable_tracing
    fast_core_config.tracing_endpoint = ml_config.tracing_endpoint
    fast_core_config.tracing_sample_rate = ml_config.tracing_sample_rate
    fast_core_config.enable_performance_metrics = ml_config.enable_performance_metrics
    fast_core_config.enable_deep_health_checks = ml_config.enable_deep_health_checks
    fast_core_config.enable_error_tracking = ml_config.enable_error_tracking

    logger.info("Fast-core config created successfully")
    return fast_core_config


def is_feature_enabled(config: FastAPIConfig, feature_name: str) -> bool:
    """Check if a feature is enabled in fast-core config.

    Args:
        config: Fast-core configuration
        feature_name: Name of the feature

    Returns:
        True if feature is enabled, False otherwise
    """
    return config.is_feature_enabled(feature_name)
