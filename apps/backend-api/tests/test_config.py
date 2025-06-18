***REMOVED*** type: ignore

"""Tests for Backend API configuration."""

import os
import tempfile
from typing import Any
from unittest.mock import patch

import pytest


class TestConfig:
    """Test cases for Config class."""

    def test_config_defaults(self) -> None:
        """Test that configuration uses proper defaults."""
        ***REMOVED*** Import here to avoid module path issues
        from backend_api.config.app import Config

        config = Config()

        ***REMOVED*** Check that basic defaults are set
        assert config.log_level == "INFO"
        assert config.api_port == 8001
        assert config.debug is False
        assert isinstance(config.cors_origins, list)

    def test_logs_dir_empty_string_becomes_none(self) -> None:
        """Test that empty LOGS_DIR environment variable becomes None."""
        from backend_api.config.app import Config

        with patch.dict(os.environ, {"LOGS_DIR": ""}):
            ***REMOVED*** Clear the singleton to force re-initialization
            Config._instance = None
            config = Config.get_instance()

            ***REMOVED*** Empty string should become None to disable file logging
            assert config.logs_dir is None

    def test_logs_dir_valid_path_preserved(self) -> None:
        """Test that valid LOGS_DIR is preserved."""
        from backend_api.config.app import Config

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"LOGS_DIR": temp_dir}):
                ***REMOVED*** Clear the singleton to force re-initialization
                Config._instance = None
                config = Config.get_instance()

                ***REMOVED*** Valid path should be preserved
                assert config.logs_dir == temp_dir

    def test_logs_dir_none_from_env_vars(self) -> None:
        """Test that missing LOGS_DIR defaults to logs directory."""
        from backend_api.config.app import Config

        ***REMOVED*** Remove LOGS_DIR from environment if it exists
        env_without_logs_dir = {k: v for k, v in os.environ.items() if k != "LOGS_DIR"}

        with patch.dict(os.environ, env_without_logs_dir, clear=True):
            ***REMOVED*** Clear the singleton to force re-initialization
            Config._instance = None
            config = Config.get_instance()

            ***REMOVED*** Should default to "logs" directory
            assert config.logs_dir == "logs"

    def test_config_singleton(self) -> None:
        """Test that Config.get_instance() returns singleton."""
        from backend_api.config.app import Config

        config1 = Config.get_instance()
        config2 = Config.get_instance()

        assert config1 is config2

    def test_config_production_forces_debug_false(self) -> None:
        """Test that production environment forces debug to False."""
        from backend_api.config.app import Config

        with patch.dict(os.environ, {"ENVIRONMENT": "production", "DEBUG": "true"}):
            ***REMOVED*** Clear the singleton to force re-initialization
            Config._instance = None
            config = Config.get_instance()

            ***REMOVED*** Even if DEBUG=true, production should force it to False
            assert config.debug is False

    def test_config_repr_masks_secrets(self) -> None:
        """Test that string representation masks sensitive information."""
        from backend_api.config.app import Config

        config = Config()
        config_str = str(config)

        ***REMOVED*** JWT secret should be masked
        assert "***" in config_str
        assert config.jwt_secret not in config_str

    def teardown_method(self) -> None:
        """Clean up after each test."""
        ***REMOVED*** Reset singleton instance for any Config class that was imported
        try:
            from backend_api.config.app import Config

            Config._instance = None
        except ImportError:
            pass
