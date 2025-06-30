"""Configuration settings for the Recommendation API service using the config library."""

from typing import List, Optional, Dict, Any

from pydantic import Field, validator, computed_field
from config.base.config import ServiceConfig
from config.services.cache import CacheConfigMixin
from config.services.vector import VectorDBConfigMixin
from config.profiles.service_profiles import apply_profiles

from config.logging import get_logger

***REMOVED*** Configure basic logging first for this module
logger = get_logger(__name__)


class RecommendationAPIConfig(ServiceConfig, CacheConfigMixin, VectorDBConfigMixin):
    """Recommendation API service configuration.

    Provides configuration for the Recommendation API service with cache and vector DB support.
    """

    ***REMOVED*** Service identification
    service_name: str = Field(default="recommendation-api", description="Service name")
    port: int = Field(default=8002, description="Service port")

    ***REMOVED*** Logging configuration
    logs_dir: Optional[str] = Field(
        default=None, description="Directory for log files (None disables file logging)"
    )

    ***REMOVED*** Environment configuration
    environment: str = Field(
        default="development",
        description="Deployment environment (development, staging, production)",
    )

    ***REMOVED*** Workers configuration
    workers: int = Field(default=1, description="Number of worker processes")
    reload: bool = Field(default=False, description="Enable auto-reload on code changes")
    proxy_headers: bool = Field(default=True, description="Process proxy headers")
    forwarded_allow_ips: str = Field(default="*", description="Allowed IPs for forwarded headers")

    ***REMOVED*** Backend API settings (for movie data)
    backend_api_url: str = Field(default="http://localhost:8000", description="Backend API URL")
    backend_api_timeout: int = Field(default=30, description="Backend API timeout in seconds")
    internal_api_key: str = Field(
        default="reco-to-backend-secret-key",
        description="Internal API key for backend communication",
    )

    ***REMOVED*** ML API settings
    ml_api_url: str = Field(default="http://localhost:8004", description="ML API URL")
    ml_api_timeout: int = Field(default=30, description="ML API timeout in seconds")

    ***REMOVED*** Embedding model settings
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="Embedding model name")
    embedding_dimension: int = Field(default=384, description="Embedding dimension size")
    batch_size: int = Field(default=32, description="Batch size for embedding generation")
    max_sequence_length: int = Field(
        default=512, description="Max sequence length for embedding model"
    )

    ***REMOVED*** Recommendation settings
    default_recommendation_count: int = Field(
        default=10, description="Default number of recommendations"
    )
    min_imdb_rating: float = Field(
        default=6.0, description="Minimum IMDb rating for recommendations"
    )
    similarity_threshold: float = Field(default=0.7, description="Minimum similarity threshold")
    user_vector_weight: float = Field(
        default=0.6, description="Weight for user vector in hybrid recommendations"
    )
    content_vector_weight: float = Field(
        default=0.4, description="Weight for content vector in hybrid recommendations"
    )

    ***REMOVED*** Cache settings (extending CacheConfigMixin)
    precompute_similarities: bool = Field(default=False, description="Precompute similarity scores")
    enable_caching: bool = Field(default=True, description="Enable Redis caching")

    ***REMOVED*** Performance settings
    max_concurrent_requests: int = Field(default=100, description="Maximum concurrent requests")
    request_timeout_seconds: int = Field(default=30, description="Request timeout in seconds")
    embedding_generation_timeout: int = Field(
        default=60, description="Embedding generation timeout"
    )

    ***REMOVED*** Feature flags
    enable_collaborative_filtering: bool = Field(
        default=True, description="Enable collaborative filtering"
    )
    enable_content_filtering: bool = Field(default=True, description="Enable content filtering")
    enable_trending_fallback: bool = Field(default=True, description="Enable trending fallback")
    enable_diversity_boost: bool = Field(default=True, description="Enable diversity boost")

    ***REMOVED*** Monitoring settings

    metrics_port: int = Field(default=9090, description="Metrics server port")
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")

    ***REMOVED*** Compatibility property for vector_collection_name vs qdrant_collection_name
    @property
    def qdrant_collection_name(self) -> str:
        """Return the vector collection name for compatibility with both naming conventions.

        Returns:
            The vector collection name
        """
        return self.vector_collection_name

    model_config = {
        "env_prefix": "",  ***REMOVED*** No prefix for environment variables
        "env_file": [".env", ".env.local"],
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    def __init__(self, **kwargs: Any) -> None:
        """Initialize Recommendation API configuration."""
        ***REMOVED*** Initialize with Pydantic Settings (will auto-load .env files)
        super().__init__(**kwargs)

        ***REMOVED*** Apply shared security and logging patterns
        self.apply_production_security_overrides()
        self._apply_recommendation_specific_overrides()
        self.log_configuration_summary()
        self._log_recommendation_specific_summary()

    def _apply_recommendation_specific_overrides(self) -> None:
        """Apply recommendation-specific production overrides."""
        if not self.is_production:
            return

        ***REMOVED*** Disable file logging in production to avoid volume permission issues
        if self.logs_dir:
            logger.warning("File logging disabled in production to avoid volume permission issues")
            object.__setattr__(self, "logs_dir", None)

    def _log_recommendation_specific_summary(self) -> None:
        """Log recommendation-specific configuration details."""
        ***REMOVED*** Log service URLs in compact format
        urls = {
            "backend": self.backend_api_url,
            "ml": self.ml_api_url,
            "qdrant": self.qdrant_url,
        }
        logger.info(f"Service URLs: {urls}")

        ***REMOVED*** Log feature flags in compact format
        logger.info(
            f"Features: collaborative={self.enable_collaborative_filtering}, "
            + f"content={self.enable_content_filtering}, "
            + f"trending={self.enable_trending_fallback}, "
            + f"diversity={self.enable_diversity_boost}"
        )

        ***REMOVED*** Log Redis URL
        logger.info(f"Redis URL: {self.get_redis_url_masked()}")

    @validator("backend_api_url", "ml_api_url")
    def validate_service_url(cls, v: str) -> str:
        """Validate service URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Service URL must start with http:// or https://")
        return v

    @validator("backend_api_timeout", "ml_api_timeout", "embedding_generation_timeout")
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is positive."""
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        if v > 300:
            raise ValueError("Timeout should not exceed 300 seconds")
        return v

    @validator("min_imdb_rating")
    def validate_imdb_rating(cls, v: float) -> float:
        """Validate IMDb rating is in valid range."""
        if not (0.0 <= v <= 10.0):
            raise ValueError("IMDb rating must be between 0.0 and 10.0")
        return v

    @validator("similarity_threshold", "user_vector_weight", "content_vector_weight")
    def validate_threshold_and_weights(cls, v: float) -> float:
        """Validate threshold and weights are between 0.0 and 1.0."""
        if not (0.0 <= v <= 1.0):
            raise ValueError("Value must be between 0.0 and 1.0")
        return v

    @validator("user_vector_weight", "content_vector_weight")
    def validate_weights_sum(cls, v: float, values: Dict[str, Any]) -> float:
        """Validate that weights sum to 1.0."""
        if "user_vector_weight" in values and "content_vector_weight" in values:
            total = values["user_vector_weight"] + v
            if abs(total - 1.0) > 0.001:  ***REMOVED*** Allow small floating point errors
                raise ValueError("User and content vector weights must sum to 1.0")
        return v

    def validate_production_settings(self) -> List[str]:
        """Validate configuration for production deployment."""
        issues = []

        ***REMOVED*** Get validation from parent classes
        issues.extend(super().validate_production_settings())
        issues.extend(self.validate_cache_production_settings())
        issues.extend(self.validate_vector_production_settings())

        ***REMOVED*** Recommendation-specific production validations
        if self.is_production:
            ***REMOVED*** Check for secure service URLs
            for url_name, url in [
                ("backend_api_url", self.backend_api_url),
                ("ml_api_url", self.ml_api_url),
            ]:
                if url.startswith("http://"):
                    issues.append(f"{url_name} should use HTTPS in production")

            ***REMOVED*** Check for localhost in URLs
            for url_name, url in [
                ("backend_api_url", self.backend_api_url),
                ("ml_api_url", self.ml_api_url),
            ]:
                if "localhost" in url:
                    issues.append(f"{url_name} should not use localhost in production")

        return issues

    def __str__(self) -> str:
        """Return a comprehensive multi-line string representation."""
        return f"""Recommendation API Configuration:
  Environment: {self.environment}
  Service: {self.service_name}
  
  HTTP Service:
    Host: {self.host}
    Port: {self.port}
    Debug: {self.debug}
    CORS Origins: {', '.join(self.cors_origins)}
    Allowed Hosts: {', '.join(self.allowed_hosts)}

  Service URLs:
    Backend: {self.backend_api_url}
    ML API: {self.ml_api_url}
    Qdrant: {self.qdrant_url}

  Cache:
    URL: {self.get_redis_url_masked()}
    TTL: {self.cache_ttl_default}s

  Vector DB:
    Collection: {self.vector_collection_name}
    Dimension: {self.vector_dimension}
    Distance Metric: {self.vector_distance_metric}

  Features:
    Collaborative Filtering: {self.enable_collaborative_filtering}
    Content Filtering: {self.enable_content_filtering}
    Trending Fallback: {self.enable_trending_fallback}
    Diversity Boost: {self.enable_diversity_boost}
    
  Recommendation Settings:
    Default Count: {self.default_recommendation_count}
    Min IMDb Rating: {self.min_imdb_rating}
    Similarity Threshold: {self.similarity_threshold}
    User/Content Weights: {self.user_vector_weight}/{self.content_vector_weight}"""


***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** GLOBAL SETTINGS INSTANCE
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Create global settings instance
settings = RecommendationAPIConfig()

***REMOVED*** Override log level for development
if settings.is_development:
    object.__setattr__(settings, "log_level", "DEBUG")
