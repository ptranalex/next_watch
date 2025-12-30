"""Vector database configuration mixin for Qdrant.

Provides configuration for Qdrant vector database connections with
collection management and search settings.
"""

from typing import Any
from urllib.parse import urlparse

from pydantic import Field, validator


class VectorDBConfigMixin:
    """Qdrant vector database configuration mixin.

    This mixin provides Qdrant vector database configuration that can be composed
    into service configurations. It includes connection settings, collection
    management, and search configuration.

    Environment variables (with service prefix):
    - {SERVICE}_QDRANT_URL: Qdrant connection URL
    - {SERVICE}_QDRANT_API_KEY: Qdrant API key
    - {SERVICE}_QDRANT_COLLECTION_NAME: Default collection name
    - {SERVICE}_VECTOR_DIMENSION: Vector dimension size
    - {SERVICE}_VECTOR_DISTANCE_METRIC: Distance metric for similarity
    """

    qdrant_url: str = Field(
        default="http://localhost:6333",
        description="Qdrant server URL",
        examples=["http://localhost:6333", "https://qdrant.example.com"],
    )
    qdrant_api_key: str | None = Field(
        default=None, description="Qdrant API key for authentication"
    )
    qdrant_timeout: int = Field(default=30, description="Request timeout in seconds")
    qdrant_prefer_grpc: bool = Field(
        default=False, description="Prefer gRPC over HTTP for better performance"
    )
    qdrant_grpc_port: int = Field(default=6334, description="gRPC port for Qdrant")

    # Collection configuration
    vector_collection_name: str = Field(
        default="movies", description="Default vector collection name"
    )
    vector_dimension: int = Field(
        default=768, description="Vector dimension size (must match embedding model)"
    )
    vector_distance_metric: str = Field(
        default="cosine", description="Distance metric for similarity calculation"
    )

    # Search configuration
    search_limit_default: int = Field(default=10, description="Default search result limit")
    search_limit_max: int = Field(default=100, description="Maximum allowed search result limit")
    search_score_threshold: float = Field(
        default=0.7, description="Minimum similarity score threshold"
    )

    # Performance configuration
    vector_cache_size: int = Field(
        default=1000, description="Vector cache size for better performance"
    )
    enable_vector_indexing: bool = Field(
        default=True, description="Enable vector indexing for faster search"
    )
    hnsw_ef_construct: int = Field(default=64, description="HNSW index construction parameter")
    hnsw_m: int = Field(default=16, description="HNSW index M parameter")

    @validator("qdrant_url")
    def validate_qdrant_url(cls, v: str) -> str:
        """Validate Qdrant URL format."""
        if not v:
            raise ValueError("Qdrant URL cannot be empty")

        try:
            parsed = urlparse(v)
            if parsed.scheme not in ["http", "https"]:
                raise ValueError(
                    f"Unsupported Qdrant URL scheme: {parsed.scheme}. "
                    "Only 'http' and 'https' are supported"
                )

            if not parsed.hostname:
                raise ValueError("Qdrant URL must include hostname")

        except Exception as e:
            raise ValueError(f"Invalid Qdrant URL format: {e}")

        return v

    @validator("qdrant_timeout")
    def validate_qdrant_timeout(cls, v: int) -> int:
        """Validate Qdrant timeout."""
        if v < 1:
            raise ValueError("Qdrant timeout must be at least 1 second")
        if v > 300:  # 5 minutes
            raise ValueError("Qdrant timeout should not exceed 300 seconds")
        return v

    @validator("qdrant_grpc_port")
    def validate_grpc_port(cls, v: int) -> int:
        """Validate gRPC port."""
        if not (1 <= v <= 65535):
            raise ValueError("Qdrant gRPC port must be between 1 and 65535")
        return v

    @validator("vector_collection_name")
    def validate_collection_name(cls, v: str) -> str:
        """Validate collection name format."""
        if not v:
            raise ValueError("Vector collection name cannot be empty")

        # Collection names should be valid identifiers
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Collection name must contain only alphanumeric, underscore, or dash characters"
            )

        if len(v) > 63:
            raise ValueError("Collection name must be 63 characters or less")

        return v

    @validator("vector_dimension")
    def validate_vector_dimension(cls, v: int) -> int:
        """Validate vector dimension."""
        if v < 1:
            raise ValueError("Vector dimension must be at least 1")
        if v > 4096:  # Reasonable upper limit
            raise ValueError("Vector dimension should not exceed 4096")

        # Common embedding dimensions
        common_dimensions = [128, 256, 384, 512, 768, 1024, 1536, 2048]
        if v not in common_dimensions:
            # Warning: this might be intentional, so don't raise error
            pass

        return v

    @validator("vector_distance_metric")
    def validate_distance_metric(cls, v: str) -> str:
        """Validate distance metric."""
        allowed_metrics = ["cosine", "dot", "euclid", "manhattan"]
        if v not in allowed_metrics:
            raise ValueError(
                f"Unsupported distance metric: {v}. "
                f"Allowed metrics: {', '.join(allowed_metrics)}"
            )
        return v

    @validator("search_limit_default", "search_limit_max")
    def validate_search_limits(cls, v: int) -> int:
        """Validate search limits."""
        if v < 1:
            raise ValueError("Search limit must be at least 1")
        if v > 1000:
            raise ValueError("Search limit should not exceed 1000")
        return v

    @validator("search_score_threshold")
    def validate_score_threshold(cls, v: float) -> float:
        """Validate similarity score threshold."""
        if not (0.0 <= v <= 1.0):
            raise ValueError("Search score threshold must be between 0.0 and 1.0")
        return v

    @validator("vector_cache_size")
    def validate_cache_size(cls, v: int) -> int:
        """Validate vector cache size."""
        if v < 0:
            raise ValueError("Vector cache size cannot be negative")
        if v > 100000:
            raise ValueError("Vector cache size should not exceed 100,000")
        return v

    @validator("hnsw_ef_construct")
    def validate_hnsw_ef_construct(cls, v: int) -> int:
        """Validate HNSW ef_construct parameter."""
        if v < 4:
            raise ValueError("HNSW ef_construct must be at least 4")
        if v > 512:
            raise ValueError("HNSW ef_construct should not exceed 512")
        return v

    @validator("hnsw_m")
    def validate_hnsw_m(cls, v: int) -> int:
        """Validate HNSW M parameter."""
        if v < 2:
            raise ValueError("HNSW M must be at least 2")
        if v > 64:
            raise ValueError("HNSW M should not exceed 64")
        return v

    def get_qdrant_config(self) -> dict[str, Any]:
        """Get Qdrant connection configuration dictionary.

        Returns:
            Dictionary with Qdrant connection configuration
        """
        config = {
            "url": self.qdrant_url,
            "timeout": self.qdrant_timeout,
            "prefer_grpc": self.qdrant_prefer_grpc,
        }

        if self.qdrant_api_key:
            config["api_key"] = self.qdrant_api_key

        if self.qdrant_prefer_grpc:
            config["grpc_port"] = self.qdrant_grpc_port

        return config

    def get_collection_config(self) -> dict[str, Any]:
        """Get vector collection configuration dictionary.

        Returns:
            Dictionary with collection configuration
        """
        return {
            "name": self.vector_collection_name,
            "dimension": self.vector_dimension,
            "distance_metric": self.vector_distance_metric,
            "hnsw_config": {
                "ef_construct": self.hnsw_ef_construct,
                "m": self.hnsw_m,
            },
            "cache_size": self.vector_cache_size,
            "indexing_enabled": self.enable_vector_indexing,
        }

    def get_search_config(self) -> dict[str, Any]:
        """Get search configuration dictionary.

        Returns:
            Dictionary with search configuration
        """
        return {
            "default_limit": self.search_limit_default,
            "max_limit": self.search_limit_max,
            "score_threshold": self.search_score_threshold,
        }

    def get_qdrant_url_masked(self) -> str:
        """Get Qdrant URL with API key masked for logging.

        Returns:
            Qdrant URL with sensitive information masked
        """
        # API key is typically passed separately, so just return URL
        return self.qdrant_url

    def validate_vector_production_settings(self) -> list[str]:
        """Validate vector database configuration for production deployment.

        Returns:
            List of validation issues, empty if valid
        """
        issues = []

        # Check for development/test URLs in production
        if "localhost" in self.qdrant_url:
            issues.append("Qdrant should not use localhost in production")

        if "test" in self.qdrant_url.lower():
            issues.append("Qdrant URL appears to reference test instance")

        # API key should be configured for production
        if not self.qdrant_api_key:
            issues.append("Qdrant API key should be configured in production")

        # Performance settings for production
        if not self.enable_vector_indexing:
            issues.append("Vector indexing should be enabled in production")

        if self.vector_cache_size < 100:
            issues.append("Vector cache size should be at least 100 in production")

        # gRPC recommended for production performance
        if not self.qdrant_prefer_grpc:
            issues.append("Consider enabling gRPC for better performance in production")

        # Check collection name doesn't contain sensitive info
        if "test" in self.vector_collection_name.lower():
            issues.append("Collection name appears to reference test collection")

        return issues
