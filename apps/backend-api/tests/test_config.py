# type: ignore

"""Tests for Backend API configuration."""

import os
import tempfile
from unittest.mock import patch

from backend_api.config.app import BackendAPIConfig


class TestConfig:
    """Test cases for BackendAPIConfig."""

    def test_config_defaults(self) -> None:
        """Test that configuration uses proper defaults."""
        env_without_logs_dir = {k: v for k, v in os.environ.items() if k != "LOGS_DIR"}

        with patch.dict(os.environ, env_without_logs_dir, clear=True):
            config = BackendAPIConfig()

        assert config.service_name == "backend-api"
        assert config.port == 8000
        assert isinstance(config.cors_origins, list)

    def test_logs_dir_empty_string_becomes_none(self) -> None:
        """Test that empty LOGS_DIR environment variable becomes None."""
        with patch.dict(os.environ, {"LOGS_DIR": ""}):
            config = BackendAPIConfig()
            assert config.logs_dir is None

    def test_logs_dir_valid_path_preserved(self) -> None:
        """Test that valid LOGS_DIR is preserved."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"LOGS_DIR": temp_dir}):
                config = BackendAPIConfig()
                assert config.logs_dir == temp_dir

    def test_logs_dir_none_from_env_vars(self) -> None:
        """Test that missing LOGS_DIR defaults to None."""
        env_without_logs_dir = {k: v for k, v in os.environ.items() if k != "LOGS_DIR"}

        with patch.dict(os.environ, env_without_logs_dir, clear=True):
            config = BackendAPIConfig()
            assert config.logs_dir is None

    def test_config_production_forces_debug_false(self) -> None:
        """Test that production environment forces debug to False."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "DEBUG": "true"}):
            config = BackendAPIConfig()
            assert config.debug is False

    def test_config_repr_masks_secrets(self) -> None:
        """Test that string representation masks sensitive information."""
        config = BackendAPIConfig()
        config_str = str(config)

        assert config.jwt_secret not in config_str
