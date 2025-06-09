"""Application configuration management.

This module provides centralized configuration for the backend-api application,
loading settings from environment variables with sensible defaults.
"""

import json
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
***REMOVED*** DATABASE SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_DATABASE_URL = get_env_var(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/next_watch"
)

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** API SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_API_PORT = get_env_int("API_PORT", 8000)
DEFAULT_CORS_ORIGINS = get_env_var("CORS_ORIGINS", "*")
DEFAULT_DEBUG = get_env_bool("DEBUG", False)

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** LOGGING AND OUTPUT SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_LOG_LEVEL = get_env_var("LOG_LEVEL", "INFO")

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** PERFORMANCE MONITORING
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_ENABLE_PERFORMANCE_METRICS = get_env_bool("ENABLE_PERFORMANCE_METRICS", False)

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** AUTHENTICATION SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_JWT_SECRET = get_env_var("JWT_SECRET", "change_this_in_production_very_important")
DEFAULT_JWT_ALGORITHM = get_env_var("JWT_ALGORITHM", "HS256")
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = get_env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = get_env_int("REFRESH_TOKEN_EXPIRE_DAYS", 7)
DEFAULT_JWT_JWK_ROTATION_INTERVAL = get_env_int("JWT_JWK_ROTATION_INTERVAL", 86400)  ***REMOVED*** 24 hours

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** REDIS SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_REDIS_URL = get_env_var("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_REDIS_MAX_CONNECTIONS = get_env_int("REDIS_MAX_CONNECTIONS", 10)
DEFAULT_REDIS_SOCKET_TIMEOUT = get_env_int("REDIS_SOCKET_TIMEOUT", 30)
DEFAULT_REDIS_SOCKET_CONNECT_TIMEOUT = get_env_int("REDIS_SOCKET_CONNECT_TIMEOUT", 30)
DEFAULT_REDIS_RETRY_ON_TIMEOUT = get_env_bool("REDIS_RETRY_ON_TIMEOUT", True)

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** CONFIGURATION CLASS
***REMOVED*** ------------------------------------------------------------------------------


class ConfigDict(TypedDict):
    """Type definition for configuration dictionary."""

    logs_dir: Path
    database_url: str
    api_port: int
    cors_origins: List[str]
    debug: bool
    log_level: str
    enable_performance_metrics: bool
    redis_url: str
    redis_max_connections: int
    redis_socket_timeout: int
    redis_socket_connect_timeout: int
    redis_retry_on_timeout: bool
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    jwt_jwk_rotation_interval: int


class Config:
    """Configuration class for the backend API."""

    logs_dir: Path
    database_url: str
    api_port: int
    log_level: str
    debug: bool
    cors_origins: List[str]
    enable_performance_metrics: bool
    redis_url: str
    redis_max_connections: int
    redis_socket_timeout: int
    redis_socket_connect_timeout: int
    redis_retry_on_timeout: bool
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    jwt_jwk: Optional[Dict[str, Any]]
    jwt_jwk_rotation_interval: int

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
        database_url: str = DEFAULT_DATABASE_URL,
        api_port: int = DEFAULT_API_PORT,
        log_level: str = DEFAULT_LOG_LEVEL,
        debug: bool = DEFAULT_DEBUG,
        cors_origins: str = DEFAULT_CORS_ORIGINS,
        enable_performance_metrics: bool = DEFAULT_ENABLE_PERFORMANCE_METRICS,
        redis_url: str = DEFAULT_REDIS_URL,
        redis_max_connections: int = DEFAULT_REDIS_MAX_CONNECTIONS,
        redis_socket_timeout: int = DEFAULT_REDIS_SOCKET_TIMEOUT,
        redis_socket_connect_timeout: int = DEFAULT_REDIS_SOCKET_CONNECT_TIMEOUT,
        redis_retry_on_timeout: bool = DEFAULT_REDIS_RETRY_ON_TIMEOUT,
        jwt_secret: str = DEFAULT_JWT_SECRET,
        jwt_algorithm: str = DEFAULT_JWT_ALGORITHM,
        access_token_expire_minutes: int = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days: int = DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
        jwt_jwk_rotation_interval: int = DEFAULT_JWT_JWK_ROTATION_INTERVAL,
    ):
        """Initialize configuration.

        Args:
            logs_dir: Directory to save log files
            database_url: URL for database connection
            api_port: Port for the API server
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            debug: Whether to enable debug mode
            cors_origins: Comma-separated list of allowed origins for CORS
            enable_performance_metrics: Whether to enable performance metrics
            redis_url: URL for Redis connection
            redis_max_connections: Maximum number of Redis connections in pool
            redis_socket_timeout: Redis socket timeout in seconds
            redis_socket_connect_timeout: Redis socket connect timeout in seconds
            redis_retry_on_timeout: Whether to retry on timeout errors
            jwt_secret: Secret key for JWT token generation
            jwt_algorithm: Algorithm for JWT token generation
            access_token_expire_minutes: Minutes until access token expires
            refresh_token_expire_days: Days until refresh token expires
            jwt_jwk_rotation_interval: Interval in seconds for JWK rotation
        """
        ***REMOVED*** In production, force debug to False
        environment = get_env_var("ENVIRONMENT", "development")
        if environment == "production":
            debug = False

        self.logs_dir = logs_dir
        self.database_url = database_url
        self.api_port = api_port
        self.log_level = log_level
        self.debug = debug
        self.cors_origins = (
            [origin.strip() for origin in cors_origins.split(",")] if cors_origins != "*" else ["*"]
        )
        self.enable_performance_metrics = enable_performance_metrics

        ***REMOVED*** Redis settings
        self.redis_url = redis_url
        self.redis_max_connections = redis_max_connections
        self.redis_socket_timeout = redis_socket_timeout
        self.redis_socket_connect_timeout = redis_socket_connect_timeout
        self.redis_retry_on_timeout = redis_retry_on_timeout

        ***REMOVED*** JWT settings
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.jwt_jwk_rotation_interval = jwt_jwk_rotation_interval

        ***REMOVED*** Parse JWK if available
        self.jwt_jwk = None
        if jwk_str := get_env_var("JWT_JWK"):
            try:
                self.jwt_jwk = json.loads(jwk_str)
                logger.info("JWK configuration loaded successfully")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JWK configuration: {e}")
                if not self.debug:
                    raise ValueError("Invalid JWK configuration in production environment")

        ***REMOVED*** Log configuration
        logger.info(f"Initializing configuration with environment: {environment}")
        logger.info(f"Database URL: {self._mask_database_password(self.database_url)}")
        logger.info(f"Redis URL: {self.redis_url}")
        logger.info(f"Redis max connections: {self.redis_max_connections}")
        logger.info(
            f"Redis timeouts: socket={self.redis_socket_timeout}s, connect={self.redis_socket_connect_timeout}s"
        )
        logger.info(f"Redis retry on timeout: {self.redis_retry_on_timeout}")
        logger.info(f"Debug mode: {self.debug}")
        logger.info(f"JWT algorithm: {self.jwt_algorithm}")
        logger.info(f"JWK enabled: {self.jwt_jwk is not None}")

        ***REMOVED*** Warn if using default JWT secret in production
        if self.jwt_secret == DEFAULT_JWT_SECRET and not self.debug:
            logger.warning(
                "WARNING: Using default JWT_SECRET in production environment. "
                "This is insecure. Set a proper JWT_SECRET environment variable."
            )

    def _mask_database_password(self, url: str) -> str:
        """Mask password in database URL for logging.

        Args:
            url: Database URL

        Returns:
            Masked URL
        """
        if "@" in url and "://" in url:
            protocol_part = url.split("://")[0]
            auth_part = url.split("://")[1].split("@")[0]
            masked_auth = auth_part.split(":")[0] + ":****"
            remaining_part = url.split("@", 1)[1]
            return f"{protocol_part}://{masked_auth}@{remaining_part}"
        return url

    def __str__(self) -> str:
        """Return a string representation of the Config instance with sensitive data masked.

        Returns:
            String representation of Config
        """
        ***REMOVED*** Mask sensitive information
        masked_url = self._mask_database_password(self.database_url)
        masked_jwt = "****" if self.jwt_secret else None

        return (
            f"Config(\n"
            f"  logs_dir={self.logs_dir},\n"
            f"  database_url={masked_url},\n"
            f"  api_port={self.api_port},\n"
            f"  log_level={self.log_level},\n"
            f"  debug={self.debug},\n"
            f"  cors_origins={self.cors_origins},\n"
            f"  enable_performance_metrics={self.enable_performance_metrics},\n"
            f"  redis_url={self.redis_url},\n"
            f"  redis_max_connections={self.redis_max_connections},\n"
            f"  redis_socket_timeout={self.redis_socket_timeout},\n"
            f"  redis_socket_connect_timeout={self.redis_socket_connect_timeout},\n"
            f"  redis_retry_on_timeout={self.redis_retry_on_timeout},\n"
            f"  jwt_algorithm={self.jwt_algorithm},\n"
            f"  access_token_expire_minutes={self.access_token_expire_minutes},\n"
            f"  refresh_token_expire_days={self.refresh_token_expire_days},\n"
            f"  jwt_jwk_rotation_interval={self.jwt_jwk_rotation_interval},\n"
            f"  jwt_jwk_enabled={self.jwt_jwk is not None}\n"
            f")"
        )


***REMOVED*** Create a singleton instance to be imported elsewhere
settings = Config()
