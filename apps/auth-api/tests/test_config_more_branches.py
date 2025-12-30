"""Additional tests to cover auth-api config branch behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

from auth_api.config.app import AuthAPIConfig


def test_production_overrides_enforce_https_and_disable_logs_dir(tmp_path: Path) -> None:
    cfg = AuthAPIConfig(
        environment="production",
        jwt_secret="this-is-a-secure-jwt-secret-value",
        require_https_production=False,
        logs_dir=str(tmp_path),
    )

    # Overrides should enforce HTTPS and disable file logging
    assert cfg.require_https_production is True
    assert cfg.logs_dir is None


def test_production_rejects_default_jwt_secret() -> None:
    with pytest.raises(ValueError):
        AuthAPIConfig(
            environment="production", jwt_secret="change_this_in_production_very_important"
        )


def test_jwk_parsing() -> None:
    cfg = AuthAPIConfig(jwt_jwk='{"kty":"oct","k":"abc"}')
    assert isinstance(cfg.jwt_jwk, dict)

    cfg2 = AuthAPIConfig(jwt_jwk={"kty": "oct", "k": "abc"})
    assert cfg2.jwt_jwk["kty"] == "oct"

    cfg3 = AuthAPIConfig(jwt_jwk="")
    assert cfg3.jwt_jwk is None

    with pytest.raises(ValueError):
        AuthAPIConfig(jwt_jwk="not-json")


def test_production_cors_wildcard_warning_path() -> None:
    # Just exercise the validator path; no assertion on logs.
    cfg = AuthAPIConfig(
        environment="production",
        jwt_secret="this-is-a-secure-jwt-secret-value",
        cors_origins=["*"],
    )
    assert "*" in cfg.cors_origins
