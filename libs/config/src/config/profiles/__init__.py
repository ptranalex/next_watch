"""Configuration profiles for NextWatch services.

This module provides configuration profiles for different service types and deployment scenarios.
"""

from .service_profiles import (
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

__all__ = [
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
    "apply_profiles",
    "get_profile_by_name",
]
