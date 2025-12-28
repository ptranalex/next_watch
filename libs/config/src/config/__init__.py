"""NextWatch configuration library.

Provides a simplified, standardized way to manage configuration across NextWatch services.
"""

***REMOVED*** Base configuration classes
from config.base.config import BaseConfig, ServiceConfig, WorkerConfig

***REMOVED*** Configuration profiles
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

***REMOVED*** Service-specific configuration mixins
from config.services.auth import AuthConfigMixin
from config.services.cache import CacheConfigMixin
from config.services.database import DatabaseConfigMixin

__all__ = [
    ***REMOVED*** Base classes
    "BaseConfig",
    "ServiceConfig",
    "WorkerConfig",
    ***REMOVED*** Mixins
    "AuthConfigMixin",
    "CacheConfigMixin",
    "DatabaseConfigMixin",
    ***REMOVED*** Profiles
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
    ***REMOVED*** Profile utilities
    "apply_profiles",
    "get_profile_by_name",
]
