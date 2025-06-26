***REMOVED*** type: ignore

"""Test configuration for Search API."""

import pytest
from search_api.config.app import SearchAPIConfig


def test_search_config_creation():
    """Test that SearchAPIConfig can be created with defaults."""
    config = SearchAPIConfig()

    assert config.service_name == "search-api"
    assert config.port == 8004
    assert config.max_suggestions == 50
    assert config.enable_search_analytics is True
    assert config.enable_semantic_search is False


def test_search_config_validation():
    """Test configuration validation."""
    ***REMOVED*** Test valid config
    config = SearchAPIConfig(
        max_suggestions=25, search_cache_ttl=600, backend_api_url="https://api.example.com"
    )

    assert config.max_suggestions == 25
    assert config.search_cache_ttl == 600
    assert config.backend_api_url == "https://api.example.com"


def test_search_config_redis_settings():
    """Test Redis-specific settings."""
    config = SearchAPIConfig()

    assert config.redis_suggestion_key_prefix == "suggestions:"
    assert config.redis_entity_key_prefix == "entity:"
    assert config.redis_search_result_prefix == "search_results:"
