"""Redis repository for the Recommendation API.

This package provides access to Redis for caching and storage operations.
"""

from recommendation_api.repositories.redis.repository import (
    RedisRepository,
    delete_similar_movies,
    get_cache_info,
    get_redis_repository,
    get_similar_movies,
    store_similar_movies,
)

***REMOVED*** Define the public API
__all__ = [
    "RedisRepository",
    "get_redis_repository",
    "store_similar_movies",
    "get_similar_movies",
    "delete_similar_movies",
    "get_cache_info",
]
