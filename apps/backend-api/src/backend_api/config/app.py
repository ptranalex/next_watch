"""Configuration settings for the backend API."""

import os
import sys
from pathlib import Path
from typing import List
import logging

***REMOVED*** Configure basic logging first for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

***REMOVED*** Note: Environment variables are now loaded in main.py

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** DEFAULT SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Database settings
DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/next_watch"
)

***REMOVED*** API settings
DEFAULT_API_PORT = int(os.getenv("API_PORT", "8000"))
DEFAULT_CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

***REMOVED*** Logging and debugging
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEFAULT_DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DEFAULT_LOGS_DIR = os.getenv("LOGS_DIR", "logs")

***REMOVED*** Performance monitoring
DEFAULT_ENABLE_PERFORMANCE_METRICS = (
    os.getenv("ENABLE_PERFORMANCE_METRICS", "false").lower() == "true"
)

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** CONFIGURATION CLASS
***REMOVED*** ------------------------------------------------------------------------------


class Settings:
    """Configuration class for the backend API."""

    database_url: str
    api_port: int
    log_level: str
    debug: bool
    cors_origins: List[str]
    enable_performance_metrics: bool
    log_dir: str

    ***REMOVED*** Singleton instance
    _instance = None

    @classmethod
    def get_instance(cls) -> "Settings":
        """Get the singleton instance of Settings.

        Returns:
            The global Settings instance
        """
        if cls._instance is None:
            cls._instance = Settings()
        return cls._instance

    def __init__(
        self,
        database_url: str = DEFAULT_DATABASE_URL,
        api_port: int = DEFAULT_API_PORT,
        log_level: str = DEFAULT_LOG_LEVEL,
        debug: bool = DEFAULT_DEBUG,
        cors_origins: str = DEFAULT_CORS_ORIGINS,
        enable_performance_metrics: bool = DEFAULT_ENABLE_PERFORMANCE_METRICS,
        log_dir: str = DEFAULT_LOGS_DIR,
    ):
        """Initialize configuration.

        Args:
            database_url: URL for database connection
            api_port: Port for the API server
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            debug: Whether to enable debug mode
            cors_origins: Comma-separated list of allowed origins for CORS
            enable_performance_metrics: Whether to enable performance metrics
            log_dir: Directory to store log files
        """
        self.database_url = database_url
        self.api_port = api_port
        self.log_level = log_level
        self.debug = debug
        self.cors_origins = (
            [origin.strip() for origin in cors_origins.split(",")]
            if cors_origins != "*"
            else ["*"]
        )
        self.enable_performance_metrics = enable_performance_metrics
        self.log_dir = log_dir

    def __str__(self) -> str:
        """Return a string representation of the Settings instance with sensitive data masked.

        Returns:
            String representation of Settings
        """
        ***REMOVED*** Mask sensitive information in the connection string
        masked_url = self.database_url
        if "@" in masked_url and "://" in masked_url:
            protocol_part = masked_url.split("://")[0]
            auth_part = masked_url.split("://")[1].split("@")[0]
            masked_auth = auth_part.split(":")[0] + ":****"
            remaining_part = masked_url.split("@", 1)[1]
            masked_url = f"{protocol_part}://{masked_auth}@{remaining_part}"

        return (
            f"Settings(database_url={masked_url}, "
            f"api_port={self.api_port}, "
            f"log_level={self.log_level}, "
            f"debug={self.debug}, "
            f"cors_origins={self.cors_origins}, "
            f"log_dir={self.log_dir}, "
            f"enable_performance_metrics={self.enable_performance_metrics})"
        )


***REMOVED*** Create a singleton instance to be imported elsewhere
settings = Settings()
