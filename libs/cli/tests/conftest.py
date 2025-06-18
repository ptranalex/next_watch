"""Test configuration and utilities for CLI Framework tests.

Simplified version without pytest dependencies to avoid type checking issues.
"""

import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import AsyncMock, Mock

from cli.output.handler import CLIOutput
from cli.services.service_registry import ServiceRegistry, ServiceConfig
from cli.services.client_factory import ServiceClientFactory


def create_test_config() -> Dict[str, Any]:
    """Create test configuration dictionary."""
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


def create_mock_console() -> Mock:
    """Create mock Rich console."""
    console = Mock()
    console.print = Mock()
    console.log = Mock()
    console.status = Mock()
    console.confirm = Mock(return_value=True)
    return console


def create_cli_output() -> CLIOutput:
    """Create CLI output handler for testing."""
    return CLIOutput(command_name="test-command", verbose=False, quiet=False)


def create_verbose_cli_output() -> CLIOutput:
    """Create verbose CLI output handler for testing."""
    return CLIOutput(command_name="test-command", verbose=True, quiet=False)


def create_quiet_cli_output() -> CLIOutput:
    """Create quiet CLI output handler for testing."""
    return CLIOutput(command_name="test-command", verbose=False, quiet=True)


def create_service_registry() -> ServiceRegistry:
    """Create service registry with test services."""
    registry = ServiceRegistry()

    ***REMOVED*** Register test services with correct API
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

    auth_config = ServiceConfig(
        name="auth-api",
        url="http://localhost:8001",
        timeout=15,
        retry_attempts=2,
        retry_backoff="linear",
        health_endpoint="/health/live",
        service_type="http",
    )
    registry.register_service(auth_config)

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


def create_mock_redis_client() -> AsyncMock:
    """Create mock Redis client."""
    mock_redis = AsyncMock()

    ***REMOVED*** Mock common Redis operations
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


def create_mock_httpx_client() -> AsyncMock:
    """Create mock httpx client."""
    mock_client = AsyncMock()

    ***REMOVED*** Create mock response object
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json = Mock(return_value={"status": "healthy", "version": "1.0.0"})
    mock_response.headers = {"content-type": "application/json"}

    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.aclose = AsyncMock()

    return mock_client


def create_mock_health_service() -> Mock:
    """Create mock health service."""
    service = Mock()

    ***REMOVED*** Mock health check results
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


def create_sample_health_results() -> Dict[str, Any]:
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


***REMOVED*** Command testing utilities
class CLITestResult:
    """Helper class for CLI test results."""

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
