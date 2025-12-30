"""Base test classes and utilities for CLI Framework tests."""

import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, Mock

if TYPE_CHECKING:
    from cli.services.service_registry import ServiceRegistry

from cli.output.handler import CLIOutput
from cli.services.service_registry import ServiceConfig, ServiceRegistry


class CLITestCase:
    """Base test case class for CLI Framework tests."""

    def setup_method(self) -> None:
        """Set up test method with temporary directory and mock console."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.mock_console = Mock()
        self.mock_console.print = Mock()
        self.mock_console.log = Mock()
        self.mock_console.status = Mock()
        self.mock_console.confirm = Mock(return_value=True)

    def teardown_method(self) -> None:
        """Clean up test method."""
        if hasattr(self, "temp_dir") and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_test_file(self, filename: str, content: str = "") -> Path:
        """Create a test file in the temporary directory.

        Args:
            filename: Name of the file to create
            content: Content to write to the file

        Returns:
            Path to the created file
        """
        file_path = self.temp_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path

    def create_cli_output(self, verbose: bool = False, quiet: bool = False) -> CLIOutput:
        """Create a CLI output handler for testing.

        Args:
            verbose: Enable verbose mode
            quiet: Enable quiet mode

        Returns:
            Configured CLIOutput instance
        """
        return CLIOutput(command_name="test-command", verbose=verbose, quiet=quiet)

    def create_test_config(self) -> dict[str, Any]:
        """Create a test configuration dictionary."""
        return {
            "host": "localhost",
            "port": 8000,
            "database_url": "postgresql://user:secret@localhost:5432/test_db",
            "redis_url": "redis://localhost:6379/0",
            "jwt_secret": "test-jwt-secret-key",
            "api_key": "test-api-key-12345",
            "debug": True,
            "log_level": "INFO",
            "timeout": 30.0,
            "retries": 3,
        }

    def create_mock_redis_client(self) -> AsyncMock:
        """Create a mock Redis client."""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.info = AsyncMock(
            return_value={
                "redis_version": "7.0.0",
                "connected_clients": "1",
                "used_memory_human": "1.2M",
            }
        )
        mock_redis.keys = AsyncMock(return_value=[b"test:key1", b"test:key2"])
        mock_redis.get = AsyncMock(return_value=b"test_value")
        mock_redis.set = AsyncMock(return_value=True)
        mock_redis.delete = AsyncMock(return_value=1)
        mock_redis.flushdb = AsyncMock(return_value=True)
        mock_redis.type = AsyncMock(return_value=b"string")
        mock_redis.ttl = AsyncMock(return_value=3600)
        mock_redis.close = AsyncMock()
        return mock_redis

    def create_mock_http_client(self) -> AsyncMock:
        """Create a mock HTTP client."""
        mock_client = AsyncMock()

        # Create a mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"status": "healthy", "version": "1.0.0"})
        mock_response.headers = {"content-type": "application/json"}

        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()

        return mock_client

    def create_mock_health_service(self) -> Mock:
        """Create a mock health service."""
        service = Mock()

        # Mock health check results
        healthy_result = Mock(is_healthy=True, response_time=0.1, status="healthy")
        unhealthy_result = Mock(
            is_healthy=False,
            response_time=None,
            status="unhealthy",
            error="Connection timeout",
        )

        service.check_all = AsyncMock(
            return_value={
                "backend-api": healthy_result,
                "auth-api": healthy_result,
                "redis": unhealthy_result,
            }
        )

        service.check_backend_api = AsyncMock(return_value=healthy_result)
        service.check_auth_api = AsyncMock(return_value=healthy_result)
        service.check_redis = AsyncMock(return_value=unhealthy_result)
        service.close = AsyncMock()

        return service


class AsyncTestCase(CLITestCase):
    """Base async test case for CLI Framework tests."""

    async def async_setup_method(self) -> None:
        """Async setup for test methods."""
        self.setup_method()
        self.async_resources: list[Any] = []

    async def async_teardown_method(self) -> None:
        """Async cleanup for test methods."""
        # Clean up async resources in reverse order
        for resource in reversed(self.async_resources):
            if hasattr(resource, "aclose"):
                await resource.aclose()
            elif hasattr(resource, "close"):
                if hasattr(resource.close, "__call__"):
                    resource.close()

        self.teardown_method()

    def add_async_resource(self, resource: Any) -> None:
        """Add an async resource to be cleaned up."""
        if hasattr(self, "async_resources"):
            self.async_resources.append(resource)


class CLITestResult:
    """Helper class for CLI test results validation."""

    def __init__(self, exit_code: int, stdout: str, stderr: str = ""):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

    def assert_success(self) -> None:
        """Assert that the command was successful."""
        assert (
            self.exit_code == 0
        ), f"Command failed with exit code {self.exit_code}. Output: {self.stdout}"

    def assert_failure(self, expected_code: int = 1) -> None:
        """Assert that the command failed with expected code."""
        assert (
            self.exit_code == expected_code
        ), f"Expected exit code {expected_code}, got {self.exit_code}"

    def assert_contains(self, text: str, in_stdout: bool = True) -> None:
        """Assert that output contains specific text."""
        target = self.stdout if in_stdout else self.stderr
        assert (
            text in target
        ), f"'{text}' not found in {'stdout' if in_stdout else 'stderr'}: {target}"

    def assert_not_contains(self, text: str, in_stdout: bool = True) -> None:
        """Assert that output does not contain specific text."""
        target = self.stdout if in_stdout else self.stderr
        assert (
            text not in target
        ), f"'{text}' unexpectedly found in {'stdout' if in_stdout else 'stderr'}: {target}"


# Test data factory functions
def create_sample_health_results() -> dict[str, Any]:
    """Create sample health check results for testing."""
    return {
        "backend-api": Mock(
            is_healthy=True,
            response_time=0.123,
            status="healthy",
            version="1.0.0",
            details={"database": "connected", "cache": "active"},
        ),
        "auth-api": Mock(
            is_healthy=True,
            response_time=0.045,
            status="healthy",
            version="0.8.2",
            details={"jwt_validation": "ok", "user_store": "connected"},
        ),
        "redis": Mock(
            is_healthy=False,
            response_time=None,
            status="unhealthy",
            error="Connection timeout",
            details={},
        ),
    }


def create_test_service_registry() -> ServiceRegistry:
    """Create a service registry with test services."""
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
        headers={"Authorization": "Bearer test-token"},
    )
    registry.register_service(backend_config)

    # Redis service
    redis_config = ServiceConfig(
        name="redis",
        url="redis://localhost:6379/0",
        timeout=5,
        retry_attempts=3,
        retry_backoff="exponential",
        service_type="redis",
    )
    registry.register_service(redis_config)

    return registry


def create_mock_health_service() -> Mock:
    """Create a mock health service for testing."""
    service = Mock()

    # Mock health check results
    healthy_result = Mock(is_healthy=True, response_time=0.1, status="healthy")
    unhealthy_result = Mock(
        is_healthy=False,
        response_time=None,
        status="unhealthy",
        error="Connection timeout",
    )

    service.check_all = Mock(
        return_value={
            "backend-api": healthy_result,
            "auth-api": healthy_result,
            "redis": unhealthy_result,
        }
    )

    service.check_backend_api = Mock(return_value=healthy_result)
    service.check_auth_api = Mock(return_value=healthy_result)
    service.check_redis = Mock(return_value=unhealthy_result)

    return service


# Mock client factories
def create_mock_redis_client() -> Mock:
    """Create a mock Redis client for testing."""
    mock_redis = Mock()

    # Mock common Redis operations
    mock_redis.ping.return_value = True
    mock_redis.info.return_value = {
        "redis_version": "7.0.0",
        "connected_clients": "1",
        "used_memory_human": "1.2M",
    }
    mock_redis.keys.return_value = [b"test:key1", b"test:key2"]
    mock_redis.get.return_value = b"test_value"
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.flushdb.return_value = True
    mock_redis.type.return_value = b"string"
    mock_redis.ttl.return_value = 3600

    return mock_redis


def create_mock_httpx_client() -> Mock:
    """Create a mock httpx client for testing."""
    mock_client = Mock()

    # Create mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "healthy", "version": "1.0.0"}
    mock_response.headers = {"content-type": "application/json"}

    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response

    return mock_client
