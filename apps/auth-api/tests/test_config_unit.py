"""Unit tests for auth-api config."""

import os
from unittest.mock import patch

from auth_api.config.app import AuthAPIConfig


def test_config_defaults() -> None:
    cfg = AuthAPIConfig()
    assert cfg.service_name == "auth-api"
    assert cfg.port == 8003


def test_config_env_overrides_production_forces_debug_false() -> None:
    with patch.dict(os.environ, {"ENVIRONMENT": "production", "DEBUG": "true"}, clear=True):
        cfg = AuthAPIConfig()
    assert cfg.environment == "production"
    assert cfg.debug is False
