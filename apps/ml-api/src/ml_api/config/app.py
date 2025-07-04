"""ML API service configuration.

Provides configuration for the ML API service using the simplified config library.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import Field, validator
from config.base.config import ServiceConfig
from config.logging import get_logger
from config.services.monitoring import MonitoringConfigMixin

***REMOVED*** Configure basic logging first for this module
logger = get_logger(__name__)


class MLAPIConfig(ServiceConfig, MonitoringConfigMixin):
    """ML API service configuration.

    Provides configuration for the ML API service with ML-specific features and monitoring support.
    """

    ***REMOVED*** Service identification
    service_name: str = Field(default="ml-api", description="Service name")
    port: int = Field(default=8000, description="Service port")

    ***REMOVED*** Logging configuration
    logs_dir: Optional[str] = Field(
        default=None, description="Directory for log files (None disables file logging)"
    )

    ***REMOVED*** ML-specific configuration
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2", description="Sentence transformer model name"
    )
    model_cache_dir: Optional[str] = Field(
        default=None, description="Directory for model cache (None uses default)"
    )
    max_batch_size: int = Field(default=32, description="Maximum batch size for embeddings")
    embeddings_db_path: Optional[str] = Field(
        default=None, description="Path to embeddings database"
    )

    ***REMOVED*** Feature flags
    enable_embeddings: bool = Field(default=True, description="Enable embedding features")
    enable_batch_processing: bool = Field(default=True, description="Enable batch processing")
    enable_model_caching: bool = Field(default=True, description="Enable model caching")

    class Config:
        """Pydantic configuration for environment handling."""

        env_prefix = ""  ***REMOVED*** Remove ML_ prefix requirement
        env_file = [".env", ".env.local"]
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    def __init__(self, **kwargs: Any) -> None:
        """Initialize ML API configuration."""
        ***REMOVED*** Initialize with Pydantic Settings (will auto-load .env files)
        super().__init__(**kwargs)

        ***REMOVED*** Apply shared security and logging patterns
        self.apply_production_security_overrides()
        self._apply_ml_specific_overrides()
        self.log_configuration_summary()
        self._log_ml_specific_summary()

    def _apply_ml_specific_overrides(self) -> None:
        """Apply ML-specific production overrides."""
        if not self.is_production:
            return

        ***REMOVED*** Disable file logging in production to avoid volume permission issues
        if self.logs_dir:
            logger.warning("File logging disabled in production to avoid volume permission issues")
            object.__setattr__(self, "logs_dir", None)

    def _log_ml_specific_summary(self) -> None:
        """Log ML-specific configuration details."""
        ***REMOVED*** Log ML configuration in compact format
        ml_config = {
            "model": self.embedding_model,
            "max_batch": self.max_batch_size,
            "cache_dir": self.model_cache_dir,
        }
        logger.info(f"ML Configuration: {ml_config}")

        ***REMOVED*** Log feature flags in compact format if any are disabled
        features = {
            "embeddings": self.enable_embeddings,
            "batch_processing": self.enable_batch_processing,
            "model_caching": self.enable_model_caching,
            "metrics": True,  ***REMOVED*** Always enabled for production observability
        }
        disabled_features = [k for k, v in features.items() if not v]
        if disabled_features:
            logger.info(f"Disabled features: {disabled_features}")

    @validator("max_batch_size")
    def validate_batch_size(cls, v: int) -> int:
        """Validate batch size is reasonable."""
        if v < 1:
            raise ValueError("Batch size must be at least 1")
        if v > 1000:
            raise ValueError("Batch size should not exceed 1000")
        return v

    @validator("model_cache_dir")
    def validate_cache_dir(cls, v: Optional[str]) -> Optional[str]:
        """Validate cache directory format."""
        if v is None:
            return None

        ***REMOVED*** Ensure it's a valid path
        try:
            Path(v)
        except Exception:
            raise ValueError("Invalid cache directory path")

        return v

    def validate_production_settings(self) -> List[str]:
        """Validate configuration for production deployment."""
        issues = []

        ***REMOVED*** Get validation from parent class (includes basic debug mode checks)
        issues.extend(super().validate_production_settings())

        ***REMOVED*** ML-specific production validations
        if self.is_production:
            ***REMOVED*** Warn about model caching in production
            if not self.enable_model_caching:
                issues.append("Model caching should be enabled in production for performance")

            ***REMOVED*** Check for reasonable batch size
            if self.max_batch_size > 100:
                issues.append("Large batch sizes (>100) may cause memory issues in production")

        return issues

    @property
    def model_cache_path(self) -> Optional[Path]:
        """Get model cache path as Path object."""
        if self.model_cache_dir:
            return Path(self.model_cache_dir)
        return None

    def __str__(self) -> str:
        """Return a comprehensive multi-line string representation."""
        return f"""ML API Configuration:
  Environment: {self.environment}
  Service: {self.service_name}
  
  HTTP Service:
    Host: {self.host}
    Port: {self.port}
    Debug: {self.debug}
    CORS Origins: {', '.join(self.cors_origins)}
    Allowed Hosts: {', '.join(self.allowed_hosts)}

  ML Configuration:
    Embedding Model: {self.embedding_model}
    Max Batch Size: {self.max_batch_size}
    Model Cache Dir: {self.model_cache_dir}
    Embeddings DB Path: {self.embeddings_db_path}

  Feature Flags:
    Embeddings: {self.enable_embeddings}
    Batch Processing: {self.enable_batch_processing}
    Model Caching: {self.enable_model_caching}
    Metrics: True (Always Enabled)

  Logging:
    Log Level: {self.log_level}
    Log Directory: {self.logs_dir}"""


***REMOVED*** Create settings instance using environment variable discovery
_cached_settings: Optional[MLAPIConfig] = None


def get_ml_settings() -> MLAPIConfig:
    """Get ML API settings instance (cached singleton).

    Returns:
        Cached MLAPIConfig instance to avoid re-initialization
    """
    global _cached_settings
    if _cached_settings is None:
        _cached_settings = MLAPIConfig()
    return _cached_settings


***REMOVED*** Default settings instance
settings = get_ml_settings()
