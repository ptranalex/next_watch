"""Fast-Core configuration adapter for ML API.

This module provides utilities to convert ML API configuration to fast-core
compatible configuration using the enhanced FastAPIConfig.
"""

from typing import Optional
from fast_core import FastAPIConfig
from ml_api.config.app import MLAPIConfig
from config.logging import get_logger

logger = get_logger(__name__)


def create_fast_core_config(ml_config: MLAPIConfig) -> FastAPIConfig:
    """Convert ML API configuration to fast-core configuration.

    Args:
        ml_config: ML API configuration instance

    Returns:
        FastAPIConfig instance with ML-specific settings
    """
    logger.info("Converting ML config to fast-core config")

    ***REMOVED*** Create fast-core config using enhanced configuration
    fast_core_config = FastAPIConfig(
        ***REMOVED*** Basic service configuration (inherited from ServiceConfig)
        service_name=ml_config.service_name,
        environment=ml_config.environment,
        debug=ml_config.debug,
        host=ml_config.host,
        port=ml_config.port,
        log_level=ml_config.log_level,
        ***REMOVED*** CORS configuration
        cors_origins=ml_config.cors_origins,
        cors_allow_credentials=True,
        cors_allow_methods=["*"],
        cors_allow_headers=["*"],
        ***REMOVED*** Feature flags
        feature_flags={
            "embeddings": ml_config.enable_embeddings,
            "batch_processing": ml_config.enable_batch_processing,
            "model_caching": ml_config.enable_model_caching,
            "metrics": True,  ***REMOVED*** Always enabled for production observability
        },
        ***REMOVED*** FastAPI-specific configuration
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

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
