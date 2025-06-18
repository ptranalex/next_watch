"""Configuration settings for the Backend API service.

This module provides centralized configuration for the backend-api application,
loading settings from environment variables with sensible defaults.

It combines movie database configuration with API-specific settings including
authentication, Redis, CORS, and performance monitoring.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

from backend_api.config.env import get_env_bool, get_env_int, get_env_var
from backend_api.config.logging import get_logger

***REMOVED*** Configure basic logging first for this module
logger = get_logger(__name__)

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** TYPE DEFINITIONS
***REMOVED*** ------------------------------------------------------------------------------


class ConfigDict(TypedDict, total=False):
    """Type definition for configuration dictionary."""

    database_url: str
    database_echo: bool
    database_pool_size: int
    database_max_overflow: int
    database_pool_timeout: int
    log_level: str
    sql_log_level: str
    api_port: int
    debug: bool
    cors_origins: List[str]
    redis_url: str
    jwt_secret: str


***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** DEFAULT CONFIGURATION VALUES
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Database URLs and connection settings
DEFAULT_DATABASE_URL = get_env_var(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/next_watch"
)
DEFAULT_DATABASE_ECHO = get_env_bool("DATABASE_ECHO", False)
DEFAULT_DATABASE_POOL_SIZE = get_env_int("DATABASE_POOL_SIZE", 5)
DEFAULT_DATABASE_MAX_OVERFLOW = get_env_int("DATABASE_MAX_OVERFLOW", 10)
DEFAULT_DATABASE_POOL_TIMEOUT = get_env_int("DATABASE_POOL_TIMEOUT", 30)

***REMOVED*** API settings
DEFAULT_API_PORT = get_env_int("BACKEND_API_PORT", 8001)
DEFAULT_CORS_ORIGINS = get_env_var("CORS_ORIGINS", "*")

***REMOVED*** Logging settings
DEFAULT_LOG_LEVEL = get_env_var("LOG_LEVEL", "INFO")
DEFAULT_SQL_LOG_LEVEL = get_env_var("SQL_LOG_LEVEL", "WARNING")
DEFAULT_DEBUG = get_env_bool("DEBUG", False)
***REMOVED*** Set to None to disable file logging, or provide a path to enable it
***REMOVED*** Disable file logging in production to avoid volume permission issues
_logs_dir_env = get_env_var("LOGS_DIR", "logs")
_environment = get_env_var("ENVIRONMENT", "development")
DEFAULT_LOGS_DIR = _logs_dir_env if _environment != "production" else None

***REMOVED*** Performance monitoring
DEFAULT_ENABLE_PERFORMANCE_METRICS = get_env_bool("ENABLE_PERFORMANCE_METRICS", False)

***REMOVED*** Database profiling settings (development/debugging only)
DEFAULT_ENABLE_DB_PROFILING = get_env_bool("ENABLE_DB_PROFILING", False)
DEFAULT_DB_PROFILING_SLOW_QUERY_THRESHOLD_MS = get_env_int(
    "DB_PROFILING_SLOW_QUERY_THRESHOLD_MS", 100
)

***REMOVED*** Database monitoring settings
DEFAULT_DATABASE_MONITORING_ENABLED = get_env_bool("DATABASE_MONITORING_ENABLED", True)
DEFAULT_SLOW_QUERY_THRESHOLD_MS = get_env_int("SLOW_QUERY_THRESHOLD_MS", 100)

***REMOVED*** Redis settings
DEFAULT_REDIS_URL = get_env_var("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_REDIS_MAX_CONNECTIONS = get_env_int("REDIS_MAX_CONNECTIONS", 10)
DEFAULT_REDIS_SOCKET_TIMEOUT = get_env_int("REDIS_SOCKET_TIMEOUT", 30)
DEFAULT_REDIS_SOCKET_CONNECT_TIMEOUT = get_env_int("REDIS_SOCKET_CONNECT_TIMEOUT", 10)
DEFAULT_REDIS_RETRY_ON_TIMEOUT = get_env_bool("REDIS_RETRY_ON_TIMEOUT", True)

***REMOVED*** Authentication settings (for JWT integration with auth-api)
DEFAULT_JWT_SECRET = get_env_var("JWT_SECRET", "change_this_in_production_very_important")
DEFAULT_JWT_ALGORITHM = get_env_var("JWT_ALGORITHM", "HS256")
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = get_env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = get_env_int("REFRESH_TOKEN_EXPIRE_DAYS", 7)

***REMOVED*** Security settings
DEFAULT_ALLOWED_HOSTS = get_env_var("ALLOWED_HOSTS", "localhost,127.0.0.1,backend-api")

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** CONFIGURATION CLASS
***REMOVED*** ------------------------------------------------------------------------------


class Config:
    """Configuration class for the Backend API service."""

    ***REMOVED*** Environment settings
    environment: str

    ***REMOVED*** Database settings
    database_url: str
    database_echo: bool
    database_pool_size: int
    database_max_overflow: int
    database_pool_timeout: int

    ***REMOVED*** API settings
    api_port: int
    debug: bool
    cors_origins: List[str]
    enable_performance_metrics: bool
    logs_dir: Optional[str]

    ***REMOVED*** Logging settings
    log_level: str
    sql_log_level: str

    ***REMOVED*** Redis settings
    redis_url: str
    redis_max_connections: int
    redis_socket_timeout: int
    redis_socket_connect_timeout: int
    redis_retry_on_timeout: bool

    ***REMOVED*** JWT settings (for auth integration)
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    ***REMOVED*** Security settings
    allowed_hosts: List[str]

    ***REMOVED*** Database profiling settings (development only)
    enable_db_profiling: bool
    db_profiling_slow_query_threshold_ms: int

    ***REMOVED*** Database monitoring settings
    database_monitoring_enabled: bool
    slow_query_threshold_ms: int

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
        ***REMOVED*** Environment settings
        environment: str = get_env_var("ENVIRONMENT", "development"),
        ***REMOVED*** Database settings
        database_url: str = DEFAULT_DATABASE_URL,
        database_echo: bool = DEFAULT_DATABASE_ECHO,
        database_pool_size: int = DEFAULT_DATABASE_POOL_SIZE,
        database_max_overflow: int = DEFAULT_DATABASE_MAX_OVERFLOW,
        database_pool_timeout: int = DEFAULT_DATABASE_POOL_TIMEOUT,
        ***REMOVED*** API settings
        api_port: int = DEFAULT_API_PORT,
        debug: bool = DEFAULT_DEBUG,
        cors_origins: str = DEFAULT_CORS_ORIGINS,
        enable_performance_metrics: bool = DEFAULT_ENABLE_PERFORMANCE_METRICS,
        logs_dir: Optional[str] = DEFAULT_LOGS_DIR,
        ***REMOVED*** Logging settings
        log_level: str = DEFAULT_LOG_LEVEL,
        sql_log_level: str = DEFAULT_SQL_LOG_LEVEL,
        ***REMOVED*** Redis settings
        redis_url: str = DEFAULT_REDIS_URL,
        redis_max_connections: int = DEFAULT_REDIS_MAX_CONNECTIONS,
        redis_socket_timeout: int = DEFAULT_REDIS_SOCKET_TIMEOUT,
        redis_socket_connect_timeout: int = DEFAULT_REDIS_SOCKET_CONNECT_TIMEOUT,
        redis_retry_on_timeout: bool = DEFAULT_REDIS_RETRY_ON_TIMEOUT,
        ***REMOVED*** JWT settings
        jwt_secret: str = DEFAULT_JWT_SECRET,
        jwt_algorithm: str = DEFAULT_JWT_ALGORITHM,
        access_token_expire_minutes: int = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days: int = DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
        ***REMOVED*** Security settings
        allowed_hosts: str = DEFAULT_ALLOWED_HOSTS,
        ***REMOVED*** Database profiling settings (development only)
        enable_db_profiling: bool = DEFAULT_ENABLE_DB_PROFILING,
        db_profiling_slow_query_threshold_ms: int = DEFAULT_DB_PROFILING_SLOW_QUERY_THRESHOLD_MS,
        ***REMOVED*** Database monitoring settings
        database_monitoring_enabled: bool = DEFAULT_DATABASE_MONITORING_ENABLED,
        slow_query_threshold_ms: int = DEFAULT_SLOW_QUERY_THRESHOLD_MS,
    ):
        """Initialize Backend API configuration.

        Args:
            environment: Application environment (development, production, etc.)
            database_url: Database connection URL
            database_echo: Whether to echo SQL commands
            database_pool_size: Connection pool size
            database_max_overflow: Maximum overflow connections
            database_pool_timeout: Pool timeout in seconds
            api_port: Port for the backend API server
            debug: Whether to enable debug mode
            cors_origins: Comma-separated list of allowed origins for CORS
            enable_performance_metrics: Whether to enable performance metrics
            logs_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            sql_log_level: SQL-specific logging level
            redis_url: Redis connection URL
            redis_max_connections: Maximum Redis connections
            redis_socket_timeout: Redis socket timeout in seconds
            redis_socket_connect_timeout: Redis connection timeout in seconds
            redis_retry_on_timeout: Whether to retry on Redis timeout
            jwt_secret: Secret key for JWT token generation
            jwt_algorithm: Algorithm for JWT token generation
            access_token_expire_minutes: Minutes until access token expires
            refresh_token_expire_days: Days until refresh token expires
            allowed_hosts: Comma-separated list of allowed hosts
            enable_db_profiling: Whether to enable database profiling
            db_profiling_slow_query_threshold_ms: Threshold in milliseconds for slow queries
            database_monitoring_enabled: Whether to enable database monitoring instrumentation
            slow_query_threshold_ms: Threshold in milliseconds for slow query warnings
        """
        ***REMOVED*** Store environment setting
        self.environment = environment

        ***REMOVED*** In production, force debug to False
        if environment == "production":
            debug = False

        ***REMOVED*** Database settings
        self.database_url = database_url
        self.database_echo = database_echo
        self.database_pool_size = database_pool_size
        self.database_max_overflow = database_max_overflow
        self.database_pool_timeout = database_pool_timeout

        ***REMOVED*** API settings
        self.api_port = api_port
        self.debug = debug
        self.cors_origins = (
            [origin.strip() for origin in cors_origins.split(",")] if cors_origins != "*" else ["*"]
        )
        self.enable_performance_metrics = enable_performance_metrics
        ***REMOVED*** Store logs directory
        self.logs_dir = logs_dir

        ***REMOVED*** Logging settings
        self.log_level = log_level
        self.sql_log_level = sql_log_level

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

        ***REMOVED*** Security settings
        self.allowed_hosts = (
            [host.strip() for host in allowed_hosts.split(",")] if allowed_hosts != "*" else ["*"]
        )

        ***REMOVED*** Database profiling settings (development only)
        self.enable_db_profiling = enable_db_profiling
        self.db_profiling_slow_query_threshold_ms = db_profiling_slow_query_threshold_ms

        ***REMOVED*** Database monitoring settings
        self.database_monitoring_enabled = database_monitoring_enabled
        self.slow_query_threshold_ms = slow_query_threshold_ms

        ***REMOVED*** Force disable profiling in production for security and performance
        if self.is_production:
            if self.enable_db_profiling:
                logger.warning(
                    "Database profiling is disabled in production for security and performance"
                )
            self.enable_db_profiling = False

        ***REMOVED*** Log configuration on initialization
        logger.info(f"Initializing backend-api configuration with environment: {self.environment}")
        logger.info(f"Database URL: {self._mask_database_password(self.database_url)}")
        logger.info(f"API Port: {self.api_port}")
        logger.info(f"Debug mode: {self.debug}")
        logger.info(f"Redis URL: {self._mask_database_password(self.redis_url)}")

        ***REMOVED*** Warn if using default JWT secret in production
        if self.jwt_secret == DEFAULT_JWT_SECRET and not self.debug:
            logger.warning(
                "WARNING: Using default JWT_SECRET in production environment. "
                "This is insecure. Set a proper JWT_SECRET environment variable."
            )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def __str__(self) -> str:
        """Return a comprehensive multi-line string representation of the Config instance."""
        ***REMOVED*** Mask password in database_url for security
        masked_db_url = self._mask_database_password(self.database_url)
        masked_redis_url = self._mask_database_password(self.redis_url)

        return f"""Backend API Configuration:
  Environment: {self.environment}
  
  Database Settings:
    URL: {masked_db_url}
    Echo SQL: {self.database_echo}
    Pool Size: {self.database_pool_size}
    Max Overflow: {self.database_max_overflow}
    Pool Timeout: {self.database_pool_timeout}s

  API Settings:
    Port: {self.api_port}
    Debug: {self.debug}
    CORS Origins: {', '.join(self.cors_origins)}
    Performance Metrics: {self.enable_performance_metrics}

  Logging Settings:
    Log Level: {self.log_level}
    SQL Log Level: {self.sql_log_level}
    Logs Directory: {self.logs_dir}

  Redis Settings:
    URL: {masked_redis_url}
    Max Connections: {self.redis_max_connections}
    Socket Timeout: {self.redis_socket_timeout}s
    Connect Timeout: {self.redis_socket_connect_timeout}s
    Retry on Timeout: {self.redis_retry_on_timeout}

  Authentication Settings:
    JWT Algorithm: {self.jwt_algorithm}
    Access Token Expire: {self.access_token_expire_minutes}min
    Refresh Token Expire: {self.refresh_token_expire_days}days

  Security Settings:
    Allowed Hosts: {', '.join(self.allowed_hosts)}"""

    @staticmethod
    def _mask_database_password(url: str) -> str:
        """Mask the password in a database URL for logging purposes.

        Args:
            url: Database URL string

        Returns:
            URL with password masked
        """
        if "://" not in url:
            return url

        try:
            ***REMOVED*** Simple approach to mask password in standard SQLAlchemy URLs
            if "@" in url and ":" in url:
                ***REMOVED*** Split URL into components
                protocol_part, rest = url.split("://", 1)
                if "@" in rest:
                    auth_part, host_part = rest.split("@", 1)
                    if ":" in auth_part:
                        username, password = auth_part.split(":", 1)
                        ***REMOVED*** Replace password with asterisks
                        return f"{protocol_part}://{username}:******@{host_part}"
        except Exception:
            pass

        return url


***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** GLOBAL SETTINGS INSTANCE
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Create global settings instance
settings = Config.get_instance()
