"""Core application configuration for BFF service."""

import os
from typing import Optional
from functools import lru_cache

try:
    from dotenv import load_dotenv

    load_dotenv(".env.local", override=False)
    load_dotenv(".env", override=False)
except ImportError:
    pass

***REMOVED*** Default configuration constants
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8001
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_BACKEND_API_URL = "http://localhost:8000"
DEFAULT_REDIS_URL = "redis://localhost:6379"
DEFAULT_CACHE_TTL = 300  ***REMOVED*** 5 minutes


class Config:
    """Configuration class for BFF application."""

    _instance: Optional["Config"] = None

    def __init__(
        self,
        host: str = os.getenv("HOST", DEFAULT_HOST),
        port: int = int(os.getenv("PORT", str(DEFAULT_PORT))),
        log_level: str = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL),
        backend_api_url: str = os.getenv("BACKEND_API_URL", DEFAULT_BACKEND_API_URL),
        backend_api_timeout: int = int(os.getenv("BACKEND_API_TIMEOUT", "30")),
        redis_url: str = os.getenv("REDIS_URL", DEFAULT_REDIS_URL),
        cache_ttl: int = int(os.getenv("CACHE_TTL", str(DEFAULT_CACHE_TTL))),
        jwt_secret: Optional[str] = os.getenv("JWT_SECRET"),
        environment: str = os.getenv("ENVIRONMENT", "development"),
        debug: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
    ):
        """Initialize configuration with environment variables and defaults."""
        self.host = host
        self.port = port
        self.log_level = log_level
        self.backend_api_url = backend_api_url.rstrip("/")
        self.backend_api_timeout = backend_api_timeout
        self.redis_url = redis_url
        self.cache_ttl = cache_ttl
        self.jwt_secret = jwt_secret
        self.environment = environment
        self.debug = debug

        ***REMOVED*** Derived settings
        self.is_production = environment == "production"
        self.is_development = environment == "development"

    @classmethod
    def get_instance(cls) -> "Config":
        """Get or create singleton instance of configuration."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __repr__(self) -> str:
        """String representation masking sensitive information."""
        return (
            f"Config("
            f"host={self.host!r}, "
            f"port={self.port}, "
            f"log_level={self.log_level!r}, "
            f"backend_api_url={self.backend_api_url!r}, "
            f"environment={self.environment!r}, "
            f"debug={self.debug}, "
            f"jwt_secret={'***' if self.jwt_secret else None}"
            f")"
        )


@lru_cache()
def get_config() -> Config:
    """Cached function to get configuration instance."""
    return Config.get_instance()
