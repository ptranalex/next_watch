"""Pytest configuration and fixtures for BFF tests."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock
import httpx

from bff_api.main import create_app
from bff_api.config import Config
from bff_api.services.backend_client import BackendClient


@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return Config(
        backend_api_url="http://test-backend",
        backend_api_timeout=5,
        redis_url="redis://test-redis:6379",
        cache_ttl=60,
        jwt_secret="test-secret",
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
    app = create_app()

    ***REMOVED*** Override dependencies
    app.dependency_overrides = {
        BackendClient: lambda: mock_backend_client,
    }

    return app


@pytest.fixture
def client(app):
    """Test client fixture."""
    return TestClient(app)
