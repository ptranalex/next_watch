"""Configuration settings for the movie storage module."""

from typing import TypedDict

from movie_storage.config.env import get_env_bool, get_env_int, get_env_var

# ------------------------------------------------------------------------------
# TYPE DEFINITIONS
# ------------------------------------------------------------------------------


class ConfigDict(TypedDict, total=False):
    """Type definition for configuration dictionary."""

    database_url: str
    database_echo: bool
    database_pool_size: int
    database_max_overflow: int
    database_pool_timeout: int
    log_level: str
    sql_log_level: str


# ------------------------------------------------------------------------------
# DEFAULT CONFIGURATION VALUES
# ------------------------------------------------------------------------------

# Database URLs and connection settings
DEFAULT_DATABASE_URL = get_env_var("DATABASE_URL", "sqlite:///movies.db")
DEFAULT_DATABASE_ECHO = get_env_bool("DATABASE_ECHO", False)
DEFAULT_DATABASE_POOL_SIZE = get_env_int("DATABASE_POOL_SIZE", 5)
DEFAULT_DATABASE_MAX_OVERFLOW = get_env_int("DATABASE_MAX_OVERFLOW", 10)
DEFAULT_DATABASE_POOL_TIMEOUT = get_env_int("DATABASE_POOL_TIMEOUT", 30)

# Logging settings
DEFAULT_LOG_LEVEL = get_env_var("LOG_LEVEL", "INFO")
DEFAULT_SQL_LOG_LEVEL = get_env_var("SQL_LOG_LEVEL", "WARNING")

# ------------------------------------------------------------------------------
# CONFIGURATION CLASS
# ------------------------------------------------------------------------------


class Config:
    """Configuration class for the movie storage module."""

    database_url: str
    database_echo: bool
    database_pool_size: int
    database_max_overflow: int
    database_pool_timeout: int
    log_level: str
    sql_log_level: str

    # Singleton instance
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
        """Return a comprehensive multi-line string representation of the Config instance."""
        # Mask password in database_url for security
        masked_url = self._mask_database_password(self.database_url)

        return f"""Movie Storage Configuration:
  Database Settings:
    URL: {masked_url}
    Echo SQL: {self.database_echo}
    Pool Size: {self.database_pool_size}
    Max Overflow: {self.database_max_overflow}
    Pool Timeout: {self.database_pool_timeout}s

  Logging Settings:
    Log Level: {self.log_level}
    SQL Log Level: {self.sql_log_level}"""

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
            # Simple approach to mask password in standard SQLAlchemy URLs
            if "@" in url and ":" in url:
                # Split URL into components
                protocol_part, rest = url.split("://", 1)
                if "@" in rest:
                    auth_part, host_part = rest.split("@", 1)
                    if ":" in auth_part:
                        username, password = auth_part.split(":", 1)
                        # Replace password with asterisks
                        return f"{protocol_part}://{username}:******@{host_part}"
        except Exception:
            pass

        return url
