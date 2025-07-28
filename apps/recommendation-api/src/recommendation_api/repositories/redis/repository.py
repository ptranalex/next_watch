"""Redis repository for caching recommendations in the Recommendation API.

This module provides the RedisRepository class for caching and retrieving
precomputed recommendation data, especially similar movie recommendations.
"""

from config.logging import get_logger
import json
from typing import List, Optional, Dict, Any, Tuple, Union, Set, cast
import redis
from redis.exceptions import RedisError

from recommendation_api.config import settings

logger = get_logger(__name__)

***REMOVED*** Default expiration time for cache entries (1 day in seconds)
DEFAULT_CACHE_TTL = 86400

***REMOVED*** Key prefixes for different types of data
SIMILAR_MOVIES_KEY_PREFIX = "similar_movies"


class RedisRepository:
    """Repository for caching recommendation data in Redis."""

    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl: int = DEFAULT_CACHE_TTL,
    ):
        """Initialize the Redis repository.

        Args:
            redis_url: Redis connection URL (defaults to config)
            default_ttl: Default TTL for cached items in seconds
        """
        self.redis_url = redis_url or settings.redis_url
        self.default_ttl = default_ttl
        self._client: Optional[redis.Redis] = None

    @property
    def client(self) -> redis.Redis:
        """Get the Redis client, creating it if needed.

        Returns:
            Redis client instance
        """
        if self._client is None:
            logger.debug(f"Initializing Redis client with URL: {self.redis_url}")
            try:
                self._client = redis.Redis.from_url(
                    self.redis_url,
                    decode_responses=True,  ***REMOVED*** Auto-decode bytes to strings
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                )
            except Exception as e:
                logger.error(f"Failed to initialize Redis client: {e}")
                raise
        return self._client

    def close(self) -> None:
        """Close the Redis client connection."""
        if self._client is not None:
            logger.debug("Closing Redis client connection")
            self._client.close()
            self._client = None

    def ping(self) -> bool:
        """Test the Redis connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            return bool(self.client.ping())
        except RedisError as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    def _similar_movies_key(self, movie_id: int) -> str:
        """Generate a Redis key for similar movies.

        Args:
            movie_id: Movie ID

        Returns:
            Redis key string
        """
        return f"{SIMILAR_MOVIES_KEY_PREFIX}:{movie_id}"

    def store_similar_movies(
        self,
        movie_id: int,
        similar_movies: List[Tuple[int, float]],
        ttl: Optional[int] = None,
    ) -> bool:
        """Store similar movies in Redis.

        Args:
            movie_id: Source movie ID
            similar_movies: List of tuples (movie_id, similarity_score)
            ttl: Optional TTL override in seconds

        Returns:
            True if successful, False otherwise
        """
        if not similar_movies:
            logger.warning(f"Not storing empty similar movies list for movie {movie_id}")
            return False

        key = self._similar_movies_key(movie_id)

        ***REMOVED*** Convert to a serializable format (list of lists)
        data = [[m_id, float(score)] for m_id, score in similar_movies]

        try:
            ***REMOVED*** Store as JSON string
            json_data = json.dumps(data)
            result = self.client.set(key, json_data, ex=ttl or self.default_ttl)
            logger.debug(f"Stored {len(similar_movies)} similar movies for movie {movie_id}")
            return bool(result)
        except (RedisError, TypeError, ValueError) as e:
            logger.error(f"Failed to store similar movies for {movie_id}: {e}")
            return False

    def get_similar_movies(
        self,
        movie_id: int,
        limit: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> Optional[List[Tuple[int, float]]]:
        """Get similar movies from Redis.

        Args:
            movie_id: Source movie ID
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of tuples (movie_id, similarity_score) or None if not found
        """
        key = self._similar_movies_key(movie_id)

        try:
            ***REMOVED*** Get the cached data
            json_data = self.client.get(key)
            if not json_data:
                logger.debug(f"No cached similar movies found for movie {movie_id}")
                return None

            ***REMOVED*** Parse the JSON data - cast to str to satisfy type checker
            data = json.loads(cast(str, json_data))

            ***REMOVED*** Convert to tuples and apply filters
            similar_movies = [(int(m_id), float(score)) for m_id, score in data]

            ***REMOVED*** Apply min_score filter if specified
            if min_score is not None:
                similar_movies = [
                    (m_id, score) for m_id, score in similar_movies if score >= min_score
                ]

            ***REMOVED*** Apply limit if specified
            if limit is not None and limit > 0:
                similar_movies = similar_movies[:limit]

            logger.debug(
                f"Retrieved {len(similar_movies)} similar movies for movie {movie_id} from cache"
            )
            return similar_movies

        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get similar movies for {movie_id}: {e}")
            return None

    def delete_similar_movies(self, movie_id: int) -> bool:
        """Delete similar movies from Redis.

        Args:
            movie_id: Source movie ID

        Returns:
            True if successful, False otherwise
        """
        key = self._similar_movies_key(movie_id)

        try:
            result = self.client.delete(key)
            logger.debug(f"Deleted similar movies for movie {movie_id}")
            ***REMOVED*** Cast result to int to satisfy type checker
            return bool(cast(int, result) > 0)
        except RedisError as e:
            logger.error(f"Failed to delete similar movies for {movie_id}: {e}")
            return False

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the Redis cache.

        Returns:
            Dictionary with cache statistics
        """
        try:
            ***REMOVED*** Get all similar movies keys
            pattern = f"{SIMILAR_MOVIES_KEY_PREFIX}:*"
            keys_result = self.client.keys(pattern)
            ***REMOVED*** Convert to list to satisfy type checker
            similar_keys = list(cast(List[str], keys_result))

            ***REMOVED*** Get server info
            info_result = self.client.info()
            ***REMOVED*** Convert to dict to satisfy type checker
            info = cast(Dict[str, Any], info_result)

            return {
                "similar_movies_count": len(similar_keys),
                "similar_movies_sample": similar_keys[:5] if similar_keys else [],
                "memory_used": info.get("used_memory_human", "unknown"),
                "total_keys": info.get("db0", {}).get("keys", 0),
                "uptime_days": info.get("uptime_in_days", 0),
            }
        except RedisError as e:
            logger.error(f"Failed to get cache info: {e}")
            return {"error": str(e)}

    def clear_all_similar_movies(self) -> int:
        """Clear all similar movies from the cache.

        Returns:
            Number of keys deleted
        """
        try:
            pattern = f"{SIMILAR_MOVIES_KEY_PREFIX}:*"
            keys_result = self.client.keys(pattern)
            ***REMOVED*** Convert to list to satisfy type checker
            keys = list(cast(List[str], keys_result))

            if not keys:
                logger.debug("No similar movies keys to delete")
                return 0

            ***REMOVED*** Delete keys in batches to avoid blocking Redis
            batch_size = 100
            deleted = 0

            for i in range(0, len(keys), batch_size):
                batch = keys[i : i + batch_size]
                ***REMOVED*** Cast result to int to satisfy type checker
                deleted += cast(int, self.client.delete(*batch))

            logger.info(f"Deleted {deleted} similar movies keys")
            return deleted
        except RedisError as e:
            logger.error(f"Failed to clear similar movies: {e}")
            return 0

    def batch_store_similar_movies(
        self,
        similar_movies_data: Dict[int, List[Tuple[int, float]]],
        ttl: Optional[int] = None,
    ) -> int:
        """Store multiple similar movies entries in batch.

        Args:
            similar_movies_data: Dict mapping movie_id to list of similar movies
            ttl: Optional TTL override in seconds

        Returns:
            Number of entries successfully stored
        """
        if not similar_movies_data:
            logger.warning("Empty data provided for batch storage")
            return 0

        ***REMOVED*** Use pipeline for better performance
        pipe = self.client.pipeline()
        count = 0

        try:
            for movie_id, similar_movies in similar_movies_data.items():
                if not similar_movies:
                    continue

                key = self._similar_movies_key(movie_id)
                ***REMOVED*** Convert to a serializable format
                data = [[m_id, float(score)] for m_id, score in similar_movies]
                json_data = json.dumps(data)

                pipe.set(key, json_data, ex=ttl or self.default_ttl)
                count += 1

            ***REMOVED*** Execute all commands in the pipeline
            pipe.execute()
            logger.info(f"Stored similar movies for {count} movies in batch")
            return count

        except (RedisError, TypeError, ValueError) as e:
            logger.error(f"Failed to batch store similar movies: {e}")
            return 0

    def batch_check_cached_movies(self, movie_ids: List[int]) -> Dict[int, bool]:
        """Check which movies already have cached similar movies.

        Args:
            movie_ids: List of movie IDs to check

        Returns:
            Dictionary mapping movie_id to True if cached, False otherwise
        """
        if not movie_ids:
            return {}

        try:
            ***REMOVED*** Use pipeline for batch checking
            pipe = self.client.pipeline()

            ***REMOVED*** Add EXISTS commands for all keys
            for movie_id in movie_ids:
                key = self._similar_movies_key(movie_id)
                pipe.exists(key)

            ***REMOVED*** Execute all checks at once
            results = pipe.execute()

            ***REMOVED*** Create result mapping
            cached_status = {}
            for movie_id, exists in zip(movie_ids, results):
                cached_status[movie_id] = bool(exists)

            cached_count = sum(cached_status.values())
            logger.debug(f"Batch check: {cached_count}/{len(movie_ids)} movies already cached")

            return cached_status

        except RedisError as e:
            logger.error(f"Failed to batch check cached movies: {e}")
            ***REMOVED*** Return all False on error
            return {movie_id: False for movie_id in movie_ids}

    def store_similar_movie_recommendations(
        self,
        movie_id: int,
        recommendations: List[Dict[str, Any]],
        ttl: Optional[int] = None,
    ) -> bool:
        """Store similar movie recommendations (lightweight objects) in Redis.

        Args:
            movie_id: Source movie ID
            recommendations: List of lightweight movie recommendation objects
            ttl: Optional TTL override in seconds

        Returns:
            True if successful, False otherwise
        """
        if not recommendations:
            logger.warning(f"Not storing empty recommendations list for movie {movie_id}")
            return False

        key = self._similar_movies_key(movie_id)

        try:
            ***REMOVED*** Store as JSON string
            json_data = json.dumps(recommendations)
            result = self.client.set(key, json_data, ex=ttl or self.default_ttl)
            logger.debug(
                f"Stored {len(recommendations)} similar movie recommendations for movie {movie_id}"
            )
            return bool(result)
        except (RedisError, TypeError, ValueError) as e:
            logger.error(f"Failed to store similar movie recommendations for {movie_id}: {e}")
            return False

    def get_similar_movie_recommendations(
        self,
        movie_id: int,
        limit: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """Get similar movie recommendations (lightweight objects) from Redis.

        Args:
            movie_id: Source movie ID
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of lightweight movie recommendation objects or None if not found
        """
        key = self._similar_movies_key(movie_id)

        try:
            ***REMOVED*** Get the cached data
            json_data = self.client.get(key)
            if not json_data:
                logger.debug(f"No cached similar movie recommendations found for movie {movie_id}")
                return None

            ***REMOVED*** Parse the JSON data
            recommendations = json.loads(cast(str, json_data))

            ***REMOVED*** Handle backward compatibility - check if it's the old format (list of lists)
            if recommendations and isinstance(recommendations[0], list):
                logger.debug(
                    f"Found old format cache for movie {movie_id}, returning None to trigger recomputation"
                )
                return None

            ***REMOVED*** Apply min_score filter if specified
            if min_score is not None:
                recommendations = [
                    rec for rec in recommendations if rec.get("similarity_score", 0) >= min_score
                ]

            ***REMOVED*** Apply limit if specified
            if limit is not None and limit > 0:
                recommendations = recommendations[:limit]

            logger.debug(
                f"Retrieved {len(recommendations)} similar movie recommendations for movie {movie_id} from cache"
            )
            return recommendations

        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get similar movie recommendations for {movie_id}: {e}")
            return None


***REMOVED*** Create a singleton instance for global use
_redis_repository: Optional[RedisRepository] = None


def get_redis_repository() -> RedisRepository:
    """Get the global Redis repository instance.

    Returns:
        RedisRepository instance
    """
    global _redis_repository
    if _redis_repository is None:
        _redis_repository = RedisRepository()
    return _redis_repository


***REMOVED*** For backwards compatibility, also provide standalone functions
def store_similar_movies(
    movie_id: int,
    similar_movies: List[Tuple[int, float]],
    ttl: Optional[int] = None,
) -> bool:
    """Store similar movies in Redis.

    Args:
        movie_id: Source movie ID
        similar_movies: List of tuples (movie_id, similarity_score)
        ttl: Optional TTL override in seconds

    Returns:
        True if successful, False otherwise
    """
    return get_redis_repository().store_similar_movies(movie_id, similar_movies, ttl)


def get_similar_movies(
    movie_id: int,
    limit: Optional[int] = None,
    min_score: Optional[float] = None,
) -> Optional[List[Tuple[int, float]]]:
    """Get similar movies from Redis.

    Args:
        movie_id: Source movie ID
        limit: Maximum number of results to return
        min_score: Minimum similarity score threshold

    Returns:
        List of tuples (movie_id, similarity_score) or None if not found
    """
    return get_redis_repository().get_similar_movies(movie_id, limit, min_score)


def delete_similar_movies(movie_id: int) -> bool:
    """Delete similar movies from Redis.

    Args:
        movie_id: Source movie ID

    Returns:
        True if successful, False otherwise
    """
    return get_redis_repository().delete_similar_movies(movie_id)


def get_cache_info() -> Dict[str, Any]:
    """Get information about the Redis cache.

    Returns:
        Dictionary with cache statistics
    """
    return get_redis_repository().get_cache_info()
