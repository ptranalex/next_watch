"""Configuration settings for the BFF service."""

import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

***REMOVED*** Configure basic logging first for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** DEFAULT SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** API settings
DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")
DEFAULT_PORT = int(os.getenv("PORT", "8001"))
DEFAULT_CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

***REMOVED*** Logging and debugging
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEFAULT_DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DEFAULT_LOGS_DIR = os.getenv("LOGS_DIR", "logs")

***REMOVED*** Performance monitoring
DEFAULT_ENABLE_PERFORMANCE_METRICS = (
    os.getenv("ENABLE_PERFORMANCE_METRICS", "false").lower() == "true"
)

***REMOVED*** Backend API settings
DEFAULT_BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
DEFAULT_BACKEND_API_TIMEOUT = int(os.getenv("BACKEND_API_TIMEOUT", "30"))

***REMOVED*** Redis settings
DEFAULT_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  ***REMOVED*** 5 minutes

***REMOVED*** Authentication settings
DEFAULT_JWT_SECRET = os.getenv("JWT_SECRET")
DEFAULT_AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8003")


***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** CONFIGURATION CLASS
***REMOVED*** ------------------------------------------------------------------------------


class Config:
    """Configuration class for the BFF service."""

    host: str
    port: int
    log_level: str
    debug: bool
    cors_origins: List[str]
    enable_performance_metrics: bool
    log_dir: str
    backend_api_url: str
    backend_api_timeout: int
    redis_url: str
    cache_ttl: int
    jwt_secret: Optional[str]
    auth_service_url: str

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
        log_level: str = DEFAULT_LOG_LEVEL,
        debug: bool = DEFAULT_DEBUG,
        cors_origins: str = DEFAULT_CORS_ORIGINS,
        enable_performance_metrics: bool = DEFAULT_ENABLE_PERFORMANCE_METRICS,
        log_dir: str = DEFAULT_LOGS_DIR,
        backend_api_url: str = DEFAULT_BACKEND_API_URL,
        backend_api_timeout: int = DEFAULT_BACKEND_API_TIMEOUT,
        redis_url: str = DEFAULT_REDIS_URL,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        jwt_secret: Optional[str] = DEFAULT_JWT_SECRET,
        auth_service_url: str = DEFAULT_AUTH_SERVICE_URL,
    ):
        """Initialize BFF configuration.

        Args:
            host: Host for the BFF server
            port: Port for the BFF server
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            debug: Whether to enable debug mode
            cors_origins: Comma-separated list of allowed origins for CORS
            enable_performance_metrics: Whether to enable performance metrics
            log_dir: Directory to store log files
            backend_api_url: URL for backend API service
            backend_api_timeout: Timeout for backend API requests in seconds
            redis_url: URL for Redis connection
            cache_ttl: Cache TTL in seconds
            jwt_secret: Secret key for JWT token validation
            auth_service_url: URL for authentication service
        """
        ***REMOVED*** In production, force debug to False
        if os.getenv("ENVIRONMENT") == "production":
            debug = False

        self.host = host
        self.port = port
        self.log_level = log_level
        self.debug = debug
        self.cors_origins = (
            [origin.strip() for origin in cors_origins.split(",")]
            if cors_origins != "*"
            else ["*"]
        )
        self.enable_performance_metrics = enable_performance_metrics
        self.log_dir = log_dir

        ***REMOVED*** Backend API settings
        self.backend_api_url = backend_api_url.rstrip("/")
        self.backend_api_timeout = backend_api_timeout

        ***REMOVED*** Redis settings
        self.redis_url = redis_url
        self.cache_ttl = cache_ttl

        ***REMOVED*** Authentication settings
        self.jwt_secret = jwt_secret
        self.auth_service_url = auth_service_url.rstrip("/")

        ***REMOVED*** Derived settings
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.is_production = self.environment == "production"
        self.is_development = self.environment == "development"

        ***REMOVED*** Log configuration
        logger.info(
            f"Initializing BFF configuration with environment: {self.environment}"
        )
        logger.info(f"Backend API URL: {self.backend_api_url}")
        logger.info(f"Auth service URL: {self.auth_service_url}")
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

        return (
            f"Config(host={self.host}, "
            f"port={self.port}, "
            f"log_level={self.log_level}, "
            f"debug={self.debug}, "
            f"cors_origins={self.cors_origins}, "
            f"backend_api_url={self.backend_api_url}, "
            f"environment={self.environment}, "
            f"jwt_secret={masked_jwt})"
        )


***REMOVED*** Create a singleton instance to be imported elsewhere
settings = Config()
