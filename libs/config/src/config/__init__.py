"""NextWatch configuration library.

Provides a simplified, standardized way to manage configuration across NextWatch services.
"""

# Base configuration classes
from config.base.config import BaseConfig, ServiceConfig, WorkerConfig

# Configuration profiles
from config.profiles import (
    ApiServiceProfile,
    BackendServiceProfile,
    ConfigProfile,
    DevelopmentProfile,
    GatewayProfile,
    HighPerformanceProfile,
    LowResourceProfile,
    ProductionProfile,
    TestProfile,
    WorkerServiceProfile,
    apply_profiles,
    get_profile_by_name,
)

# Service-specific configuration mixins
from config.services.auth import AuthConfigMixin
from config.services.cache import CacheConfigMixin
from config.services.database import DatabaseConfigMixin

__all__ = [
    # Base classes
    "BaseConfig",
    "ServiceConfig",
    "WorkerConfig",
    # Mixins
    "AuthConfigMixin",
    "CacheConfigMixin",
    "DatabaseConfigMixin",
    # Profiles
    "ConfigProfile",
    "ApiServiceProfile",
    "BackendServiceProfile",
    "DevelopmentProfile",
    "GatewayProfile",
    "HighPerformanceProfile",
    "LowResourceProfile",
    "ProductionProfile",
    "TestProfile",
    "WorkerServiceProfile",
    # Profile utilities
    "apply_profiles",
    "get_profile_by_name",
]
