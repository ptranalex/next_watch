"""Cache service for precomputing and managing recommendation data.

This module provides functionality for precomputing and caching various
types of recommendations, especially similar movie recommendations.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, Set, TypeVar, Callable, cast, Awaitable
import asyncio
import time
from functools import wraps
from datetime import datetime, timedelta

from sqlmodel import Session

from recommendation_api.db.operations import get_all_movie_ids
from recommendation_api.services.recommendation import RecommendationService
from recommendation_api.repositories.redis import get_redis_repository
from recommendation_api.config import settings

logger = logging.getLogger(__name__)

***REMOVED*** Type variables for decorators
F = TypeVar("F", bound=Callable[..., Any])
AF = TypeVar("AF", bound=Callable[..., Awaitable[Any]])


def timeit(func: F) -> F:
    """Decorator to measure execution time of a function."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result

    return cast(F, wrapper)


def async_timeit(func: AF) -> AF:
    """Decorator to measure execution time of an async function."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result

    return cast(AF, wrapper)


class CacheService:
    """Service for precomputing and caching recommendation data."""

    def __init__(self, session: Session):
        """Initialize the cache service.

        Args:
            session: Database session
        """
        self.session = session
        self.redis_repo = get_redis_repository()
        self.recommendation_service = RecommendationService(session)

    @timeit
    def precompute_similar_movies(
        self,
        movie_ids: Optional[List[int]] = None,
        limit: int = 50,
        min_score: float = 0.01,
        ttl: Optional[int] = None,
        batch_size: int = 100,
        max_workers: int = 4,
    ) -> Dict[str, Any]:
        """Precompute similar movies for given movie IDs and cache the results.

        Args:
            movie_ids: List of movie IDs to process (None for all movies)
            limit: Maximum number of similar movies per movie
            min_score: Minimum similarity score threshold
            ttl: Optional TTL override in seconds
            batch_size: Number of movies to process in each batch
            max_workers: Maximum number of worker threads

        Returns:
            Dictionary with processing statistics
        """
        ***REMOVED*** Get all movie IDs if not provided
        if movie_ids is None:
            movie_ids = get_all_movie_ids(self.session)
            logger.info(f"Fetched {len(movie_ids)} movie IDs from database")

        if not movie_ids:
            logger.warning("No movie IDs provided for precomputation")
            return {"processed": 0, "skipped": 0, "failed": 0, "total": 0, "elapsed_time": 0}

        total_movies = len(movie_ids)
        start_time = time.time()

        ***REMOVED*** Statistics
        processed = 0
        skipped = 0
        failed = 0

        ***REMOVED*** Process movies in batches to avoid memory issues
        for i in range(0, total_movies, batch_size):
            batch = movie_ids[i : i + batch_size]
            logger.info(
                f"Processing batch {i//batch_size + 1}/{(total_movies-1)//batch_size + 1} ({len(batch)} movies)"
            )

            ***REMOVED*** Store results in a dictionary to use batch storage
            batch_results: Dict[int, List[Tuple[int, float]]] = {}

            ***REMOVED*** Process each movie in the batch
            for movie_id in batch:
                try:
                    ***REMOVED*** Get similar movies
                    similar_movies, _ = self.recommendation_service.get_similar_movies(
                        movie_id=movie_id,
                        limit=limit,
                        min_score=min_score,
                    )

                    ***REMOVED*** Extract movie IDs and scores
                    similar_tuples = []
                    for movie in similar_movies:
                        if movie.id != movie_id and movie.score is not None:
                            similar_tuples.append((movie.id, movie.score))

                    if similar_tuples:
                        batch_results[movie_id] = similar_tuples
                        processed += 1
                    else:
                        logger.debug(f"No similar movies found for movie {movie_id}")
                        skipped += 1

                except Exception as e:
                    logger.error(f"Failed to process movie {movie_id}: {e}")
                    failed += 1

            ***REMOVED*** Store batch results
            if batch_results:
                try:
                    stored_count = self.redis_repo.batch_store_similar_movies(
                        batch_results, ttl=ttl
                    )
                    logger.info(f"Stored similar movies for {stored_count} movies in Redis")
                except Exception as e:
                    logger.error(f"Failed to store batch results: {e}")
                    failed += len(batch_results)
                    processed -= len(batch_results)

            ***REMOVED*** Log progress
            elapsed = time.time() - start_time
            movies_per_second = (processed + skipped + failed) / elapsed if elapsed > 0 else 0
            estimated_remaining = (
                (total_movies - (processed + skipped + failed)) / movies_per_second
                if movies_per_second > 0
                else 0
            )

            logger.info(
                f"Progress: {(processed + skipped + failed) / total_movies:.1%} - "
                f"Processed: {processed}, Skipped: {skipped}, Failed: {failed} - "
                f"Speed: {movies_per_second:.1f} movies/s - "
                f"ETA: {timedelta(seconds=int(estimated_remaining))}"
            )

        elapsed_time = time.time() - start_time

        ***REMOVED*** Final statistics
        result = {
            "processed": processed,
            "skipped": skipped,
            "failed": failed,
            "total": total_movies,
            "elapsed_time": elapsed_time,
            "movies_per_second": total_movies / elapsed_time if elapsed_time > 0 else 0,
        }

        logger.info(
            f"Precomputation completed in {elapsed_time:.2f} seconds - "
            f"Processed: {processed}, Skipped: {skipped}, Failed: {failed}"
        )

        return result

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the recommendation cache.

        Returns:
            Dictionary with cache statistics
        """
        try:
            ***REMOVED*** Get Redis cache info
            redis_info = self.redis_repo.get_cache_info()

            return {
                "redis_info": redis_info,
                "timestamp": datetime.now().isoformat(),
                "is_connected": self.redis_repo.ping(),
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}

    def clear_similar_movies_cache(self) -> Dict[str, Any]:
        """Clear all similar movies from the cache.

        Returns:
            Dictionary with operation results
        """
        try:
            start_time = time.time()
            deleted = self.redis_repo.clear_all_similar_movies()
            elapsed_time = time.time() - start_time

            return {
                "deleted_keys": deleted,
                "elapsed_time": elapsed_time,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to clear similar movies cache: {e}")
            return {"error": str(e)}


***REMOVED*** Factory function to create a cache service
def get_cache_service(session: Session) -> CacheService:
    """Get a cache service instance.

    Args:
        session: Database session

    Returns:
        CacheService instance
    """
    return CacheService(session)
