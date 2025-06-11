"""Application configuration management.

This module provides centralized configuration for the bff-api application,
loading settings from environment variables with sensible defaults.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

***REMOVED*** Load environment variables from .env files
from .env import get_env_var, get_env_bool, get_env_int

***REMOVED*** Configure basic logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** DEFAULT PATHS AND DIRECTORIES
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Directory paths
DEFAULT_LOGS_DIR = Path(get_env_var("LOGS_DIR", "logs"))

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** SERVER CONFIGURATION
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_HOST = get_env_var("HOST", "0.0.0.0")
DEFAULT_PORT = get_env_int("PORT", 8001)
DEFAULT_CORS_ORIGINS = get_env_var("CORS_ORIGINS", "*")
DEFAULT_DEBUG = get_env_bool("DEBUG", False)

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** LOGGING AND MONITORING
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_LOG_LEVEL = get_env_var("LOG_LEVEL", "INFO")
DEFAULT_ENABLE_PERFORMANCE_METRICS = get_env_bool("ENABLE_PERFORMANCE_METRICS", False)

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** BACKEND SERVICE URLS
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_BACKEND_API_URL = get_env_var("BACKEND_API_URL", "http://localhost:8000")
DEFAULT_BACKEND_API_TIMEOUT = get_env_int("BACKEND_API_TIMEOUT", 30)
DEFAULT_RECO_API_URL = get_env_var("RECO_API_URL", "http://localhost:8002")
DEFAULT_AUTH_API_URL = get_env_var("AUTH_API_URL", "http://localhost:8003")

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** CACHE AND REDIS SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_REDIS_URL = get_env_var("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_CACHE_TTL = get_env_int("CACHE_TTL", 300)  ***REMOVED*** 5 minutes

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** AUTHENTICATION SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_JWT_SECRET = get_env_var("JWT_SECRET", "change_this_in_production_very_important")
DEFAULT_INTERNAL_API_KEY = get_env_var("INTERNAL_API_KEY", "bff-to-backend-secret-key")

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** SECURITY SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_ALLOWED_HOSTS = get_env_var("ALLOWED_HOSTS", "localhost,127.0.0.1")

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** CONFIGURATION CLASS
***REMOVED*** ------------------------------------------------------------------------------


class ConfigDict(TypedDict):
    """Type definition for configuration dictionary."""

    logs_dir: Path
    host: str
    port: int
    cors_origins: List[str]
    debug: bool
    log_level: str
    enable_performance_metrics: bool
    backend_api_url: str
    backend_api_timeout: int
    reco_api_url: str
    auth_api_url: str
    redis_url: str
    cache_ttl: int
    jwt_secret: Optional[str]
    internal_api_key: str
    allowed_hosts: List[str]


class Config:
    """Configuration class for the BFF service."""

    logs_dir: Path
    host: str
    port: int
    log_level: str
    debug: bool
    cors_origins: List[str]
    enable_performance_metrics: bool
    backend_api_url: str
    backend_api_timeout: int
    reco_api_url: str
    auth_api_url: str
    redis_url: str
    cache_ttl: int
    jwt_secret: Optional[str]
    internal_api_key: str
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
        logs_dir: Path = DEFAULT_LOGS_DIR,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        log_level: str = DEFAULT_LOG_LEVEL,
        debug: bool = DEFAULT_DEBUG,
        cors_origins: str = DEFAULT_CORS_ORIGINS,
        enable_performance_metrics: bool = DEFAULT_ENABLE_PERFORMANCE_METRICS,
        backend_api_url: str = DEFAULT_BACKEND_API_URL,
        backend_api_timeout: int = DEFAULT_BACKEND_API_TIMEOUT,
        reco_api_url: str = DEFAULT_RECO_API_URL,
        auth_api_url: str = DEFAULT_AUTH_API_URL,
        redis_url: str = DEFAULT_REDIS_URL,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        jwt_secret: Optional[str] = DEFAULT_JWT_SECRET,
        internal_api_key: str = DEFAULT_INTERNAL_API_KEY,
        allowed_hosts: str = DEFAULT_ALLOWED_HOSTS,
    ):
        """Initialize BFF configuration.

        Args:
            logs_dir: Directory to save log files
            host: Host for the BFF server
            port: Port for the BFF server
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            debug: Whether to enable debug mode
            cors_origins: Comma-separated list of allowed origins for CORS
            enable_performance_metrics: Whether to enable performance metrics
            backend_api_url: URL for backend API service
            backend_api_timeout: Timeout for backend API requests in seconds
            reco_api_url: URL for recommendation API service
            auth_api_url: URL for authentication service
            redis_url: URL for Redis connection
            cache_ttl: Cache TTL in seconds
            jwt_secret: Secret key for JWT token validation
            internal_api_key: API key for service-to-service authentication
            allowed_hosts: Comma-separated list of allowed hosts
        """
        ***REMOVED*** In production, force debug to False
        environment = get_env_var("ENVIRONMENT", "development")
        if environment == "production":
            debug = False

        self.logs_dir = logs_dir
        self.host = host
        self.port = port
        self.log_level = log_level
        self.debug = debug
        self.cors_origins = (
            [origin.strip() for origin in cors_origins.split(",")] if cors_origins != "*" else ["*"]
        )
        self.enable_performance_metrics = enable_performance_metrics

        ***REMOVED*** Backend service URLs (strip trailing slashes)
        self.backend_api_url = backend_api_url.rstrip("/")
        self.backend_api_timeout = backend_api_timeout
        self.reco_api_url = reco_api_url.rstrip("/")
        self.auth_api_url = auth_api_url.rstrip("/")

        ***REMOVED*** Cache settings
        self.redis_url = redis_url
        self.cache_ttl = cache_ttl

        ***REMOVED*** Authentication settings
        self.jwt_secret = jwt_secret
        self.internal_api_key = internal_api_key

        ***REMOVED*** Security settings
        self.allowed_hosts = (
            [host.strip() for host in allowed_hosts.split(",")] if allowed_hosts != "*" else ["*"]
        )

        ***REMOVED*** Derived settings
        self.environment = environment
        self.is_production = environment == "production"
        self.is_development = environment == "development"

        ***REMOVED*** Log configuration
        logger.info(f"Initializing BFF configuration with environment: {self.environment}")
        logger.info(f"Backend API URL: {self.backend_api_url}")
        logger.info(f"Recommendation API URL: {self.reco_api_url}")
        logger.info(f"Auth service URL: {self.auth_api_url}")
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
        masked_jwt = "****" if self.jwt_secret else None
        masked_api_key = (
            f"{'*' * (len(self.internal_api_key) - 4)}{self.internal_api_key[-4:]}"
            if self.internal_api_key
            else ""
        )

        return (
            f"Config(\n"
            f"  logs_dir={self.logs_dir},\n"
            f"  host={self.host},\n"
            f"  port={self.port},\n"
            f"  log_level={self.log_level},\n"
            f"  debug={self.debug},\n"
            f"  cors_origins={self.cors_origins},\n"
            f"  enable_performance_metrics={self.enable_performance_metrics},\n"
            f"  backend_api_url={self.backend_api_url},\n"
            f"  backend_api_timeout={self.backend_api_timeout},\n"
            f"  reco_api_url={self.reco_api_url},\n"
            f"  auth_api_url={self.auth_api_url},\n"
            f"  redis_url={self.redis_url},\n"
            f"  cache_ttl={self.cache_ttl},\n"
            f"  jwt_secret={masked_jwt},\n"
            f"  internal_api_key={masked_api_key},\n"
            f"  allowed_hosts={self.allowed_hosts},\n"
            f"  environment={self.environment}\n"
            f")"
        )


***REMOVED*** Create a singleton instance to be imported elsewhere
settings = Config()
