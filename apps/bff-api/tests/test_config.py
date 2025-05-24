"""Tests for BFF configuration."""

import os
import pytest
from unittest.mock import patch

from bff_api.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_config_defaults(self):
        """Test that configuration uses proper defaults."""
        config = Config()

        assert config.host == "0.0.0.0"
        assert config.port == 8001
        assert config.log_level == "INFO"
        assert config.backend_api_url == "http://localhost:8000"
        assert config.environment == "development"
        assert config.debug is False
        assert config.is_development is True
        assert config.is_production is False

    def test_config_from_env_vars(self):
        """Test configuration loading from environment variables."""
        env_vars = {
            "HOST": "127.0.0.1",
            "PORT": "9000",
            "LOG_LEVEL": "DEBUG",
            "BACKEND_API_URL": "http://test-backend:8080",
            "ENVIRONMENT": "production",
            "DEBUG": "true",
            "JWT_SECRET": "test-secret",
        }

        with patch.dict(os.environ, env_vars):
            config = Config()

            assert config.host == "127.0.0.1"
            assert config.port == 9000
            assert config.log_level == "DEBUG"
            assert config.backend_api_url == "http://test-backend:8080"
            assert config.environment == "production"
            assert config.debug is True
            assert config.jwt_secret == "test-secret"
            assert config.is_production is True
            assert config.is_development is False

    def test_config_singleton(self):
        """Test that Config.get_instance() returns singleton."""
        config1 = Config.get_instance()
        config2 = Config.get_instance()

        assert config1 is config2

    def test_config_repr_masks_secrets(self):
        """Test that __repr__ masks sensitive information."""
        config = Config(jwt_secret="super-secret")
        repr_str = repr(config)

        assert "super-secret" not in repr_str
        assert "***" in repr_str

    def test_config_repr_no_secret(self):
        """Test __repr__ when no secret is set."""
        config = Config(jwt_secret=None)
        repr_str = repr(config)

        assert "jwt_secret=None" in repr_str

    def test_backend_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from backend URL."""
        config = Config(backend_api_url="http://localhost:8000/")

        assert config.backend_api_url == "http://localhost:8000"
