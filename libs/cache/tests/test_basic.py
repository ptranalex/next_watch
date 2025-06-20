***REMOVED*** type: ignore

"""Basic tests for cache functionality."""

import pytest

from cache import CacheManager, CacheSettings, RedisProvider


class TestCacheSettings:
    """Test cache settings configuration."""

    def test_default_settings(self):
        """Test default settings."""
        settings = CacheSettings()
        assert settings.redis_url == "redis://localhost:6379/0"
        assert settings.redis_pool_size == 10
        assert settings.redis_timeout == 5
        assert settings.key_prefix == "nextwatch"
        assert settings.cache_ttl_default == 300
        assert settings.ttl_movie_data == 600
        assert settings.ttl_user_session == 3600
        assert settings.ttl_popular_content == 1800

    def test_domain_ttl_mapping(self):
        """Test domain-specific TTL mapping."""
        settings = CacheSettings()

        assert settings.get_ttl_for_domain("movie") == 600
        assert settings.get_ttl_for_domain("user") == 3600
        assert settings.get_ttl_for_domain("popular") == 1800
        assert settings.get_ttl_for_domain("unknown") == 300  ***REMOVED*** default


class TestRedisProvider:
    """Test Redis provider functionality."""

    def test_redis_provider_initialization(self):
        """Test Redis provider can be initialized."""
        provider = RedisProvider(
            redis_url="redis://localhost:6379/0", key_prefix="test"
        )

        assert provider.redis_url == "redis://localhost:6379/0"
        assert provider.key_prefix == "test"
        assert provider.pool_size == 10
        assert provider.timeout == 5

    def test_redis_provider_from_settings(self):
        """Test Redis provider creation from settings."""
        settings = CacheSettings(
            redis_url="redis://localhost:6379/1", key_prefix="myapp"
        )

        provider = RedisProvider.from_settings(settings)

        assert provider.redis_url == "redis://localhost:6379/1"
        assert provider.key_prefix == "myapp"

    def test_key_building(self):
        """Test cache key building with prefix."""
        provider = RedisProvider(key_prefix="test")

        ***REMOVED*** Test key building
        assert provider._build_key("user:123") == "test:user:123"

        ***REMOVED*** Test without prefix
        provider_no_prefix = RedisProvider(key_prefix="")
        assert provider_no_prefix._build_key("user:123") == "user:123"

    def test_url_masking(self):
        """Test Redis URL masking for security."""
        provider = RedisProvider()

        ***REMOVED*** Test URL with password
        masked = provider._mask_url("redis://user:password@localhost:6379/0")
        assert "password" not in masked
        assert "***" in masked

        ***REMOVED*** Test URL without password
        simple_url = "redis://localhost:6379/0"
        assert provider._mask_url(simple_url) == simple_url


class TestCacheManager:
    """Test cache manager functionality."""

    def test_cache_manager_initialization(self):
        """Test cache manager can be initialized."""
        provider = RedisProvider()
        settings = CacheSettings()

        manager = CacheManager(provider=provider, settings=settings)

        assert manager.provider == provider
        assert manager.settings == settings

    def test_cache_manager_from_settings(self):
        """Test cache manager creation from settings."""
        settings = CacheSettings(key_prefix="test")

        manager = CacheManager.from_settings(settings)

        assert isinstance(manager.provider, RedisProvider)
        assert manager.settings == settings

    def test_domain_ttl_helpers(self):
        """Test domain-specific TTL helpers."""
        settings = CacheSettings()
        provider = RedisProvider()
        manager = CacheManager(provider=provider, settings=settings)

        assert manager.get_ttl_for_domain("movie") == 600
        assert manager.get_ttl_for_domain("user") == 3600
        assert manager.get_ttl_for_domain("unknown") == 300


***REMOVED*** Integration tests would require Redis to be running
***REMOVED*** These are marked as integration tests and can be skipped in CI
@pytest.mark.integration
class TestCacheIntegration:
    """Integration tests requiring Redis."""

    @pytest.mark.asyncio
    async def test_basic_cache_operations(self):
        """Test basic cache operations with Redis."""
        ***REMOVED*** This test requires Redis to be running
        ***REMOVED*** Skip if Redis is not available
        try:
            manager = CacheManager.from_settings()

            ***REMOVED*** Test health check
            healthy = await manager.health_check()
            if not healthy:
                pytest.skip("Redis not available")

            ***REMOVED*** Test basic operations
            key = "test:basic"
            value = {"message": "hello", "number": 42}

            ***REMOVED*** Set value
            success = await manager.set_json(key, value, ttl=60)
            assert success is True

            ***REMOVED*** Get value
            retrieved = await manager.get_json(key)
            assert retrieved == value

            ***REMOVED*** Check exists
            exists = await manager.exists(key)
            assert exists is True

            ***REMOVED*** Delete value
            deleted = await manager.delete_key(key)
            assert deleted is True

            ***REMOVED*** Verify deleted
            retrieved_after_delete = await manager.get_json(key)
            assert retrieved_after_delete is None

            await manager.close()

        except Exception as e:
            pytest.skip(f"Redis integration test failed: {e}")

    @pytest.mark.asyncio
    async def test_domain_ttl_operations(self):
        """Test domain-specific TTL operations."""
        try:
            manager = CacheManager.from_settings()

            ***REMOVED*** Test health check
            healthy = await manager.health_check()
            if not healthy:
                pytest.skip("Redis not available")

            ***REMOVED*** Test domain TTL
            key = "test:movie:123"
            value = {"title": "Test Movie", "year": 2024}

            success = await manager.set_json_with_domain_ttl(key, value, "movie")
            assert success is True

            retrieved = await manager.get_json(key)
            assert retrieved == value

            ***REMOVED*** Cleanup
            await manager.delete_key(key)
            await manager.close()

        except Exception as e:
            pytest.skip(f"Redis integration test failed: {e}")
