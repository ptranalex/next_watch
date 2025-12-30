"""Basic usage example for the cache library."""

import asyncio
from typing import cast

from cache import CacheManager, CacheSettings
from cache.types import JSONSerializable


async def basic_example() -> None:
    """Demonstrate basic cache operations."""
    print("🚀 Cache Library Basic Usage Example")
    print("=" * 50)

    # Create cache manager with default settings
    cache = CacheManager.from_settings()

    try:
        # Test health check
        print("\n1. Health Check")
        healthy = await cache.health_check()
        print(f"   Cache healthy: {healthy}")

        if not healthy:
            print("   ⚠️  Redis not available - skipping cache operations")
            return

        # Test basic operations
        print("\n2. Basic Cache Operations")

        # Set some data
        user_data: dict[str, int | str | dict[str, str | bool]] = {
            "id": 123,
            "name": "John Doe",
            "email": "john@example.com",
            "preferences": {"theme": "dark", "notifications": True},
        }

        key = "user:123"
        print(f"   Setting cache key: {key}")
        success = await cache.set_json(key, cast(JSONSerializable, user_data), ttl=300)  # 5 minutes
        print(f"   Set successful: {success}")

        # Get the data back
        print(f"   Getting cache key: {key}")
        retrieved_data = await cache.get_json(key)
        print(f"   Retrieved data: {retrieved_data}")

        # Check if key exists
        exists = await cache.exists(key)
        print(f"   Key exists: {exists}")

        # Test domain-specific TTL
        print("\n3. Domain-Specific TTL")

        movie_data = {"id": 456, "title": "The Matrix", "year": 1999, "rating": 8.7}

        movie_key = "movie:456"
        print(f"   Setting movie cache with domain TTL: {movie_key}")
        success = await cache.set_json_with_domain_ttl(
            movie_key, cast(JSONSerializable, movie_data), "movie"
        )
        print(f"   Movie TTL: {cache.get_ttl_for_domain('movie')} seconds")
        print(f"   Set successful: {success}")

        # Retrieve movie data
        retrieved_movie = await cache.get_json(movie_key)
        print(f"   Retrieved movie: {retrieved_movie}")

        # Test different domains
        print("\n4. Domain TTL Examples")
        domains = ["movie", "user", "popular", "unknown"]
        for domain in domains:
            ttl = cache.get_ttl_for_domain(domain)
            print(f"   {domain:10} TTL: {ttl:4} seconds")

        # Cleanup
        print("\n5. Cleanup")
        deleted_user = await cache.delete_key(key)
        deleted_movie = await cache.delete_key(movie_key)
        print(f"   Deleted user key: {deleted_user}")
        print(f"   Deleted movie key: {deleted_movie}")

        # Verify deletion
        user_after_delete = await cache.get_json(key)
        movie_after_delete = await cache.get_json(movie_key)
        print(f"   User data after delete: {user_after_delete}")
        print(f"   Movie data after delete: {movie_after_delete}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    finally:
        # Always close the cache manager
        await cache.close()
        print("\n✅ Cache manager closed")


async def custom_settings_example() -> None:
    """Demonstrate cache with custom settings."""
    print("\n" + "=" * 50)
    print("🔧 Custom Settings Example")
    print("=" * 50)

    # Create custom settings
    settings = CacheSettings(
        redis_url="redis://localhost:6379/0",
        key_prefix="example",
        cache_ttl_default=600,  # 10 minutes default
    )

    # Print settings
    print(f"Redis URL: {settings.redis_url}")
    print(f"Key prefix: {settings.key_prefix}")
    print(f"Default TTL: {settings.cache_ttl_default}")

    cache = CacheManager.from_settings(settings)

    try:
        healthy = await cache.health_check()
        print(f"Custom cache healthy: {healthy}")

        if healthy:
            print(f"Key prefix: {settings.key_prefix}")
            print(f"Default TTL: {settings.cache_ttl_default}")

            # Test with custom prefix
            test_key = "test:custom"
            test_data = {"message": "Custom settings work!"}

            await cache.set_json(test_key, cast(JSONSerializable, test_data))
            retrieved = await cache.get_json(test_key)
            print(f"Retrieved with custom prefix: {retrieved}")

            # Cleanup
            await cache.delete_key(test_key)

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        await cache.close()


async def main() -> None:
    """Run all examples."""
    await basic_example()
    await custom_settings_example()

    print("\n🎉 All examples completed!")
    print("\nNext steps:")
    print("- Try running with Redis: docker run -d -p 6379:6379 redis:alpine")
    print("- Check the examples/ directory for more usage patterns")
    print("- Read the README.md for full documentation")


if __name__ == "__main__":
    asyncio.run(main())
