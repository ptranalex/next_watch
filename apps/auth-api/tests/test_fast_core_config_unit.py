"""Unit tests for auth-api fast-core config adapter."""

from auth_api.config.app import AuthAPIConfig
from auth_api.config.fast_core_config import (
    create_fast_core_config,
    get_service_timeout,
    get_service_url,
    is_feature_enabled,
)


def test_create_fast_core_config_smoke() -> None:
    cfg = AuthAPIConfig()
    fc = create_fast_core_config(cfg)

    assert fc.service_name == cfg.service_name
    assert fc.port == cfg.port

    # Auth service has no external URLs
    assert get_service_url(fc, "backend") is None
    assert get_service_timeout(fc, "backend") == 30

    assert is_feature_enabled(fc, "jwt_validation") is True
