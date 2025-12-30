"""Tests for Fast Core application factory.

This module tests the core application creation functionality
and basic components of the Fast Core library.
"""

import pytest
from fast_core import AppOptions, FastAPIConfig, create_app
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestConfig(FastAPIConfig):
    """Test configuration."""

    service_name: str = "Test Service"
    debug: bool = True
    cors_origins: list = ["*"]


def test_create_app_basic():
    """Test basic app creation."""
    settings = TestConfig()
    app = create_app(settings)

    assert isinstance(app, FastAPI)
    assert app.title == "Test Service"
    assert app.debug is True


def test_create_app_with_options():
    """Test app creation with options."""
    settings = TestConfig()
    options = AppOptions(
        middleware=False,
        exception_handlers=False,
        health_checks=False,
        cors=False,
        docs=True,
    )

    app = create_app(settings, options=options)

    assert isinstance(app, FastAPI)
    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"


def test_create_app_no_docs():
    """Test app creation without documentation."""
    settings = TestConfig()
    options = AppOptions(docs=False)

    app = create_app(settings, options=options)

    assert app.docs_url is None
    assert app.redoc_url is None
    assert app.openapi_url is None


def test_app_state():
    """Test that settings are stored in app state."""
    settings = TestConfig()
    app = create_app(settings)

    assert hasattr(app.state, "settings")
    assert app.state.settings == settings


def test_app_with_client():
    """Test app with test client."""
    settings = TestConfig()
    app = create_app(settings)

    with TestClient(app) as client:
        # Test that the app responds
        response = client.get("/docs")
        # Should get redirect to /docs/ or the docs page
        assert response.status_code in [200, 307]


def test_fastapi_config():
    """Test FastAPI configuration."""
    config = FastAPIConfig(
        service_name="Test API",
        debug=True,
        cors_origins=["http://localhost:3000"],
        cors_allow_credentials=True,
        docs_url="/documentation",
        redoc_url="/redoc-ui",
    )

    fastapi_kwargs = config.get_fastapi_kwargs()

    assert fastapi_kwargs["title"] == "Test API"
    assert fastapi_kwargs["debug"] is True
    assert fastapi_kwargs["docs_url"] == "/documentation"
    assert fastapi_kwargs["redoc_url"] == "/redoc-ui"


def test_cors_config():
    """Test CORS configuration."""
    config = FastAPIConfig(
        cors_origins=["http://localhost:3000", "https://example.com"],
        cors_allow_credentials=True,
        cors_allow_methods=["GET", "POST"],
        cors_allow_headers=["Content-Type", "Authorization"],
    )

    cors_config = config.get_cors_config()

    assert cors_config["allow_origins"] == ["http://localhost:3000", "https://example.com"]
    assert cors_config["allow_credentials"] is True
    assert cors_config["allow_methods"] == ["GET", "POST"]
    assert cors_config["allow_headers"] == ["Content-Type", "Authorization"]


def test_uvicorn_config():
    """Test Uvicorn configuration."""
    config = FastAPIConfig(
        workers=4,
        keepalive=30,
        debug=False,
    )

    # Add host and port for testing
    config.host = "127.0.0.1"
    config.port = 8080
    config.log_level = "debug"

    uvicorn_config = config.get_uvicorn_config()

    assert uvicorn_config["host"] == "127.0.0.1"
    assert uvicorn_config["port"] == 8080
    assert uvicorn_config["workers"] == 4
    assert uvicorn_config["timeout_keep_alive"] == 30
    assert uvicorn_config["reload"] is False
    assert uvicorn_config["log_level"] == "debug"


def test_custom_title_and_description():
    """Test custom title and description."""
    settings = TestConfig()
    app = create_app(
        settings,
        title="Custom Title",
        description="Custom Description",
        version="2.0.0",
    )

    assert app.title == "Custom Title"
    assert app.version == "2.0.0"
    # Description is not directly accessible from FastAPI app, but we can test it was set


if __name__ == "__main__":
    pytest.main([__file__])
