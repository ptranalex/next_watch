"""Service-specific configuration mixins for NextWatch services.

This module provides composable configuration components that services can
mix and match based on their infrastructure needs.

Available mixins:
- DatabaseConfigMixin: PostgreSQL database configuration
- CacheConfigMixin: Redis cache configuration
- AuthConfigMixin: JWT authentication configuration
- MonitoringConfigMixin: Logging and metrics configuration
- VectorDBConfigMixin: Qdrant vector database configuration
"""

from config.services.auth import AuthConfigMixin
from config.services.cache import CacheConfigMixin
from config.services.database import DatabaseConfigMixin
from config.services.monitoring import MonitoringConfigMixin
from config.services.vector import VectorDBConfigMixin

__all__ = [
    "DatabaseConfigMixin",
    "CacheConfigMixin",
    "AuthConfigMixin",
    "MonitoringConfigMixin",
    "VectorDBConfigMixin",
]
