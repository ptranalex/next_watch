"""Unit tests for Recommendation API config and fast-core adapter."""

from __future__ import annotations

import importlib

import pytest


def test_reco_config_validators_and_weights_sum() -> None:
    from recommendation_api.config.app import RecommendationAPIConfig

    with pytest.raises(ValueError):
        RecommendationAPIConfig(backend_api_url="ftp://bad")

    with pytest.raises(ValueError):
        RecommendationAPIConfig(backend_api_timeout=0)

    with pytest.raises(ValueError):
        RecommendationAPIConfig(min_imdb_rating=11.0)

    with pytest.raises(ValueError):
        RecommendationAPIConfig(similarity_threshold=2.0)

    ***REMOVED*** weights must sum to 1.0
    with pytest.raises(ValueError):
        RecommendationAPIConfig(user_vector_weight=0.7, content_vector_weight=0.7)


def test_reco_config_production_overrides_and_validate_production_settings() -> None:
    from recommendation_api.config.app import RecommendationAPIConfig

    cfg = RecommendationAPIConfig(
        environment="production",
        logs_dir="/tmp/logs",
        backend_api_url="http://localhost:8000",
        ml_api_url="http://localhost:9000",
    )

    assert cfg.logs_dir is None

    issues = cfg.validate_production_settings()
    assert any("should use HTTPS" in i for i in issues)
    assert any("should not use localhost" in i for i in issues)

    assert cfg.qdrant_collection_name == cfg.vector_collection_name

    s = str(cfg)
    assert "Recommendation API Configuration" in s


def test_fast_core_config_adapter_smoke() -> None:
    from recommendation_api.config.app import RecommendationAPIConfig
    from recommendation_api.config.fast_core_config import (
        create_fast_core_config,
        get_service_timeout,
        get_service_url,
        is_feature_enabled,
    )

    cfg = RecommendationAPIConfig(environment="development")
    fc = create_fast_core_config(cfg)

    assert get_service_url(fc, "backend")
    assert get_service_timeout(fc, "backend") > 0
    assert is_feature_enabled(fc, "caching") is True


def test_module_level_settings_dev_log_level_override() -> None:
    import recommendation_api.config.app as app_module

    importlib.reload(app_module)

    assert app_module.settings.is_development
    assert app_module.settings.log_level == "DEBUG"
