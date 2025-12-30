"""Tests for ServiceRegistry functionality."""

from cli.services.service_registry import ServiceConfig, ServiceRegistry

from tests.test_base import CLITestCase


class TestServiceConfig(CLITestCase):
    """Test cases for ServiceConfig class."""

    def test_service_config_creation(self) -> None:
        """Test creating a valid service config."""
        config = ServiceConfig(
            name="test-service",
            url="http://localhost:8000",
            timeout=30,
            retry_attempts=3,
            retry_backoff="exponential",
            health_endpoint="/health",
            service_type="http",
        )

        assert config.name == "test-service"
        assert config.url == "http://localhost:8000"
        assert config.timeout == 30
        assert config.retry_attempts == 3
        assert config.retry_backoff == "exponential"
        assert config.health_endpoint == "/health"
        assert config.service_type == "http"

    def test_service_config_base_url(self) -> None:
        """Test base URL property removes trailing slashes."""
        config = ServiceConfig(name="test-service", url="http://localhost:8000/", timeout=10)

        assert config.base_url == "http://localhost:8000"

    def test_service_config_health_url(self) -> None:
        """Test health URL property combines base URL and endpoint."""
        config = ServiceConfig(
            name="test-service",
            url="http://localhost:8000",
            timeout=10,
            health_endpoint="/health/check",
        )

        assert config.health_url == "http://localhost:8000/health/check"

    def test_service_config_invalid_url(self) -> None:
        """Test that invalid URLs raise ValueError."""
        try:
            ServiceConfig(name="test-service", url="invalid-url", timeout=10)
            assert False, "Expected ValueError for invalid URL"
        except ValueError as e:
            assert "Invalid service URL" in str(e)

    def test_service_config_invalid_timeout(self) -> None:
        """Test that invalid timeout raises ValueError."""
        try:
            ServiceConfig(name="test-service", url="http://localhost:8000", timeout=0)
            assert False, "Expected ValueError for invalid timeout"
        except ValueError as e:
            assert "Service timeout must be positive" in str(e)

    def test_service_config_invalid_retry_attempts(self) -> None:
        """Test that negative retry attempts raise ValueError."""
        try:
            ServiceConfig(
                name="test-service",
                url="http://localhost:8000",
                timeout=10,
                retry_attempts=-1,
            )
            assert False, "Expected ValueError for negative retry attempts"
        except ValueError as e:
            assert "Retry attempts cannot be negative" in str(e)

    def test_service_config_invalid_backoff(self) -> None:
        """Test that invalid backoff strategy raises ValueError."""
        try:
            ServiceConfig(
                name="test-service",
                url="http://localhost:8000",
                timeout=10,
                retry_backoff="invalid",
            )
            assert False, "Expected ValueError for invalid backoff"
        except ValueError as e:
            assert "Invalid retry backoff" in str(e)


class TestServiceRegistry(CLITestCase):
    """Test cases for ServiceRegistry class."""

    def setup_method(self) -> None:
        """Set up test method with a fresh registry."""
        super().setup_method()
        self.registry = ServiceRegistry()

    def test_registry_initialization(self) -> None:
        """Test registry starts empty."""
        assert len(self.registry) == 0
        assert list(self.registry.list_services()) == []

    def test_register_service(self) -> None:
        """Test registering a single service."""
        config = ServiceConfig(name="test-service", url="http://localhost:8000", timeout=10)

        self.registry.register_service(config)

        assert len(self.registry) == 1
        assert "test-service" in self.registry
        assert self.registry.is_registered("test-service")

    def test_register_duplicate_service(self) -> None:
        """Test that registering duplicate service raises ValueError."""
        config = ServiceConfig(name="test-service", url="http://localhost:8000", timeout=10)

        self.registry.register_service(config)

        try:
            self.registry.register_service(config)
            assert False, "Expected ValueError for duplicate service"
        except ValueError as e:
            assert "Service 'test-service' is already registered" in str(e)

    def test_get_service(self) -> None:
        """Test retrieving a registered service."""
        config = ServiceConfig(name="test-service", url="http://localhost:8000", timeout=10)

        self.registry.register_service(config)
        retrieved = self.registry.get_service("test-service")

        assert retrieved == config
        assert retrieved.name == "test-service"
        assert retrieved.url == "http://localhost:8000"

    def test_get_nonexistent_service(self) -> None:
        """Test that getting nonexistent service raises KeyError."""
        try:
            self.registry.get_service("nonexistent")
            assert False, "Expected KeyError for nonexistent service"
        except KeyError as e:
            assert "Service 'nonexistent' not found" in str(e)

    def test_list_services(self) -> None:
        """Test listing all service names."""
        configs = [
            ServiceConfig(name="service-1", url="http://localhost:8001", timeout=10),
            ServiceConfig(name="service-2", url="http://localhost:8002", timeout=10),
            ServiceConfig(name="service-3", url="http://localhost:8003", timeout=10),
        ]

        for config in configs:
            self.registry.register_service(config)

        service_names = self.registry.list_services()
        assert len(service_names) == 3
        assert "service-1" in service_names
        assert "service-2" in service_names
        assert "service-3" in service_names

    def test_get_services_by_type(self) -> None:
        """Test filtering services by type."""
        http_config = ServiceConfig(
            name="http-service",
            url="http://localhost:8000",
            timeout=10,
            service_type="http",
        )
        redis_config = ServiceConfig(
            name="redis-service",
            url="redis://localhost:6379",
            timeout=10,
            service_type="redis",
        )

        self.registry.register_service(http_config)
        self.registry.register_service(redis_config)

        http_services = self.registry.get_services_by_type("http")
        redis_services = self.registry.get_services_by_type("redis")

        assert len(http_services) == 1
        assert len(redis_services) == 1
        assert http_services[0].name == "http-service"
        assert redis_services[0].name == "redis-service"

    def test_unregister_service(self) -> None:
        """Test unregistering a service."""
        config = ServiceConfig(name="test-service", url="http://localhost:8000", timeout=10)

        self.registry.register_service(config)
        assert len(self.registry) == 1

        self.registry.unregister_service("test-service")
        assert len(self.registry) == 0
        assert not self.registry.is_registered("test-service")

    def test_unregister_nonexistent_service(self) -> None:
        """Test that unregistering nonexistent service raises KeyError."""
        try:
            self.registry.unregister_service("nonexistent")
            assert False, "Expected KeyError for nonexistent service"
        except KeyError as e:
            assert "Service 'nonexistent' not found" in str(e)

    def test_clear_registry(self) -> None:
        """Test clearing all services from registry."""
        configs = [
            ServiceConfig(name="service-1", url="http://localhost:8001", timeout=10),
            ServiceConfig(name="service-2", url="http://localhost:8002", timeout=10),
        ]

        for config in configs:
            self.registry.register_service(config)

        assert len(self.registry) == 2

        self.registry.clear()
        assert len(self.registry) == 0
        assert list(self.registry.list_services()) == []

    def test_registry_contains(self) -> None:
        """Test registry __contains__ method."""
        config = ServiceConfig(name="test-service", url="http://localhost:8000", timeout=10)

        assert "test-service" not in self.registry

        self.registry.register_service(config)
        assert "test-service" in self.registry

    def test_registry_iteration(self) -> None:
        """Test iterating over registry service names."""
        configs = [
            ServiceConfig(name="service-a", url="http://localhost:8001", timeout=10),
            ServiceConfig(name="service-b", url="http://localhost:8002", timeout=10),
        ]

        for config in configs:
            self.registry.register_service(config)

        service_names = list(self.registry)
        assert len(service_names) == 2
        assert "service-a" in service_names
        assert "service-b" in service_names

    def test_register_multiple_services(self) -> None:
        """Test registering multiple services at once."""
        configs = [
            ServiceConfig(name="service-1", url="http://localhost:8001", timeout=10),
            ServiceConfig(name="service-2", url="http://localhost:8002", timeout=10),
            ServiceConfig(name="service-3", url="http://localhost:8003", timeout=10),
        ]

        self.registry.register_services(configs)

        assert len(self.registry) == 3
        for config in configs:
            assert self.registry.is_registered(config.name)
            retrieved = self.registry.get_service(config.name)
            assert retrieved == config


class TestServiceRegistryIntegration(CLITestCase):
    """Integration tests for ServiceRegistry with realistic configurations."""

    def test_nextwatch_service_registry(self) -> None:
        """Test registry with NextWatch-like service configurations."""
        registry = ServiceRegistry()

        # Backend API service
        backend_config = ServiceConfig(
            name="backend-api",
            url="http://localhost:8000",
            timeout=30,
            retry_attempts=3,
            retry_backoff="exponential",
            health_endpoint="/health",
            service_type="http",
            headers={"Authorization": "Bearer token"},
        )

        # Auth API service
        auth_config = ServiceConfig(
            name="auth-api",
            url="http://localhost:8001",
            timeout=15,
            retry_attempts=2,
            retry_backoff="linear",
            health_endpoint="/health/live",
            service_type="http",
        )

        # Redis cache service
        redis_config = ServiceConfig(
            name="redis",
            url="redis://localhost:6379/0",
            timeout=5,
            retry_attempts=3,
            retry_backoff="exponential",
            service_type="redis",
        )

        # Register all services
        for config in [backend_config, auth_config, redis_config]:
            registry.register_service(config)

        # Verify all services are registered correctly
        assert len(registry) == 3

        # Test retrieving specific services
        backend = registry.get_service("backend-api")
        assert backend.timeout == 30
        assert backend.headers["Authorization"] == "Bearer token"

        auth = registry.get_service("auth-api")
        assert auth.health_endpoint == "/health/live"
        assert auth.retry_backoff == "linear"

        redis = registry.get_service("redis")
        assert redis.service_type == "redis"
        assert redis.timeout == 5

        # Test filtering by service type
        http_services = registry.get_services_by_type("http")
        redis_services = registry.get_services_by_type("redis")

        assert len(http_services) == 2
        assert len(redis_services) == 1

        http_names = [svc.name for svc in http_services]
        assert "backend-api" in http_names
        assert "auth-api" in http_names
