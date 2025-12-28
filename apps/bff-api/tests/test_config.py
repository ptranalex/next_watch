"""Tests for BFF configuration."""

import os
from unittest.mock import patch

from bff_api.config import BFFAPIConfig


class TestConfig:
    """Test cases for BFFAPIConfig."""

    def test_config_defaults(self) -> None:
        config = BFFAPIConfig()

        assert config.host == "0.0.0.0"
        assert config.port == 8001
        assert config.backend_api_url == "http://localhost:8000"
        assert config.environment == "development"

    def test_config_from_env_vars(self) -> None:
        env_vars = {
            "HOST": "127.0.0.1",
            "PORT": "9000",
            "LOG_LEVEL": "DEBUG",
            "BACKEND_API_URL": "http://test-backend:8080/",
            "ENVIRONMENT": "production",
            "DEBUG": "true",
            "JWT_SECRET": "test-secret-which-is-long",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = BFFAPIConfig()

        assert config.host == "127.0.0.1"
        assert config.port == 9000
        assert config.log_level == "DEBUG"
        assert (
            config.backend_api_url == "http://test-backend:8080"
        )  ***REMOVED*** trailing slash removed
        assert config.environment == "production"
        ***REMOVED*** production overrides should force debug off
        assert config.debug is False

    def test_backend_url_trailing_slash_removed(self) -> None:
        config = BFFAPIConfig(backend_api_url="http://localhost:8000/")
        assert config.backend_api_url == "http://localhost:8000"
