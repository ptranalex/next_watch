"""Example of how services can use enhanced cache methods directly without wrapper classes."""

import asyncio
from typing import Any

from cache import CacheManager
from cache.config import CacheSettings


async def main():
    """Example of using enhanced cache methods in a service."""
    ***REMOVED*** Initialize cache with service-specific settings
    settings = CacheSettings(
        redis_url="redis://localhost:6379/0",
        key_prefix="myservice:",
        cache_ttl_default=300,
    )
    cache = CacheManager.from_settings(settings)

    ***REMOVED*** Example service function using enhanced methods directly
    async def get_user_profile(user_id: int) -> dict[str, Any] | None:
        """Get user profile from cache or backend."""
        ***REMOVED*** Use get_dict for type-safe dictionary retrieval
        cache_key = f"user:{user_id}"
        user_data = await cache.get_dict(cache_key)

        if user_data:
            print(f"Cache hit for user {user_id}")
            return user_data

        ***REMOVED*** Simulate backend call
        print(f"Cache miss for user {user_id}, fetching from backend")
        user_data = {
            "id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com",
            "preferences": {"theme": "dark", "notifications": True},
        }

        ***REMOVED*** Use set_json_safe for error handling
        success = await cache.set_json_safe(cache_key, user_data, ttl=600)
        if success:
            print(f"Cached user {user_id} data")
        else:
            print(f"Failed to cache user {user_id} data")

        return user_data

    ***REMOVED*** Example service function using list type
    async def get_popular_movies() -> list:
        """Get popular movies from cache or backend."""
        cache_key = "movies:popular"
        movies = await cache.get_list(cache_key)

        if movies:
            print("Cache hit for popular movies")
            return movies

        ***REMOVED*** Simulate backend call
        print("Cache miss for popular movies, fetching from backend")
        movies = [
            {"id": 1, "title": "Movie 1", "rating": 4.5},
            {"id": 2, "title": "Movie 2", "rating": 4.8},
            {"id": 3, "title": "Movie 3", "rating": 4.2},
        ]

        ***REMOVED*** Use set_json_safe for error handling
        await cache.set_json_safe(cache_key, movies, ttl=300)
        return movies

    ***REMOVED*** Simulate service operations
    user = await get_user_profile(123)
    print(f"Got user: {user}")

    ***REMOVED*** Second call should hit cache
    user_again = await get_user_profile(123)
    print(f"Got user again: {user_again}")

    movies = await get_popular_movies()
    print(f"Got {len(movies)} popular movies")

    ***REMOVED*** Test error handling by deleting a non-existent key
    success = await cache.delete_key_safe("nonexistent:key")
    print(f"Delete operation succeeded: {success}")

    ***REMOVED*** Close cache connections
    await cache.close()


if __name__ == "__main__":
    asyncio.run(main())
