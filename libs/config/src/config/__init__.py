"""NextWatch Shared Configuration Library.

A unified configuration management library for the NextWatch monorepo that provides
consistent, type-safe, and production-ready configuration patterns across all services.

This library addresses configuration fragmentation by providing:
- Unified interface across all services
- Type safety with Pydantic
- Environment hierarchy with .env support
- Built-in security and secret masking
- Rich CLI integration
- Production-ready validation
"""

from config.base.config import BaseConfig, ServiceConfig, WorkerConfig
from config.env.loader import EnvironmentLoader, load_environment_for_service
from config.env.parser import get_env_var, get_env_bool, get_env_int
from config.logging import configure_logging, get_logger, COLOR_THEMES
from config.security.masking import mask_config_for_display
from config.services import (
    DatabaseConfigMixin,
    CacheConfigMixin,
    AuthConfigMixin,
    MonitoringConfigMixin,
    VectorDBConfigMixin,
)

__version__ = "0.1.0"

__all__ = [
    ***REMOVED*** Version
    "__version__",
    ***REMOVED*** Base configuration classes
    "BaseConfig",
    "ServiceConfig",
    "WorkerConfig",
    ***REMOVED*** Environment loading
    "EnvironmentLoader",
    "load_environment_for_service",
    ***REMOVED*** Environment parsing
    "get_env_var",
    "get_env_bool",
    "get_env_int",
    ***REMOVED*** Logging configuration
    "configure_logging",
    "get_logger",
    "COLOR_THEMES",
    ***REMOVED*** Security utilities
    "mask_config_for_display",
    ***REMOVED*** Service mixins
    "DatabaseConfigMixin",
    "CacheConfigMixin",
    "AuthConfigMixin",
    "MonitoringConfigMixin",
    "VectorDBConfigMixin",
]
