"""Tests for singleton dependency management."""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Any

from fast_core.dependencies.singleton import (
    SingletonConfig,
    SingletonManager,
    register_singleton,
    get_singleton_client,
    get_singleton,
    cleanup_singletons,
    list_singletons,
    create_singleton_dependency,
)


class MockClient:
    """Mock client for testing."""

    def __init__(self, name: str):
        self.name = name
        self.closed = False

    async def close(self) -> None:
        """Mock close method."""
        self.closed = True

    def __setattr__(self, name: str, value: Any) -> None:
        """Allow setting arbitrary attributes."""
        super().__setattr__(name, value)


class MockClientWithoutClose:
    """Mock client without close method."""

    def __init__(self, name: str):
        self.name = name


def create_mock_client(name: str = "test-client") -> MockClient:
    """Factory function for creating mock clients."""
    return MockClient(name)


def create_mock_client_without_close(name: str = "test-client") -> MockClientWithoutClose:
    """Factory function for creating mock clients without close method."""
    return MockClientWithoutClose(name)


class TestSingletonConfig:
    """Test SingletonConfig class."""

    def test_singleton_config_creation(self) -> None:
        """Test creating singleton configuration."""
        config = SingletonConfig(
            name="test-singleton",
            factory=create_mock_client,
            lifecycle="app",
            cleanup_on_shutdown=True,
            dependencies=[],
        )

        assert config.name == "test-singleton"
        assert config.factory == create_mock_client
        assert config.lifecycle == "app"
        assert config.cleanup_on_shutdown is True
        assert config.dependencies == []

    def test_singleton_config_defaults(self):
        """Test singleton configuration with defaults."""
        config = SingletonConfig(name="test", factory=create_mock_client)

        assert config.lifecycle == "app"
        assert config.cleanup_on_shutdown is True
        assert config.dependencies == []


class TestSingletonManager:
    """Test SingletonManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = SingletonManager()

    def test_register_singleton(self):
        """Test registering a singleton."""
        config = SingletonConfig(name="test", factory=create_mock_client)
        self.manager.register(config)

        assert "test" in self.manager._factories
        assert self.manager._factories["test"] == config

    def test_get_or_create_new_instance(self):
        """Test creating new singleton instance."""
        config = SingletonConfig(name="test", factory=create_mock_client)
        self.manager.register(config)

        instance = self.manager.get_or_create("test")

        assert isinstance(instance, MockClient)
        assert instance.name == "test-client"
        assert "test" in self.manager._instances

    def test_get_or_create_existing_instance(self):
        """Test getting existing singleton instance."""
        config = SingletonConfig(name="test", factory=create_mock_client)
        self.manager.register(config)

        instance1 = self.manager.get_or_create("test")
        instance2 = self.manager.get_or_create("test")

        assert instance1 is instance2  ***REMOVED*** Same instance

    def test_get_or_create_unregistered_singleton(self):
        """Test getting unregistered singleton raises error."""
        with pytest.raises(ValueError, match="Singleton 'unknown' not registered"):
            self.manager.get_or_create("unknown")

    def test_get_or_create_with_args(self):
        """Test creating singleton with arguments."""
        config = SingletonConfig(name="test", factory=create_mock_client)
        self.manager.register(config)

        instance = self.manager.get_or_create("test", "custom-name")

        assert instance.name == "custom-name"

    def test_get_or_create_with_dependencies(self):
        """Test creating singleton with dependencies."""

        def dependency_func():
            return "dependency-value"

        def factory_with_deps(dep_value: str, name: str = "test") -> MockClient:
            client = MockClient(name)
            client.dependency = dep_value
            return client

        config = SingletonConfig(
            name="test",
            factory=factory_with_deps,
            dependencies=[dependency_func],
        )
        self.manager.register(config)

        instance = self.manager.get_or_create("test")

        assert hasattr(instance, "dependency")
        assert instance.dependency == "dependency-value"

    @pytest.mark.asyncio
    async def test_cleanup_single_instance(self):
        """Test cleaning up single singleton instance."""
        config = SingletonConfig(name="test", factory=create_mock_client)
        self.manager.register(config)

        instance = self.manager.get_or_create("test")
        assert not instance.closed

        await self.manager.cleanup("test")

        assert instance.closed
        assert "test" not in self.manager._instances

    @pytest.mark.asyncio
    async def test_cleanup_all_instances(self):
        """Test cleaning up all singleton instances."""
        config1 = SingletonConfig(name="test1", factory=create_mock_client)
        config2 = SingletonConfig(name="test2", factory=create_mock_client)
        self.manager.register(config1)
        self.manager.register(config2)

        instance1 = self.manager.get_or_create("test1")
        instance2 = self.manager.get_or_create("test2")

        await self.manager.cleanup()

        assert instance1.closed
        assert instance2.closed
        assert len(self.manager._instances) == 0

    @pytest.mark.asyncio
    async def test_cleanup_instance_without_close(self):
        """Test cleaning up instance without close method."""
        config = SingletonConfig(name="test", factory=create_mock_client_without_close)
        self.manager.register(config)

        instance = self.manager.get_or_create("test")

        ***REMOVED*** Should not raise error
        await self.manager.cleanup("test")

        assert "test" not in self.manager._instances

    @pytest.mark.asyncio
    async def test_cleanup_with_async_close(self):
        """Test cleanup with async close method."""
        async_close_mock = AsyncMock()

        def create_async_client():
            client = MockClient("async-test")
            client.close = async_close_mock
            return client

        config = SingletonConfig(name="test", factory=create_async_client)
        self.manager.register(config)

        instance = self.manager.get_or_create("test")
        await self.manager.cleanup("test")

        async_close_mock.assert_called_once()

    def test_list_singletons(self):
        """Test listing singleton status."""
        config1 = SingletonConfig(name="test1", factory=create_mock_client)
        config2 = SingletonConfig(name="test2", factory=create_mock_client)
        self.manager.register(config1)
        self.manager.register(config2)

        ***REMOVED*** Create one instance
        self.manager.get_or_create("test1")

        status = self.manager.list_singletons()

        assert status["test1"] == "active"
        assert status["test2"] == "registered"


class TestSingletonFunctions:
    """Test singleton utility functions."""

    def setup_method(self):
        """Set up test fixtures."""
        ***REMOVED*** Clear global singleton manager
        from fast_core.dependencies.singleton import _singleton_manager

        _singleton_manager._instances.clear()
        _singleton_manager._factories.clear()
        _singleton_manager._cleanup_hooks.clear()

    def teardown_method(self):
        """Clean up after tests."""
        ***REMOVED*** Clear global singleton manager
        from fast_core.dependencies.singleton import _singleton_manager

        _singleton_manager._instances.clear()
        _singleton_manager._factories.clear()
        _singleton_manager._cleanup_hooks.clear()

    def test_register_singleton(self):
        """Test register_singleton function."""
        register_singleton(name="test", factory=create_mock_client)

        singletons = list_singletons()
        assert "test" in singletons
        assert singletons["test"] == "registered"

    def test_get_singleton_decorator(self):
        """Test get_singleton_client decorator."""

        @get_singleton_client("test-decorator")
        def create_test_client():
            return MockClient("decorator-test")

        ***REMOVED*** Should return dependency function
        dependency_func = create_test_client
        assert callable(dependency_func)

        ***REMOVED*** Should create singleton instance
        instance1 = dependency_func()
        instance2 = dependency_func()

        assert isinstance(instance1, MockClient)
        assert instance1 is instance2  ***REMOVED*** Same instance

    def test_get_singleton_function(self):
        """Test get_singleton function."""
        register_singleton(name="test-func", factory=create_mock_client)

        dependency_func = get_singleton("test-func")
        assert callable(dependency_func)

        instance = dependency_func()
        assert isinstance(instance, MockClient)

    def test_create_singleton_dependency(self):
        """Test create_singleton_dependency convenience function."""
        dependency_func = create_singleton_dependency(
            name="test-convenience",
            factory=create_mock_client,
        )

        assert callable(dependency_func)

        instance1 = dependency_func()
        instance2 = dependency_func()

        assert isinstance(instance1, MockClient)
        assert instance1 is instance2  ***REMOVED*** Same instance

    @pytest.mark.asyncio
    async def test_cleanup_singletons(self):
        """Test cleanup_singletons function."""
        register_singleton(name="test-cleanup", factory=create_mock_client)

        dependency_func = get_singleton("test-cleanup")
        instance = dependency_func()

        await cleanup_singletons()

        assert instance.closed

    @pytest.mark.asyncio
    async def test_cleanup_specific_singleton(self):
        """Test cleaning up specific singleton."""
        register_singleton(name="test1", factory=create_mock_client)
        register_singleton(name="test2", factory=create_mock_client)

        dep1 = get_singleton("test1")
        dep2 = get_singleton("test2")

        instance1 = dep1()
        instance2 = dep2()

        await cleanup_singletons("test1")

        assert instance1.closed
        assert not instance2.closed

    def test_list_singletons_function(self):
        """Test list_singletons function."""
        register_singleton(name="test-list", factory=create_mock_client)

        singletons = list_singletons()

        assert "test-list" in singletons
        assert singletons["test-list"] == "registered"


class TestSingletonIntegration:
    """Integration tests for singleton system."""

    def setup_method(self):
        """Set up test fixtures."""
        ***REMOVED*** Clear global singleton manager
        from fast_core.dependencies.singleton import _singleton_manager

        _singleton_manager._instances.clear()
        _singleton_manager._factories.clear()
        _singleton_manager._cleanup_hooks.clear()

    def teardown_method(self):
        """Clean up after tests."""
        ***REMOVED*** Clear global singleton manager
        from fast_core.dependencies.singleton import _singleton_manager

        _singleton_manager._instances.clear()
        _singleton_manager._factories.clear()
        _singleton_manager._cleanup_hooks.clear()

    def test_multiple_singletons(self):
        """Test managing multiple singletons."""

        @get_singleton_client("client1")
        def create_client1():
            return MockClient("client-1")

        @get_singleton_client("client2")
        def create_client2():
            return MockClient("client-2")

        instance1a = create_client1()
        instance1b = create_client1()
        instance2a = create_client2()
        instance2b = create_client2()

        ***REMOVED*** Same singleton instances
        assert instance1a is instance1b
        assert instance2a is instance2b

        ***REMOVED*** Different singleton instances
        assert instance1a is not instance2a

    def test_singleton_with_fastapi_depends(self):
        """Test singleton works with FastAPI Depends."""
        from fastapi import Depends

        @get_singleton_client("fastapi-test")
        def create_fastapi_client():
            return MockClient("fastapi-client")

        ***REMOVED*** Simulate FastAPI dependency injection
        def route_handler(client: MockClient = Depends(create_fastapi_client)):
            return {"client_name": client.name}

        ***REMOVED*** Resolve dependency manually (simulating FastAPI)
        client = create_fastapi_client()
        result = route_handler(client)

        assert result["client_name"] == "fastapi-client"

    @pytest.mark.asyncio
    async def test_singleton_lifespan_integration(self):
        """Test singleton lifespan integration."""
        from fast_core.dependencies.singleton import singleton_lifespan
        from unittest.mock import Mock

        @get_singleton_client("lifespan-test")
        def create_lifespan_client():
            return MockClient("lifespan-client")

        ***REMOVED*** Create instance
        instance = create_lifespan_client()
        assert not instance.closed

        ***REMOVED*** Simulate app lifespan
        mock_app = Mock()
        async with singleton_lifespan(mock_app):
            ***REMOVED*** During app lifetime
            assert not instance.closed

        ***REMOVED*** After app shutdown
        assert instance.closed
