"""Unit tests to cover ML config, fast-core adapter, and embedding models."""

from __future__ import annotations

import pytest


def test_ml_config_validators_and_helpers() -> None:
    from ml_api.config.app import MLAPIConfig, get_ml_settings

    with pytest.raises(ValueError):
        MLAPIConfig(max_batch_size=0)

    cfg = MLAPIConfig(model_cache_dir="/tmp", enable_embeddings=False)
    assert cfg.model_cache_path is not None

    ***REMOVED*** ensure caching singleton works
    a = get_ml_settings()
    b = get_ml_settings()
    assert a is b


def test_ml_config_production_settings_warnings() -> None:
    from ml_api.config.app import MLAPIConfig

    cfg = MLAPIConfig(environment="production", enable_model_caching=False, max_batch_size=200)
    issues = cfg.validate_production_settings()
    assert any("Model caching" in i for i in issues)
    assert any("Large batch" in i for i in issues)


def test_ml_fast_core_config_adapter() -> None:
    from ml_api.config.app import MLAPIConfig
    from ml_api.config.fast_core_config import create_fast_core_config, is_feature_enabled

    cfg = MLAPIConfig(environment="development")
    fc = create_fast_core_config(cfg)
    assert is_feature_enabled(fc, "embeddings") is True


def test_embedding_models_construct() -> None:
    from ml_api.models.embedding import (
        ModelInfo,
        MovieEmbeddingRequest,
        MovieEmbeddingResponse,
        UserEmbeddingRequest,
        UserEmbeddingResponse,
        UserMovieRating,
    )

    req = MovieEmbeddingRequest(movie_id="1", title="T", overview="O")
    assert req.genres == []

    resp = MovieEmbeddingResponse(movie_id="1", embedding=[0.1], model_id="m", dimensions=1)
    assert resp.dimensions == 1

    ureq = UserEmbeddingRequest(
        user_id="u", liked_movies=[UserMovieRating(movie_id="1", rating=5.0)]
    )
    assert ureq.watched_genres == {}

    uresp = UserEmbeddingResponse(user_id="u", preference_vector=[0.0], model_id="m", dimensions=1)
    assert uresp.model_id == "m"

    mi = ModelInfo(model_id="m", dimensions=1, version="1", status="loaded", health="ok")
    assert mi.health == "ok"
