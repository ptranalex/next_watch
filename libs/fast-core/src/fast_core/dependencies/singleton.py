"""Singleton dependency management for Fast Core.

This module provides utilities for managing singleton dependencies in FastAPI applications,
allowing for performance optimization and resource management while maintaining clean
dependency injection patterns.
"""

import inspect
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any, TypeVar

from config.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

***REMOVED*** Global singleton registry
_singleton_registry: dict[str, Any] = {}
_singleton_factories: dict[str, Callable] = {}
_singleton_lifecycle_hooks: dict[str, dict[str, Callable]] = {}


class SingletonConfig:
    """Configuration for singleton dependencies."""

    def __init__(
        self,
        name: str,
        factory: Callable[..., T],
        lifecycle: str = "app",
        cleanup_on_shutdown: bool = True,
        dependencies: list | None = None,
    ):
        """Initialize singleton configuration.

        Args:
            name: Unique name for the singleton
            factory: Factory function to create the singleton instance
            lifecycle: Lifecycle scope ('app', 'request', 'session')
            cleanup_on_shutdown: Whether to cleanup on app shutdown
            dependencies: List of dependency functions for the factory
        """
        self.name = name
        self.factory = factory
        self.lifecycle = lifecycle
        self.cleanup_on_shutdown = cleanup_on_shutdown
        self.dependencies = dependencies or []


class SingletonManager:
    """Manages singleton instances and their lifecycle."""

    def __init__(self) -> None:
        self._instances: dict[str, Any] = {}
        self._factories: dict[str, SingletonConfig] = {}
        self._cleanup_hooks: dict[str, Callable] = {}

    def register(self, config: SingletonConfig) -> None:
        """Register a singleton configuration.

        Args:
            config: Singleton configuration
        """
        logger.info(f"Registering singleton: {config.name}")
        self._factories[config.name] = config

    def get_or_create(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Get existing singleton or create new one.

        Args:
            name: Singleton name
            *args: Arguments for factory function
            **kwargs: Keyword arguments for factory function

        Returns:
            Singleton instance

        Raises:
            ValueError: If singleton is not registered
        """
        if name not in self._factories:
            raise ValueError(f"Singleton '{name}' not registered")

        if name not in self._instances:
            config = self._factories[name]
            logger.info(f"Creating singleton instance: {name}")

            ***REMOVED*** Resolve dependencies
            resolved_deps = []
            for dep in config.dependencies:
                if callable(dep):
                    resolved_deps.append(dep())
                else:
                    resolved_deps.append(dep)

            ***REMOVED*** Create instance
            instance = config.factory(*resolved_deps, *args, **kwargs)
            self._instances[name] = instance

            ***REMOVED*** Register cleanup hook if needed
            if (
                config.cleanup_on_shutdown
                and hasattr(instance, "close")
                and callable(getattr(instance, "close", None))
            ):
                self._cleanup_hooks[name] = getattr(instance, "close")

        return self._instances[name]

    async def cleanup(self, name: str | None = None) -> None:
        """Cleanup singleton instances.

        Args:
            name: Specific singleton to cleanup, or None for all
        """
        if name:
            await self._cleanup_single(name)
        else:
            ***REMOVED*** Cleanup all singletons
            for singleton_name in list(self._instances.keys()):
                await self._cleanup_single(singleton_name)

    async def _cleanup_single(self, name: str) -> None:
        """Cleanup a single singleton instance.

        Args:
            name: Singleton name
        """
        if name in self._instances:
            logger.info(f"Cleaning up singleton: {name}")

            ***REMOVED*** Call cleanup hook if available
            if name in self._cleanup_hooks:
                cleanup_func = self._cleanup_hooks[name]
                try:
                    if inspect.iscoroutinefunction(cleanup_func):
                        await cleanup_func()
                    else:
                        cleanup_func()
                except Exception as e:
                    logger.error(f"Error cleaning up singleton {name}: {e}")

            ***REMOVED*** Remove from registry
            del self._instances[name]
            if name in self._cleanup_hooks:
                del self._cleanup_hooks[name]

    def list_singletons(self) -> dict[str, str]:
        """List all registered singletons and their status.

        Returns:
            Dictionary mapping singleton names to their status
        """
        result = {}
        for name in self._factories:
            status = "active" if name in self._instances else "registered"
            result[name] = status
        return result


***REMOVED*** Global singleton manager instance
_singleton_manager = SingletonManager()


def register_singleton(
    name: str,
    factory: Callable[..., T],
    lifecycle: str = "app",
    cleanup_on_shutdown: bool = True,
    dependencies: list | None = None,
) -> None:
    """Register a singleton factory function.

    Args:
        name: Unique name for the singleton
        factory: Factory function to create the singleton
        lifecycle: Lifecycle scope ('app', 'request', 'session')
        cleanup_on_shutdown: Whether to cleanup on app shutdown
        dependencies: List of dependency functions for the factory
    """
    config = SingletonConfig(
        name=name,
        factory=factory,
        lifecycle=lifecycle,
        cleanup_on_shutdown=cleanup_on_shutdown,
        dependencies=dependencies,
    )
    _singleton_manager.register(config)


def get_singleton_client(
    name: str,
    lifecycle: str = "app",
    cleanup_on_shutdown: bool = True,
    dependencies: list | None = None,
) -> Callable[[Callable[..., T]], Callable[[], Any]]:
    """Decorator to register a singleton client factory.

    Args:
        name: Unique name for the singleton
        lifecycle: Lifecycle scope ('app', 'request', 'session')
        cleanup_on_shutdown: Whether to cleanup on app shutdown
        dependencies: List of dependency functions for the factory

    Returns:
        Decorator function
    """

    def decorator(factory_func: Callable[..., T]) -> Callable[[], Any]:
        ***REMOVED*** Register the singleton
        register_singleton(
            name=name,
            factory=factory_func,
            lifecycle=lifecycle,
            cleanup_on_shutdown=cleanup_on_shutdown,
            dependencies=dependencies,
        )

        ***REMOVED*** Create dependency function
        def dependency() -> Any:
            return _singleton_manager.get_or_create(name)

        ***REMOVED*** Preserve function metadata
        dependency.__name__ = f"get_{name}_singleton"
        dependency.__doc__ = f"Get {name} singleton instance"

        return dependency

    return decorator


def get_singleton(name: str) -> Callable[[], Any]:
    """Get a dependency function for a registered singleton.

    Args:
        name: Singleton name

    Returns:
        Dependency function that returns the singleton instance
    """

    def dependency() -> Any:
        return _singleton_manager.get_or_create(name)

    dependency.__name__ = f"get_{name}_singleton"
    dependency.__doc__ = f"Get {name} singleton instance"

    return dependency


async def cleanup_singletons(name: str | None = None) -> None:
    """Cleanup singleton instances.

    Args:
        name: Specific singleton to cleanup, or None for all
    """
    await _singleton_manager.cleanup(name)


def list_singletons() -> dict[str, str]:
    """List all registered singletons and their status.

    Returns:
        Dictionary mapping singleton names to their status
    """
    return _singleton_manager.list_singletons()


***REMOVED*** Application lifecycle integration
@asynccontextmanager
async def singleton_lifespan(app: Any) -> AsyncGenerator[None, None]:
    """Application lifespan manager for singleton cleanup.

    This should be used as the lifespan parameter in FastAPI app creation
    to ensure proper singleton cleanup on shutdown.
    """
    ***REMOVED*** Startup
    logger.info("Application startup - singletons ready")
    yield
    ***REMOVED*** Shutdown
    logger.info("Application shutdown - cleaning up singletons")
    await cleanup_singletons()


***REMOVED*** Convenience functions for common patterns
def create_singleton_dependency(
    name: str,
    factory: Callable[..., T],
    dependencies: list | None = None,
) -> Callable[[], T]:
    """Create a singleton dependency function.

    Args:
        name: Unique name for the singleton
        factory: Factory function to create the singleton
        dependencies: List of dependency functions for the factory

    Returns:
        Dependency function that can be used with FastAPI Depends()
    """
    register_singleton(name=name, factory=factory, dependencies=dependencies)
    return get_singleton(name)


***REMOVED*** Export all public functions
__all__ = [
    "SingletonConfig",
    "SingletonManager",
    "register_singleton",
    "get_singleton_client",
    "get_singleton",
    "cleanup_singletons",
    "list_singletons",
    "singleton_lifespan",
    "create_singleton_dependency",
]
