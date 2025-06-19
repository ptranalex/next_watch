"""Tests for BFF cache integration."""

from unittest.mock import AsyncMock, patch

import pytest

from bff_api.services.cache_service import BFFCacheService, get_cache_service


class TestBFFCacheIntegration:
    """Test BFF cache service integration."""

    @pytest.mark.asyncio
    async def test_cache_service_initialization(self) -> None:
        """Test that cache service initializes correctly."""
        cache_service = get_cache_service()
        assert cache_service is not None
        assert isinstance(cache_service, BFFCacheService)

    @pytest.mark.asyncio
    async def test_movie_caching(self) -> None:
        """Test movie data caching functionality."""
        cache_service = get_cache_service()

        ***REMOVED*** Mock the cache manager to avoid Redis dependency
        with (
            patch.object(cache_service.cache_manager, "set_json", return_value=True) as mock_set,
            patch.object(cache_service.cache_manager, "get_json", return_value=None) as mock_get,
        ):

            ***REMOVED*** Test setting movie data
            movie_data = {"id": 123, "title": "Test Movie", "year": 2023}
            result = await cache_service.set_movie_details(123, movie_data)
            assert result is True
            mock_set.assert_called_once()

            ***REMOVED*** Test getting movie data (cache miss)
            cached_data = await cache_service.get_movie_details(123)
            assert cached_data is None
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_trending_movies_caching(self) -> None:
        """Test trending movies caching functionality."""
        cache_service = get_cache_service()

        with (
            patch.object(cache_service.cache_manager, "set_json", return_value=True) as mock_set,
            patch.object(cache_service.cache_manager, "get_json", return_value=None) as mock_get,
        ):

            ***REMOVED*** Test setting trending data
            trending_data = {"results": [{"id": 1, "title": "Trending Movie"}], "page": 1}
            result = await cache_service.set_trending_movies(trending_data, page=1)
            assert result is True
            mock_set.assert_called_once()

            ***REMOVED*** Test getting trending data (cache miss)
            cached_data = await cache_service.get_trending_movies(page=1)
            assert cached_data is None
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_watchlist_caching(self) -> None:
        """Test user watchlist caching functionality."""
        cache_service = get_cache_service()

        with (
            patch.object(cache_service.cache_manager, "set_json", return_value=True) as mock_set,
            patch.object(cache_service.cache_manager, "get_json", return_value=None) as mock_get,
            patch.object(
                cache_service.cache_manager, "delete_key", return_value=True
            ) as mock_delete,
        ):

            ***REMOVED*** Test setting watchlist data
            watchlist_data = [{"id": 1, "title": "Movie 1"}, {"id": 2, "title": "Movie 2"}]
            result = await cache_service.set_user_watchlist("user123", watchlist_data)
            assert result is True
            mock_set.assert_called_once()

            ***REMOVED*** Test getting watchlist data (cache miss)
            cached_data = await cache_service.get_user_watchlist("user123")
            assert cached_data is None
            mock_get.assert_called_once()

            ***REMOVED*** Test invalidating watchlist
            result = await cache_service.invalidate_user_watchlist("user123")
            assert result is True
            mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_results_caching(self) -> None:
        """Test search results caching functionality."""
        cache_service = get_cache_service()

        with (
            patch.object(cache_service.cache_manager, "set_json", return_value=True) as mock_set,
            patch.object(cache_service.cache_manager, "get_json", return_value=None) as mock_get,
        ):

            ***REMOVED*** Test setting search results
            search_data = {"results": [{"id": 1, "title": "Search Result"}], "query": "test"}
            result = await cache_service.set_search_results("Test Query", search_data, page=1)
            assert result is True
            mock_set.assert_called_once()

            ***REMOVED*** Verify query normalization
            args, kwargs = mock_set.call_args
            assert "test query" in args[0]  ***REMOVED*** Key should contain normalized query

            ***REMOVED*** Test getting search results (cache miss)
            cached_data = await cache_service.get_search_results("Test Query", page=1)
            assert cached_data is None
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check(self) -> None:
        """Test cache service health check."""
        cache_service = get_cache_service()

        with patch.object(
            cache_service.cache_manager, "health_check", return_value=True
        ) as mock_health:
            result = await cache_service.health_check()
            assert result is True
            mock_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_stats(self) -> None:
        """Test cache statistics retrieval."""
        cache_service = get_cache_service()

        with patch.object(cache_service, "health_check", return_value=True) as mock_health:
            stats = await cache_service.get_cache_stats()

            assert isinstance(stats, dict)
            assert "healthy" in stats
            assert "provider" in stats
            assert "settings" in stats
            assert "timestamp" in stats

            assert stats["healthy"] is True
            assert stats["provider"] == "redis"
            mock_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_stats_error_handling(self) -> None:
        """Test cache statistics error handling."""
        cache_service = get_cache_service()

        with patch.object(
            cache_service, "health_check", side_effect=Exception("Test error")
        ) as mock_health:
            stats = await cache_service.get_cache_stats()

            assert isinstance(stats, dict)
            assert "healthy" in stats
            assert "error" in stats
            assert "timestamp" in stats

            assert stats["healthy"] is False
            assert "Test error" in stats["error"]
            mock_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test cache service as async context manager."""
        with patch("bff_api.services.cache_service.BFFCacheService.close") as mock_close:
            async with BFFCacheService() as cache_service:
                assert cache_service is not None
                assert isinstance(cache_service, BFFCacheService)

            mock_close.assert_called_once()
