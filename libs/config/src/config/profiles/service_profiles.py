"""Service configuration profiles.

Provides predefined configuration profiles for different service types and
deployment scenarios with a simplified approach.
"""

from typing import Any


class ConfigProfile:
    """Base configuration profile class.

    Provides a base class for configuration profiles that can be applied to
    service configurations.
    """

    name: str
    description: str
    overrides: dict[str, Any]

    def __init__(self, name: str, description: str, overrides: dict[str, Any]) -> None:
        """Initialize configuration profile.

        Args:
            name: Profile name
            description: Profile description
            overrides: Configuration overrides
        """
        self.name = name
        self.description = description
        self.overrides = overrides

    def apply_to_config(self, config: Any) -> None:
        """Apply profile overrides to configuration.

        Args:
            config: Configuration object to apply overrides to
        """
        for key, value in self.overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)

    def __str__(self) -> str:
        """String representation of profile."""
        return f"ConfigProfile({self.name}): {self.description}"


***REMOVED*** Development profiles
DevelopmentProfile = ConfigProfile(
    name="Development",
    description="Development environment with debugging enabled",
    overrides={
        "environment": "development",
        "debug": True,
        "log_level": "DEBUG",
    },
)

TestProfile = ConfigProfile(
    name="Test",
    description="Test environment for unit and integration tests",
    overrides={
        "environment": "test",
        "debug": True,
        "log_level": "DEBUG",
    },
)

***REMOVED*** Production profiles
ProductionProfile = ConfigProfile(
    name="Production",
    description="Production environment with security optimizations",
    overrides={
        "environment": "production",
        "debug": False,
        "log_level": "INFO",
    },
)

***REMOVED*** Service-specific profiles
ApiServiceProfile = ConfigProfile(
    name="ApiService",
    description="API service with standard HTTP settings",
    overrides={
        "cors_origins": ["*"],  ***REMOVED*** Should be overridden in production
        "allowed_hosts": ["*"],  ***REMOVED*** Should be overridden in production
    },
)

GatewayProfile = ConfigProfile(
    name="Gateway",
    description="API Gateway with optimized settings",
    overrides={
        "cors_origins": ["*"],  ***REMOVED*** Should be overridden in production
        "allowed_hosts": ["*"],  ***REMOVED*** Should be overridden in production
        "log_level": "INFO",  ***REMOVED*** Default to INFO level for gateways
    },
)

BackendServiceProfile = ConfigProfile(
    name="BackendService",
    description="Backend service with database and cache",
    overrides={
        "database_pool_size": 10,
        "redis_max_connections": 20,
        "cache_ttl_default": 600,  ***REMOVED*** 10 minutes
    },
)

WorkerServiceProfile = ConfigProfile(
    name="WorkerService",
    description="Worker service with task processing",
    overrides={
        "workers": 4,
        "max_concurrent_tasks": 20,
        "task_timeout_seconds": 600,  ***REMOVED*** 10 minutes
    },
)

***REMOVED*** Deployment profiles
LowResourceProfile = ConfigProfile(
    name="LowResource",
    description="Low resource usage for development or small deployments",
    overrides={
        "database_pool_size": 3,
        "database_max_overflow": 5,
        "redis_max_connections": 5,
        "workers": 2,
    },
)

HighPerformanceProfile = ConfigProfile(
    name="HighPerformance",
    description="High performance settings for production",
    overrides={
        "database_pool_size": 20,
        "database_max_overflow": 30,
        "redis_max_connections": 30,
        "workers": 8,
        "max_concurrent_tasks": 50,
    },
)


def apply_profiles(config: Any, *profiles: ConfigProfile) -> None:
    """Apply multiple configuration profiles in order.

    Args:
        config: Configuration object to apply profiles to
        *profiles: Profiles to apply in order
    """
    from config.logging import get_logger

    logger = get_logger(__name__)

    for profile in profiles:
        logger.debug(f"Applying profile: {profile.name}")
        profile.apply_to_config(config)

    ***REMOVED*** Apply environment-specific overrides last
    if hasattr(config, "environment"):
        env = config.environment
        if env == "development" and hasattr(config, "debug"):
            ***REMOVED*** Always enable debug in development unless explicitly overridden
            if not any(p.name == "Production" for p in profiles):
                config.debug = True

        if env == "production" and hasattr(config, "debug"):
            ***REMOVED*** Always disable debug in production
            config.debug = False


def get_profile_by_name(name: str) -> ConfigProfile | None:
    """Get profile by name.

    Args:
        name: Profile name

    Returns:
        Profile or None if not found
    """
    profiles = {
        "development": DevelopmentProfile,
        "test": TestProfile,
        "production": ProductionProfile,
        "api": ApiServiceProfile,
        "gateway": GatewayProfile,
        "backend": BackendServiceProfile,
        "worker": WorkerServiceProfile,
        "low_resource": LowResourceProfile,
        "high_performance": HighPerformanceProfile,
    }

    return profiles.get(name.lower())
