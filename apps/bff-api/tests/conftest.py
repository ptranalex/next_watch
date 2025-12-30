"""Pytest configuration and fixtures for BFF tests."""

import os

os.environ.setdefault("OTEL_SDK_DISABLED", "true")
os.environ.setdefault("OTEL_TRACES_EXPORTER", "none")
os.environ.setdefault("OTEL_METRICS_EXPORTER", "none")
os.environ.setdefault("OTEL_LOGS_EXPORTER", "none")
os.environ.setdefault("ENABLE_TRACING", "false")
os.environ.setdefault("TRACING_ENDPOINT", "")


from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from fastapi.testclient import TestClient

from bff_api.config import Config
from bff_api.dependencies import get_backend_client
from bff_api.main import get_app
from bff_api.services.backend_client import BackendClient


@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return Config(
        backend_api_url="http://test-backend",
        backend_api_timeout=5,
        redis_url="redis://test-redis:6379",
        cache_ttl=60,
        jwt_secret="test-secret-which-is-long",
        debug=True,
    )


@pytest.fixture
def mock_backend_client():
    """Mock backend client fixture."""
    client = Mock(spec=BackendClient)
    client.get_movie = AsyncMock()
    client.get_movies = AsyncMock()
    client.get_genres = AsyncMock()
    client.get_actor = AsyncMock()
    client.search_movies = AsyncMock()
    return client


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client fixture."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def app(test_config, mock_backend_client):
    """FastAPI test application fixture."""
    app = get_app()

    # Override dependencies
    app.dependency_overrides = {
        get_backend_client: lambda: mock_backend_client,
    }

    return app


@pytest.fixture
def client(app):
    """Test client fixture."""
    return TestClient(app)
