"""Configuration settings for the movie storage module."""

import os
from pathlib import Path
from typing import Optional

***REMOVED*** Load environment variables from .env files
try:
    from dotenv import load_dotenv  ***REMOVED*** type: ignore

    ***REMOVED*** Find the module root directory (looking for .env file)
    module_root = Path(__file__).parent.parent.parent
    env_path = module_root / ".env"
    env_local_path = module_root / ".env.local"

    ***REMOVED*** Load .env first (default values)
    load_dotenv(dotenv_path=env_path)

    ***REMOVED*** Then override with .env.local if it exists (custom values)
    if env_local_path.exists():
        load_dotenv(dotenv_path=env_local_path, override=True)
except ImportError:
    print("python-dotenv not installed. Using environment variables only.")

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** DATABASE SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Database URLs and connection settings
DEFAULT_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///movies.db")
DEFAULT_DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"
DEFAULT_DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
DEFAULT_DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
DEFAULT_DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** LOGGING SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEFAULT_SQL_LOG_LEVEL = os.getenv("SQL_LOG_LEVEL", "WARNING")

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** CONFIGURATION CLASS
***REMOVED*** ------------------------------------------------------------------------------


class Config:
    """Configuration class for the movie storage module."""

    database_url: str
    database_echo: bool
    database_pool_size: int
    database_max_overflow: int
    database_pool_timeout: int
    log_level: str
    sql_log_level: str

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
        database_echo: bool = DEFAULT_DATABASE_ECHO,
        database_pool_size: int = DEFAULT_DATABASE_POOL_SIZE,
        database_max_overflow: int = DEFAULT_DATABASE_MAX_OVERFLOW,
        database_pool_timeout: int = DEFAULT_DATABASE_POOL_TIMEOUT,
        log_level: str = DEFAULT_LOG_LEVEL,
        sql_log_level: str = DEFAULT_SQL_LOG_LEVEL,
    ):
        """Initialize configuration.

        Args:
            database_url: Database connection URL
            database_echo: Whether to echo SQL commands
            database_pool_size: Connection pool size
            database_max_overflow: Maximum overflow connections
            database_pool_timeout: Pool timeout in seconds
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            sql_log_level: SQL-specific logging level
        """
        self.database_url = database_url
        self.database_echo = database_echo
        self.database_pool_size = database_pool_size
        self.database_max_overflow = database_max_overflow
        self.database_pool_timeout = database_pool_timeout
        self.log_level = log_level
        self.sql_log_level = sql_log_level

    def __str__(self) -> str:
        """Return a string representation of the Config instance."""
        ***REMOVED*** Mask password in database_url for security
        masked_url = self._mask_database_password(self.database_url)

        return (
            f"Config(database_url={masked_url}, "
            f"database_echo={self.database_echo}, "
            f"database_pool_size={self.database_pool_size}, "
            f"database_max_overflow={self.database_max_overflow}, "
            f"database_pool_timeout={self.database_pool_timeout}, "
            f"log_level={self.log_level}, "
            f"sql_log_level={self.sql_log_level})"
        )

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
