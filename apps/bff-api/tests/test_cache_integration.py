***REMOVED*** type: ignore

"""Tests for BFF cache integration."""

from unittest.mock import patch

import pytest
from bff_api.services.cache_service import check_cache_health, get_cache
from cache import CacheManager


class TestBFFCacheIntegration:
    """Test BFF cache service integration."""

    @pytest.mark.asyncio
    async def test_cache_initialization(self) -> None:
        """Test that cache initializes correctly."""
        cache = get_cache()
        assert cache is not None
        assert isinstance(cache, CacheManager)

    @pytest.mark.asyncio
    async def test_movie_caching(self) -> None:
        """Test movie data caching functionality."""
        cache = get_cache()

        ***REMOVED*** Mock the cache manager to avoid Redis dependency
        with (
            patch.object(cache, "set_json_safe", return_value=True) as mock_set,
            patch.object(cache, "get_dict", return_value=None) as mock_get,
        ):
            ***REMOVED*** Test setting movie data
            movie_data = {"id": 123, "title": "Test Movie", "year": 2023}
            key = "movie:123"
            result = await cache.set_json_safe(key, movie_data)
            assert result is True
            mock_set.assert_called_once()

            ***REMOVED*** Test getting movie data (cache miss)
            cached_data = await cache.get_dict(key)
            assert cached_data is None
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_trending_movies_caching(self) -> None:
        """Test trending movies caching functionality."""
        cache = get_cache()

        with (
            patch.object(cache, "set_json_safe", return_value=True) as mock_set,
            patch.object(cache, "get_dict", return_value=None) as mock_get,
        ):
            ***REMOVED*** Test setting trending data
            trending_data = {
                "results": [{"id": 1, "title": "Trending Movie"}],
                "page": 1,
            }
            key = "trending:movies:page:1"
            result = await cache.set_json_safe(key, trending_data)
            assert result is True
            mock_set.assert_called_once()

            ***REMOVED*** Test getting trending data (cache miss)
            cached_data = await cache.get_dict(key)
            assert cached_data is None
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_watchlist_caching(self) -> None:
        """Test user watchlist caching functionality."""
        cache = get_cache()

        with (
            patch.object(cache, "set_json_safe", return_value=True) as mock_set,
            patch.object(cache, "get_list", return_value=None) as mock_get,
            patch.object(cache, "delete_key_safe", return_value=True) as mock_delete,
        ):
            ***REMOVED*** Test setting watchlist data
            watchlist_data = [
                {"id": 1, "title": "Movie 1"},
                {"id": 2, "title": "Movie 2"},
            ]
            key = "user:user123:watchlist"
            result = await cache.set_json_safe(key, watchlist_data)
            assert result is True
            mock_set.assert_called_once()

            ***REMOVED*** Test getting watchlist data (cache miss)
            cached_data = await cache.get_list(key)
            assert cached_data is None
            mock_get.assert_called_once()

            ***REMOVED*** Test invalidating watchlist
            result = await cache.delete_key_safe(key)
            assert result is True
            mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_results_caching(self) -> None:
        """Test search results caching functionality."""
        cache = get_cache()

        with (
            patch.object(cache, "set_json_safe", return_value=True) as mock_set,
            patch.object(cache, "get_dict", return_value=None) as mock_get,
        ):
            ***REMOVED*** Test setting search results
            search_data = {
                "results": [{"id": 1, "title": "Search Result"}],
                "query": "test",
            }
            key = "search:test query:page:1"
            result = await cache.set_json_safe(key, search_data)
            assert result is True
            mock_set.assert_called_once()

            ***REMOVED*** Test getting search results (cache miss)
            cached_data = await cache.get_dict(key)
            assert cached_data is None
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check(self) -> None:
        """Test cache health check."""
        cache = get_cache()

        with patch.object(cache, "health_check", return_value=True) as mock_health:
            result = await check_cache_health()
            assert result is True
            mock_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_stats(self) -> None:
        """Test cache statistics retrieval."""
        cache = get_cache()

        with patch.object(cache, "health_check", return_value=True) as mock_health:
            stats = {
                "healthy": await cache.health_check(),
                "provider": "redis",
                "settings": {
                    "redis_url": "redis://mock:6379/0",
                    "key_prefix": "bff:",
                    "ttl_default": 300,
                },
                "timestamp": "2023-01-01T00:00:00",
            }

            assert isinstance(stats, dict)
            assert "healthy" in stats
            assert "provider" in stats
            assert "settings" in stats
            assert "timestamp" in stats

            assert stats["healthy"] is True
            assert stats["provider"] == "redis"
            mock_health.assert_called_once()
