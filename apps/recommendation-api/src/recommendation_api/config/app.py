"""Configuration settings for the Recommendation API service."""

import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

***REMOVED*** Load environment variables before any configuration
try:
    from dotenv import load_dotenv

    ***REMOVED*** Only load .env files if we're not in production
    if os.getenv("ENVIRONMENT") != "production":
        ***REMOVED*** Try multiple locations to find .env files (prioritize current directory)
        possible_paths = [
            Path.cwd() / ".env",
            Path.cwd() / ".env.local",
            Path(__file__).resolve().parents[3] / ".env",
            Path(__file__).resolve().parents[3] / ".env.local",
        ]

        for path in possible_paths:
            if path.exists():
                load_dotenv(dotenv_path=path, override=True)
                break
except ImportError:
    pass  ***REMOVED*** Continue without dotenv if not installed

***REMOVED*** Configure basic logging first for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** DEFAULT SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Server settings
DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")
DEFAULT_PORT = int(os.getenv("PORT", "8002"))
DEFAULT_WORKERS = int(os.getenv("WORKERS", "1"))
DEFAULT_RELOAD = os.getenv("RELOAD", "false").lower() == "true"
DEFAULT_VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"
DEFAULT_PROXY_HEADERS = os.getenv("PROXY_HEADERS", "true").lower() == "true"
DEFAULT_FORWARDED_ALLOW_IPS = os.getenv("FORWARDED_ALLOW_IPS", "*")

***REMOVED*** Logging and debugging
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEFAULT_DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DEFAULT_LOGS_DIR = os.getenv("LOGS_DIR", "logs")

***REMOVED*** Database settings
DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/next_watch"
)

***REMOVED*** Vector database settings
DEFAULT_QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
DEFAULT_QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
DEFAULT_QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "movies")

***REMOVED*** ML API settings
DEFAULT_ML_API_URL = os.getenv("ML_API_URL", "http://localhost:8004")
DEFAULT_ML_API_TIMEOUT = int(os.getenv("ML_API_TIMEOUT", "30"))

***REMOVED*** Embedding model settings
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
DEFAULT_EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))
DEFAULT_BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
DEFAULT_MAX_SEQUENCE_LENGTH = int(os.getenv("MAX_SEQUENCE_LENGTH", "512"))

***REMOVED*** Recommendation settings
DEFAULT_RECOMMENDATION_COUNT = int(os.getenv("RECOMMENDATION_COUNT", "10"))
DEFAULT_MIN_IMDB_RATING = float(os.getenv("MIN_IMDB_RATING", "6.0"))
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
DEFAULT_USER_VECTOR_WEIGHT = float(os.getenv("USER_VECTOR_WEIGHT", "0.6"))
DEFAULT_CONTENT_VECTOR_WEIGHT = float(os.getenv("CONTENT_VECTOR_WEIGHT", "0.4"))

***REMOVED*** Cache settings
DEFAULT_ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
DEFAULT_CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  ***REMOVED*** 1 hour
DEFAULT_PRECOMPUTE_SIMILARITIES = os.getenv("PRECOMPUTE_SIMILARITIES", "false").lower() == "true"

***REMOVED*** Performance settings
DEFAULT_MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
DEFAULT_REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
DEFAULT_EMBEDDING_GENERATION_TIMEOUT = int(os.getenv("EMBEDDING_GENERATION_TIMEOUT", "60"))

***REMOVED*** Feature flags
DEFAULT_ENABLE_COLLABORATIVE_FILTERING = (
    os.getenv("ENABLE_COLLABORATIVE_FILTERING", "true").lower() == "true"
)
DEFAULT_ENABLE_CONTENT_FILTERING = os.getenv("ENABLE_CONTENT_FILTERING", "true").lower() == "true"
DEFAULT_ENABLE_TRENDING_FALLBACK = os.getenv("ENABLE_TRENDING_FALLBACK", "true").lower() == "true"
DEFAULT_ENABLE_DIVERSITY_BOOST = os.getenv("ENABLE_DIVERSITY_BOOST", "true").lower() == "true"

***REMOVED*** Monitoring settings
DEFAULT_ENABLE_METRICS = os.getenv("ENABLE_METRICS", "false").lower() == "true"
DEFAULT_METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))
DEFAULT_HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))

***REMOVED*** Redis settings
DEFAULT_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_REDIS_TTL = int(os.getenv("REDIS_TTL", str(DEFAULT_CACHE_TTL)))
DEFAULT_REDIS_POOL_SIZE = int(os.getenv("REDIS_POOL_SIZE", "10"))

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** CONFIGURATION CLASS
***REMOVED*** ------------------------------------------------------------------------------


class Config:
    """Configuration class for the Recommendation API service."""

    ***REMOVED*** Server settings
    host: str
    port: int
    workers: int
    reload: bool
    verbose: bool
    proxy_headers: bool
    forwarded_allow_ips: str

    ***REMOVED*** Logging and debugging
    log_level: str
    debug: bool
    log_dir: str

    ***REMOVED*** Database settings
    database_url: str

    ***REMOVED*** Vector database settings
    qdrant_url: str
    qdrant_api_key: Optional[str]
    qdrant_collection_name: str

    ***REMOVED*** ML API settings
    ml_api_url: str
    ml_api_timeout: int

    ***REMOVED*** Embedding model settings
    embedding_model: str
    embedding_dimension: int
    batch_size: int
    max_sequence_length: int

    ***REMOVED*** Recommendation settings
    default_recommendation_count: int
    min_imdb_rating: float
    similarity_threshold: float
    user_vector_weight: float
    content_vector_weight: float

    ***REMOVED*** Cache settings
    enable_caching: bool
    cache_ttl_seconds: int
    precompute_similarities: bool

    ***REMOVED*** Performance settings
    max_concurrent_requests: int
    request_timeout_seconds: int
    embedding_generation_timeout: int

    ***REMOVED*** Feature flags
    enable_collaborative_filtering: bool
    enable_content_filtering: bool
    enable_trending_fallback: bool
    enable_diversity_boost: bool

    ***REMOVED*** Monitoring settings
    enable_metrics: bool
    metrics_port: int
    health_check_interval: int

    ***REMOVED*** Redis settings
    redis_url: str
    redis_ttl: int
    redis_pool_size: int

    ***REMOVED*** Derived settings
    environment: str
    is_production: bool
    is_development: bool
    allowed_hosts: List[str]

    ***REMOVED*** Singleton instance
    _instance = None

    @classmethod
    def get_instance(cls) -> "Config":
        """Get the singleton instance of Config.

        Returns:
            The global Config instance
        """
        if cls._instance is None:
            cls._instance = Config()
        return cls._instance

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        workers: int = DEFAULT_WORKERS,
        reload: bool = DEFAULT_RELOAD,
        verbose: bool = DEFAULT_VERBOSE,
        proxy_headers: bool = DEFAULT_PROXY_HEADERS,
        forwarded_allow_ips: str = DEFAULT_FORWARDED_ALLOW_IPS,
        log_level: str = DEFAULT_LOG_LEVEL,
        debug: bool = DEFAULT_DEBUG,
        log_dir: str = DEFAULT_LOGS_DIR,
        database_url: str = DEFAULT_DATABASE_URL,
        qdrant_url: str = DEFAULT_QDRANT_URL,
        qdrant_api_key: Optional[str] = DEFAULT_QDRANT_API_KEY,
        qdrant_collection_name: str = DEFAULT_QDRANT_COLLECTION_NAME,
        ml_api_url: str = DEFAULT_ML_API_URL,
        ml_api_timeout: int = DEFAULT_ML_API_TIMEOUT,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        embedding_dimension: int = DEFAULT_EMBEDDING_DIMENSION,
        batch_size: int = DEFAULT_BATCH_SIZE,
        max_sequence_length: int = DEFAULT_MAX_SEQUENCE_LENGTH,
        default_recommendation_count: int = DEFAULT_RECOMMENDATION_COUNT,
        min_imdb_rating: float = DEFAULT_MIN_IMDB_RATING,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        user_vector_weight: float = DEFAULT_USER_VECTOR_WEIGHT,
        content_vector_weight: float = DEFAULT_CONTENT_VECTOR_WEIGHT,
        enable_caching: bool = DEFAULT_ENABLE_CACHING,
        cache_ttl_seconds: int = DEFAULT_CACHE_TTL,
        precompute_similarities: bool = DEFAULT_PRECOMPUTE_SIMILARITIES,
        max_concurrent_requests: int = DEFAULT_MAX_CONCURRENT_REQUESTS,
        request_timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT,
        embedding_generation_timeout: int = DEFAULT_EMBEDDING_GENERATION_TIMEOUT,
        enable_collaborative_filtering: bool = DEFAULT_ENABLE_COLLABORATIVE_FILTERING,
        enable_content_filtering: bool = DEFAULT_ENABLE_CONTENT_FILTERING,
        enable_trending_fallback: bool = DEFAULT_ENABLE_TRENDING_FALLBACK,
        enable_diversity_boost: bool = DEFAULT_ENABLE_DIVERSITY_BOOST,
        enable_metrics: bool = DEFAULT_ENABLE_METRICS,
        metrics_port: int = DEFAULT_METRICS_PORT,
        health_check_interval: int = DEFAULT_HEALTH_CHECK_INTERVAL,
        redis_url: str = DEFAULT_REDIS_URL,
        redis_ttl: int = DEFAULT_REDIS_TTL,
        redis_pool_size: int = DEFAULT_REDIS_POOL_SIZE,
    ):
        """Initialize Recommendation API configuration.

        Args:
            host: Host address to bind the server to
            port: Port to listen on
            workers: Number of worker processes
            reload: Whether to reload on code changes
            verbose: Enable verbose logging
            proxy_headers: Whether to enable proxy header support
            forwarded_allow_ips: Which IPs to trust for forwarded headers
            log_level: Logging level
            debug: Enable debug mode
            log_dir: Directory for log files
            database_url: URL for PostgreSQL database
            qdrant_url: URL for Qdrant vector database
            qdrant_api_key: API key for Qdrant
            qdrant_collection_name: Name of the Qdrant collection for vectors
            ml_api_url: URL for ML API
            ml_api_timeout: Timeout for ML API requests
            embedding_model: Name of the embedding model to use
            embedding_dimension: Dimension of embedding vectors
            batch_size: Batch size for embedding generation
            max_sequence_length: Maximum sequence length for embeddings
            default_recommendation_count: Default number of recommendations
            min_imdb_rating: Minimum IMDb rating for recommendations
            similarity_threshold: Threshold for similarity matching
            user_vector_weight: Weight for user preference vectors
            content_vector_weight: Weight for content vectors
            enable_caching: Whether to enable caching
            cache_ttl_seconds: Cache TTL in seconds
            precompute_similarities: Whether to precompute similarities
            max_concurrent_requests: Maximum concurrent requests
            request_timeout_seconds: Request timeout in seconds
            embedding_generation_timeout: Timeout for embedding generation
            enable_collaborative_filtering: Whether to enable collaborative filtering
            enable_content_filtering: Whether to enable content filtering
            enable_trending_fallback: Whether to enable trending fallback
            enable_diversity_boost: Whether to enable diversity boost
            enable_metrics: Whether to enable metrics collection
            metrics_port: Port for metrics server
            health_check_interval: Health check interval in seconds
            redis_url: URL for Redis cache
            redis_ttl: TTL for Redis cache entries in seconds
            redis_pool_size: Size of the Redis connection pool
        """
        ***REMOVED*** In production, force debug to False
        if os.getenv("ENVIRONMENT") == "production":
            debug = False

        ***REMOVED*** Server settings
        self.host = host
        self.port = port
        self.workers = workers
        self.reload = reload
        self.verbose = verbose
        self.proxy_headers = proxy_headers
        self.forwarded_allow_ips = forwarded_allow_ips

        ***REMOVED*** Logging and debugging
        self.log_level = log_level
        self.debug = debug
        self.log_dir = log_dir

        ***REMOVED*** Database settings
        self.database_url = database_url

        ***REMOVED*** Vector database settings
        self.qdrant_url = qdrant_url.rstrip("/")
        self.qdrant_api_key = qdrant_api_key
        self.qdrant_collection_name = qdrant_collection_name

        ***REMOVED*** ML API settings
        self.ml_api_url = ml_api_url
        self.ml_api_timeout = ml_api_timeout

        ***REMOVED*** Embedding model settings
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension
        self.batch_size = batch_size
        self.max_sequence_length = max_sequence_length

        ***REMOVED*** Recommendation settings
        self.default_recommendation_count = default_recommendation_count
        self.min_imdb_rating = min_imdb_rating
        self.similarity_threshold = similarity_threshold
        self.user_vector_weight = user_vector_weight
        self.content_vector_weight = content_vector_weight

        ***REMOVED*** Cache settings
        self.enable_caching = enable_caching
        self.cache_ttl_seconds = cache_ttl_seconds
        self.precompute_similarities = precompute_similarities

        ***REMOVED*** Performance settings
        self.max_concurrent_requests = max_concurrent_requests
        self.request_timeout_seconds = request_timeout_seconds
        self.embedding_generation_timeout = embedding_generation_timeout

        ***REMOVED*** Feature flags
        self.enable_collaborative_filtering = enable_collaborative_filtering
        self.enable_content_filtering = enable_content_filtering
        self.enable_trending_fallback = enable_trending_fallback
        self.enable_diversity_boost = enable_diversity_boost

        ***REMOVED*** Monitoring settings
        self.enable_metrics = enable_metrics
        self.metrics_port = metrics_port
        self.health_check_interval = health_check_interval

        ***REMOVED*** Redis settings
        self.redis_url = redis_url
        self.redis_ttl = redis_ttl
        self.redis_pool_size = redis_pool_size

        ***REMOVED*** Derived settings
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.is_production = self.environment == "production"
        self.is_development = self.environment == "development"

        ***REMOVED*** Parse ALLOWED_HOSTS environment variable if it exists
        allowed_hosts_env = os.getenv("ALLOWED_HOSTS")
        if allowed_hosts_env:
            self.allowed_hosts = [host.strip() for host in allowed_hosts_env.split(",")]
        else:
            self.allowed_hosts = ["*"] if not self.is_production else ["localhost", "127.0.0.1"]

        ***REMOVED*** Log configuration
        logger.info(
            f"Initializing Recommendation API configuration with environment: {self.environment}"
        )
        logger.info(f"Database URL: {self.database_url}")
        logger.info(f"Qdrant URL: {self.qdrant_url}")
        logger.info(f"Qdrant Collection: {self.qdrant_collection_name}")
        logger.info(f"Debug mode: {self.debug}")

    @property
    def is_production_env(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def __str__(self) -> str:
        """Return a string representation of the Config instance with sensitive data masked.

        Returns:
            String representation of Config
        """
        ***REMOVED*** Mask sensitive information
        masked_db_url = self._mask_database_url(self.database_url)
        masked_qdrant_key = "****" if self.qdrant_api_key else None

        return (
            f"Config(host={self.host}, "
            f"port={self.port}, "
            f"log_level={self.log_level}, "
            f"debug={self.debug}, "
            f"database_url={masked_db_url}, "
            f"qdrant_url={self.qdrant_url}, "
            f"qdrant_collection={self.qdrant_collection_name}, "
            f"environment={self.environment}, "
            f"qdrant_api_key={masked_qdrant_key})"
        )

    def _mask_database_url(self, url: str) -> str:
        """Mask password in database URL if present."""
        if "@" in url and "://" in url:
            try:
                protocol_part = url.split("://")[0]
                auth_part = url.split("://")[1].split("@")[0]
                masked_auth = auth_part.split(":")[0] + ":****"
                remaining_part = url.split("@", 1)[1]
                return f"{protocol_part}://{masked_auth}@{remaining_part}"
            except (IndexError, ValueError):
                pass
        return url


***REMOVED*** Create a singleton instance to be imported elsewhere
settings = Config()
