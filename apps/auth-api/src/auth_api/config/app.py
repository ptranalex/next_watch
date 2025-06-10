"""Configuration settings for the authentication API.

This module provides centralized configuration for the auth-api application,
loading settings from environment variables with sensible defaults.

It uses the env.py module to load environment variables from .env files,
with a hierarchical loading pattern where local overrides take precedence over default values.

"""

import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from .env import get_env_var, get_env_bool, get_env_int

***REMOVED*** Configure basic logging first for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** DEFAULT SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Database settings (for user management)
DEFAULT_DATABASE_URL = get_env_var(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/next_watch"
)

***REMOVED*** Debug: Log what DATABASE_URL was loaded
logger.info(f"DATABASE_URL loaded: {DEFAULT_DATABASE_URL}")

***REMOVED*** API settings
DEFAULT_API_PORT = get_env_int("AUTH_API_PORT", 8003)
DEFAULT_CORS_ORIGINS = get_env_var("CORS_ORIGINS", "*")

***REMOVED*** Logging and debugging
DEFAULT_LOG_LEVEL = get_env_var("LOG_LEVEL", "INFO")
DEFAULT_DEBUG = get_env_bool("DEBUG", False)
DEFAULT_LOGS_DIR = Path(get_env_var("LOGS_DIR", "logs"))

***REMOVED*** Performance monitoring
DEFAULT_ENABLE_PERFORMANCE_METRICS = get_env_bool("ENABLE_PERFORMANCE_METRICS", False)

***REMOVED*** Authentication settings
DEFAULT_JWT_SECRET = get_env_var("JWT_SECRET", "change_this_in_production_very_important")
DEFAULT_JWT_ALGORITHM = get_env_var("JWT_ALGORITHM", "HS256")
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = get_env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = get_env_int("REFRESH_TOKEN_EXPIRE_DAYS", 7)
DEFAULT_JWT_JWK_ROTATION_INTERVAL = get_env_int("JWT_JWK_ROTATION_INTERVAL", 86400)  ***REMOVED*** 24 hours

***REMOVED*** Security settings
DEFAULT_ALLOWED_HOSTS = get_env_var("ALLOWED_HOSTS", "localhost,127.0.0.1,auth-api")

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** CONFIGURATION CLASS
***REMOVED*** ------------------------------------------------------------------------------


class Config:
    """Configuration class for the authentication API."""

    database_url: str
    api_port: int
    log_level: str
    debug: bool
    cors_origins: List[str]
    enable_performance_metrics: bool
    logs_dir: Path
    ***REMOVED*** JWT settings
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    jwt_jwk: Optional[Dict[str, Any]]
    jwt_jwk_rotation_interval: int
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
        database_url: str = DEFAULT_DATABASE_URL,
        api_port: int = DEFAULT_API_PORT,
        log_level: str = DEFAULT_LOG_LEVEL,
        debug: bool = DEFAULT_DEBUG,
        cors_origins: str = DEFAULT_CORS_ORIGINS,
        enable_performance_metrics: bool = DEFAULT_ENABLE_PERFORMANCE_METRICS,
        logs_dir: Path = DEFAULT_LOGS_DIR,
        jwt_secret: str = DEFAULT_JWT_SECRET,
        jwt_algorithm: str = DEFAULT_JWT_ALGORITHM,
        access_token_expire_minutes: int = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days: int = DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
        jwt_jwk_rotation_interval: int = DEFAULT_JWT_JWK_ROTATION_INTERVAL,
        allowed_hosts: str = DEFAULT_ALLOWED_HOSTS,
    ):
        """Initialize authentication configuration.

        Args:
            database_url: URL for database connection
            api_port: Port for the auth API server
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            debug: Whether to enable debug mode
            cors_origins: Comma-separated list of allowed origins for CORS
            enable_performance_metrics: Whether to enable performance metrics
            logs_dir: Directory to store log files
            jwt_secret: Secret key for JWT token generation
            jwt_algorithm: Algorithm for JWT token generation
            access_token_expire_minutes: Minutes until access token expires
            refresh_token_expire_days: Days until refresh token expires
            jwt_jwk_rotation_interval: Interval in seconds for JWK rotation
            allowed_hosts: Comma-separated list of allowed hosts
        """
        ***REMOVED*** In production, force debug to False
        if get_env_var("ENVIRONMENT", "development") == "production":
            debug = False

        self.database_url = database_url
        self.api_port = api_port
        self.log_level = log_level
        self.debug = debug
        self.cors_origins = (
            [origin.strip() for origin in cors_origins.split(",")] if cors_origins != "*" else ["*"]
        )
        self.enable_performance_metrics = enable_performance_metrics
        self.logs_dir = logs_dir

        ***REMOVED*** JWT settings
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.jwt_jwk_rotation_interval = jwt_jwk_rotation_interval

        ***REMOVED*** Parse JWK if available
        self.jwt_jwk = None
        if jwk_str := get_env_var("JWT_JWK", ""):
            try:
                self.jwt_jwk = json.loads(jwk_str)
                logger.info("JWK configuration loaded successfully")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JWK configuration: {e}")
                if not self.debug:
                    raise ValueError("Invalid JWK configuration in production environment")

        ***REMOVED*** Log configuration
        logger.info(
            f"Initializing auth configuration with environment: {get_env_var('ENVIRONMENT', 'development')}"
        )
        logger.info(f"Database URL: {self._mask_database_password(self.database_url)}")
        logger.info(f"Debug mode: {self.debug}")
        logger.info(f"JWT algorithm: {self.jwt_algorithm}")
        logger.info(f"JWK enabled: {self.jwt_jwk is not None}")

        ***REMOVED*** Warn if using default JWT secret in production
        if self.jwt_secret == DEFAULT_JWT_SECRET and not self.debug:
            logger.warning(
                "WARNING: Using default JWT_SECRET in production environment. "
                "This is insecure. Set a proper JWT_SECRET environment variable."
            )

        ***REMOVED*** Security settings
        self.allowed_hosts = (
            [host.strip() for host in allowed_hosts.split(",")] if allowed_hosts != "*" else ["*"]
        )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return get_env_var("ENVIRONMENT", "development") == "production"

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
            f"Config(database_url={masked_url}, "
            f"api_port={self.api_port}, "
            f"log_level={self.log_level}, "
            f"debug={self.debug}, "
            f"cors_origins={self.cors_origins}, "
            f"logs_dir={self.logs_dir}, "
            f"enable_performance_metrics={self.enable_performance_metrics}, "
            f"jwt_algorithm={self.jwt_algorithm}, "
            f"access_token_expire_minutes={self.access_token_expire_minutes}, "
            f"refresh_token_expire_days={self.refresh_token_expire_days}, "
            f"jwt_jwk_enabled={self.jwt_jwk is not None}, "
            f"allowed_hosts={self.allowed_hosts})"
        )


***REMOVED*** Create a singleton instance to be imported elsewhere
settings = Config()
