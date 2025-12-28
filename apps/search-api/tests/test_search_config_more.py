"""Unit tests to cover SearchAPIConfig validators and production checks."""

from __future__ import annotations

import pytest


def test_search_config_validators_reject_bad_values() -> None:
    from search_api.config.app import SearchAPIConfig

    with pytest.raises(ValueError):
        SearchAPIConfig(backend_api_timeout=0)

    with pytest.raises(ValueError):
        SearchAPIConfig(max_suggestions=0)

    with pytest.raises(ValueError):
        SearchAPIConfig(search_cache_ttl=0)

    with pytest.raises(ValueError):
        SearchAPIConfig(min_query_length=0)

    with pytest.raises(ValueError):
        SearchAPIConfig(backend_api_url="ftp://bad")


def test_search_config_production_overrides_and_validate_production_settings() -> None:
    from search_api.config.app import SearchAPIConfig

    cfg = SearchAPIConfig(
        environment="production",
        logs_dir="/tmp/logs",
        backend_api_url="http://localhost:8000",
        ml_api_url="http://localhost:9000",
    )

    ***REMOVED*** production override should disable file logging
    assert cfg.logs_dir is None

    issues = cfg.validate_production_settings()
    assert any("should use HTTPS" in i for i in issues)
    assert any("should not use localhost" in i for i in issues)

    s = str(cfg)
    assert "Search API Configuration" in s
