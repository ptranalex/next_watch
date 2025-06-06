"""Redis service for caching recommendation data."""

import json
import logging
from typing import List, Dict, Any, Optional, Set, Tuple, Union, cast
import redis

from recommendation_api.config.app import settings

logger = logging.getLogger(__name__)


class RedisService:
    """Service for caching recommendation data in Redis."""

    def __init__(self) -> None:
        """Initialize Redis connection."""
        self.redis_client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_timeout=5,
        )
        self.similar_movies_prefix = "similar_movies:"
        self.popular_movies_prefix = "popular_movies:"
        self.trending_movies_prefix = "trending_movies:"
        ***REMOVED*** Default expiration time: 24 hours (in seconds)
        self.default_expiry = 86400

    def get_similar_movies(self, movie_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get similar movies for a movie from cache.

        Args:
            movie_id: ID of the movie to get similar movies for

        Returns:
            List of similar movie data or None if not in cache
        """
        key = f"{self.similar_movies_prefix}{movie_id}"

        try:
            data = self.redis_client.get(key)
            if data:
                logger.debug(f"Cache hit for similar movies to {movie_id}")
                return cast(List[Dict[str, Any]], json.loads(data))
            logger.debug(f"Cache miss for similar movies to {movie_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving similar movies from Redis: {e}")
            return None

    def store_similar_movies(
        self,
        movie_id: int,
        similar_movies: List[Dict[str, Any]],
        expire: Optional[int] = None,
    ) -> bool:
        """Store similar movies in cache.

        Args:
            movie_id: ID of the movie
            similar_movies: List of similar movie data
            expire: Expiration time in seconds

        Returns:
            True if stored successfully, False otherwise
        """
        key = f"{self.similar_movies_prefix}{movie_id}"
        expiry = expire or self.default_expiry

        try:
            self.redis_client.setex(
                key,
                expiry,
                json.dumps(similar_movies),
            )
            logger.debug(f"Stored similar movies for {movie_id} in cache")
            return True
        except Exception as e:
            logger.error(f"Error storing similar movies in Redis: {e}")
            return False

    def get_popular_movies(self, category: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Get popular movies from cache.

        Args:
            category: Optional category filter

        Returns:
            List of popular movie data or None if not in cache
        """
        key = f"{self.popular_movies_prefix}{category or 'all'}"

        try:
            data = self.redis_client.get(key)
            if data:
                return cast(List[Dict[str, Any]], json.loads(data))
            return None
        except Exception as e:
            logger.error(f"Error retrieving popular movies from Redis: {e}")
            return None

    def store_popular_movies(
        self,
        movies: List[Dict[str, Any]],
        category: Optional[str] = None,
        expire: Optional[int] = None,
    ) -> bool:
        """Store popular movies in cache.

        Args:
            movies: List of popular movie data
            category: Optional category filter
            expire: Expiration time in seconds

        Returns:
            True if stored successfully, False otherwise
        """
        key = f"{self.popular_movies_prefix}{category or 'all'}"
        expiry = expire or self.default_expiry

        try:
            self.redis_client.setex(
                key,
                expiry,
                json.dumps(movies),
            )
            logger.debug(f"Stored popular movies in cache (category: {category or 'all'})")
            return True
        except Exception as e:
            logger.error(f"Error storing popular movies in Redis: {e}")
            return False

    def clear_all_similar_movies(self) -> bool:
        """Clear all similar movie caches.

        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            ***REMOVED*** Find all keys with the similar_movies prefix
            pattern = f"{self.similar_movies_prefix}*"
            keys = self.redis_client.keys(pattern)

            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} similar movie cache entries")
            else:
                logger.info("No similar movie cache entries to clear")

            return True
        except Exception as e:
            logger.error(f"Error clearing similar movie cache: {e}")
            return False

    def get_cached_movie_ids(self) -> Set[int]:
        """Get set of movie IDs that have cached similarities.

        Returns:
            Set of movie IDs with cached similarities
        """
        try:
            pattern = f"{self.similar_movies_prefix}*"
            keys = self.redis_client.keys(pattern)

            movie_ids = set()
            for key in keys:
                ***REMOVED*** Extract movie ID from key
                movie_id_str = key.replace(self.similar_movies_prefix, "")
                try:
                    movie_ids.add(int(movie_id_str))
                except ValueError:
                    continue

            return movie_ids
        except Exception as e:
            logger.error(f"Error getting cached movie IDs: {e}")
            return set()

    def health_check(self) -> Tuple[bool, str]:
        """Check if Redis connection is healthy.

        Returns:
            Tuple of (is_healthy, status_message)
        """
        try:
            ***REMOVED*** Simple ping to check if Redis is responsive
            response = self.redis_client.ping()
            if response:
                return True, "healthy"
            return False, "not responding"
        except redis.exceptions.ConnectionError as e:
            return False, f"connection error: {str(e)}"
        except Exception as e:
            return False, f"error: {str(e)}"
