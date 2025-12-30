"""Tests for service client factory system."""

from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from fast_core.dependencies.client_factory import (
    BaseServiceClient,
    GenericServiceClient,
    ServiceClientConfig,
    ServiceClientFactory,
    create_service_client,
    get_service_client,
    get_service_factory,
    health_check_all_services,
    list_services,
    register_client_type,
    register_service,
    service_client,
)
from fastapi import Depends, FastAPI


class TestServiceClientConfig:
    """Test ServiceClientConfig class."""

    def test_config_initialization(self):
        """Test config initialization with defaults."""
        config = ServiceClientConfig(name="test-service", base_url="https://api.example.com")

        assert config.name == "test-service"
        assert config.base_url == "https://api.example.com"
        assert config.timeout == 30
        assert config.headers == {}
        assert config.singleton is False
        assert config.client_class == httpx.AsyncClient
        assert config.client_kwargs == {}

    def test_config_initialization_with_options(self):
        """Test config initialization with custom options."""
        headers = {"Authorization": "Bearer token"}
        client_kwargs = {"verify": False}

        config = ServiceClientConfig(
            name="auth-service",
            base_url="https://auth.example.com",
            timeout=60,
            headers=headers,
            singleton=True,
            client_kwargs=client_kwargs,
        )

        assert config.name == "auth-service"
        assert config.base_url == "https://auth.example.com"
        assert config.timeout == 60
        assert config.headers == headers
        assert config.singleton is True
        assert config.client_kwargs == client_kwargs


class MockServiceClient(BaseServiceClient):
    """Mock service client for testing."""

    def __init__(self, config: ServiceClientConfig, **kwargs):
        super().__init__(config)
        self.custom_kwargs = kwargs

    async def health_check(self) -> dict[str, Any]:
        """Mock health check."""
        return {
            "service": self.name,
            "status": "healthy",
            "custom": True,
        }


class TestBaseServiceClient:
    """Test BaseServiceClient class."""

    def test_base_client_initialization(self):
        """Test base client initialization."""
        config = ServiceClientConfig(name="test-service", base_url="https://api.example.com")

        client = MockServiceClient(config)

        assert client.config == config
        assert client.name == "test-service"
        assert client.base_url == "https://api.example.com"
        assert client._client is None

    @pytest.mark.asyncio
    async def test_get_client_creation(self):
        """Test HTTP client creation."""
        config = ServiceClientConfig(
            name="test-service",
            base_url="https://api.example.com",
            timeout=45,
            headers={"User-Agent": "test"},
        )

        client = MockServiceClient(config)
        http_client = await client._get_client()

        assert isinstance(http_client, httpx.AsyncClient)
        assert str(http_client.base_url) == "https://api.example.com"
        assert http_client.timeout.read == 45
        assert "User-Agent" in http_client.headers

    @pytest.mark.asyncio
    async def test_client_close(self):
        """Test client close functionality."""
        config = ServiceClientConfig(name="test-service", base_url="https://api.example.com")

        client = MockServiceClient(config)

        # Create client
        await client._get_client()
        assert client._client is not None

        # Close client
        await client.close()
        assert client._client is None


class TestGenericServiceClient:
    """Test GenericServiceClient class."""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        config = ServiceClientConfig(name="test-service", base_url="https://api.example.com")

        client = GenericServiceClient(config)

        # Mock the HTTP client
        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http_client = AsyncMock()
            mock_http_client.get.return_value = mock_response
            mock_http_client.base_url = "https://api.example.com"
            mock_get_client.return_value = mock_http_client

            result = await client.health_check()

            assert result["service"] == "test-service"
            assert result["status"] == "healthy"
            assert result["status_code"] == 200
            assert result["url"] == "https://api.example.com"

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check failure."""
        config = ServiceClientConfig(name="test-service", base_url="https://api.example.com")

        client = GenericServiceClient(config)

        with patch.object(client, "_get_client") as mock_get_client:
            mock_get_client.side_effect = Exception("Connection failed")

            result = await client.health_check()

            assert result["service"] == "test-service"
            assert result["status"] == "error"
            assert "Connection failed" in result["error"]

    @pytest.mark.asyncio
    async def test_http_methods(self):
        """Test HTTP method wrappers."""
        config = ServiceClientConfig(name="test-service", base_url="https://api.example.com")

        client = GenericServiceClient(config)

        # Mock the HTTP client
        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http_client = AsyncMock()
            mock_http_client.get.return_value = mock_response
            mock_http_client.post.return_value = mock_response
            mock_http_client.put.return_value = mock_response
            mock_http_client.delete.return_value = mock_response
            mock_get_client.return_value = mock_http_client

            # Test GET
            response = await client.get("/test")
            assert response.status_code == 200
            mock_http_client.get.assert_called_with("/test")

            # Test POST
            response = await client.post("/test", json={"data": "test"})
            assert response.status_code == 200
            mock_http_client.post.assert_called_with("/test", json={"data": "test"})

            # Test PUT
            response = await client.put("/test", json={"data": "test"})
            assert response.status_code == 200
            mock_http_client.put.assert_called_with("/test", json={"data": "test"})

            # Test DELETE
            response = await client.delete("/test")
            assert response.status_code == 200
            mock_http_client.delete.assert_called_with("/test")


class TestServiceClientFactory:
    """Test ServiceClientFactory class."""

    def test_factory_initialization(self):
        """Test factory initialization."""
        factory = ServiceClientFactory()

        assert factory._configs == {}
        assert factory._client_types == {}
        assert factory._instances == {}

    def test_register_service(self):
        """Test service registration."""
        factory = ServiceClientFactory()

        factory.register_service(
            name="test-service",
            base_url="https://api.example.com",
            timeout=45,
            singleton=True,
        )

        assert "test-service" in factory._configs
        config = factory._configs["test-service"]
        assert config.name == "test-service"
        assert config.base_url == "https://api.example.com"
        assert config.timeout == 45
        assert config.singleton is True

    def test_register_client_type(self):
        """Test custom client type registration."""
        factory = ServiceClientFactory()

        # First register service
        factory.register_service(name="test-service", base_url="https://api.example.com")

        # Then register custom client type
        factory.register_client_type(
            service_name="test-service",
            client_class=MockServiceClient,
            singleton=True,
        )

        assert "test-service" in factory._client_types
        assert factory._client_types["test-service"] == MockServiceClient
        assert factory._configs["test-service"].singleton is True

    def test_create_client_generic(self):
        """Test creating generic client."""
        factory = ServiceClientFactory()

        factory.register_service(name="test-service", base_url="https://api.example.com")

        client = factory.create_client("test-service")

        assert isinstance(client, httpx.AsyncClient)
        assert str(client.base_url) == "https://api.example.com"

    def test_create_client_custom(self):
        """Test creating custom client."""
        factory = ServiceClientFactory()

        factory.register_service(name="test-service", base_url="https://api.example.com")

        factory.register_client_type(
            service_name="test-service",
            client_class=MockServiceClient,
        )

        client = factory.create_client("test-service", custom_param="test")

        assert isinstance(client, MockServiceClient)
        assert client.name == "test-service"
        assert client.custom_kwargs == {"custom_param": "test"}

    def test_create_client_not_registered(self):
        """Test creating client for unregistered service."""
        factory = ServiceClientFactory()

        with pytest.raises(ValueError, match="Service 'unknown' not registered"):
            factory.create_client("unknown")

    def test_get_dependency_singleton(self):
        """Test getting singleton dependency."""
        factory = ServiceClientFactory()

        factory.register_service(
            name="test-service",
            base_url="https://api.example.com",
            singleton=True,
        )

        dependency = factory.get_dependency("test-service")

        # Should be a function for FastAPI Depends
        assert callable(dependency)

    def test_get_dependency_per_request(self):
        """Test getting per-request dependency."""
        factory = ServiceClientFactory()

        factory.register_service(
            name="test-service",
            base_url="https://api.example.com",
            singleton=False,
        )

        dependency = factory.get_dependency("test-service")

        # Should be a function for FastAPI Depends
        assert callable(dependency)
        assert dependency.__name__ == "get_test-service_client"

    def test_list_services(self):
        """Test listing services."""
        factory = ServiceClientFactory()

        factory.register_service(
            name="service1",
            base_url="https://api1.example.com",
            singleton=True,
        )

        factory.register_service(
            name="service2",
            base_url="https://api2.example.com",
            timeout=60,
        )

        services = factory.list_services()

        assert len(services) == 2
        assert "service1" in services
        assert "service2" in services

        assert services["service1"]["base_url"] == "https://api1.example.com"
        assert services["service1"]["singleton"] is True
        assert services["service2"]["timeout"] == 60

    @pytest.mark.asyncio
    async def test_health_check_all(self):
        """Test health check for all services."""
        factory = ServiceClientFactory()

        factory.register_service(name="test-service", base_url="https://api.example.com")

        factory.register_client_type(
            service_name="test-service",
            client_class=MockServiceClient,
        )

        results = await factory.health_check_all()

        assert len(results) == 1
        assert "test-service" in results
        assert results["test-service"]["service"] == "test-service"
        assert results["test-service"]["status"] == "healthy"
        assert results["test-service"]["custom"] is True


class TestGlobalFunctions:
    """Test global convenience functions."""

    def test_register_service_global(self):
        """Test global service registration."""
        # Clear any existing registrations
        factory = get_service_factory()
        factory._configs.clear()
        factory._client_types.clear()

        register_service(
            name="global-service",
            base_url="https://global.example.com",
            singleton=True,
        )

        services = list_services()
        assert "global-service" in services
        assert services["global-service"]["singleton"] is True

    def test_register_client_type_global(self):
        """Test global client type registration."""
        # Ensure service is registered first
        register_service(name="custom-service", base_url="https://custom.example.com")

        register_client_type(
            service_name="custom-service",
            client_class=MockServiceClient,
        )

        client = create_service_client("custom-service")
        assert isinstance(client, MockServiceClient)

    def test_get_service_client_dependency(self):
        """Test getting service client dependency."""
        register_service(name="dep-service", base_url="https://dep.example.com")

        dependency = get_service_client("dep-service")
        assert callable(dependency)

    def test_service_client_decorator(self):
        """Test service client decorator."""
        # Register service first
        register_service(name="decorated-service", base_url="https://decorated.example.com")

        @service_client("decorated-service", singleton=True)
        class DecoratedClient(BaseServiceClient):
            async def health_check(self) -> dict[str, Any]:
                return {"service": self.name, "status": "decorated"}

        client = create_service_client("decorated-service")
        assert isinstance(client, DecoratedClient)

    @pytest.mark.asyncio
    async def test_health_check_all_services_global(self):
        """Test global health check function."""
        # Ensure we have at least one service registered
        register_service(name="health-service", base_url="https://health.example.com")

        register_client_type(
            service_name="health-service",
            client_class=MockServiceClient,
        )

        results = await health_check_all_services()

        assert isinstance(results, dict)
        assert "health-service" in results


class TestIntegrationWithFastAPI:
    """Test integration with FastAPI."""

    def test_fastapi_dependency_injection(self):
        """Test using service client as FastAPI dependency."""
        app = FastAPI()

        # Register service
        register_service(name="api-service", base_url="https://api.example.com")

        # Create dependency
        get_api_client = get_service_client("api-service")

        @app.get("/test")
        async def test_endpoint(client=Depends(get_api_client)):
            return {"client_type": type(client).__name__}

        # Verify the dependency is properly configured
        assert callable(get_api_client)

    def test_custom_client_with_fastapi(self):
        """Test custom client with FastAPI dependency injection."""
        app = FastAPI()

        # Register service with custom client
        register_service(name="custom-api", base_url="https://custom-api.example.com")

        register_client_type(
            service_name="custom-api",
            client_class=MockServiceClient,
        )

        # Create dependency
        get_custom_client = get_service_client("custom-api")

        @app.get("/custom")
        async def custom_endpoint(client=Depends(get_custom_client)):
            return {"client_name": client.name}

        # Verify the dependency works
        assert callable(get_custom_client)


if __name__ == "__main__":
    pytest.main([__file__])
