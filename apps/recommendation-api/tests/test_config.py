"""Tests for Recommendation API configuration."""

import os
from unittest.mock import patch

from recommendation_api.config.app import RecommendationAPIConfig


def test_config_creation_defaults() -> None:
    config = RecommendationAPIConfig()

    assert config.service_name == "recommendation-api"
    assert config.port == 8002

    # Embeddings defaults
    assert config.embedding_dimension == 384
    assert config.batch_size == 32
    assert isinstance(config.embedding_model, str)

    # External service URLs
    assert config.backend_api_url.startswith(("http://", "https://"))
    assert config.ml_api_url.startswith(("http://", "https://"))
    assert config.qdrant_url.startswith(("http://", "https://"))


def test_config_env_overrides() -> None:
    with patch.dict(
        os.environ,
        {
            "PORT": "9002",
            "ENVIRONMENT": "production",
            "DEBUG": "true",
        },
        clear=True,
    ):
        config = RecommendationAPIConfig()

    # env override
    assert config.port == 9002
    assert config.environment == "production"
    # production overrides should force debug off
    assert config.debug is False
