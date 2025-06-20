"""Embedding service for generating and managing movie embeddings using API-based architecture."""

import asyncio
import time
from datetime import datetime
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set, Tuple, TypeVar, cast

from config.logging import get_logger

from recommendation_api.config import settings
from recommendation_api.repositories.vector.client import get_qdrant_client
from recommendation_api.repositories.vector.repository import VectorRepository
from recommendation_api.services.backend_client import BackendClient
from recommendation_api.services.ml_api_client import get_ml_api_client
from recommendation_api.services.movie_adapter import MovieDataAdapter
from recommendation_api.services.vector_service import VectorService

logger = get_logger(__name__)

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


class EmbeddingService:
    """Service for generating and managing movie embeddings using API-based architecture."""

    def __init__(
        self,
        backend_client: BackendClient,
        movie_adapter: MovieDataAdapter,
        vector_service: VectorService,
        vector_repo: VectorRepository,
    ):
        """Initialize the embedding service.

        Args:
            backend_client: Client for backend API communication
            movie_adapter: Adapter for movie data operations
            vector_service: Service for vector operations
            vector_repo: Repository for vector storage
        """
        self.backend_client = backend_client
        self.movie_adapter = movie_adapter
        self.vector_service = vector_service
        self.vector_repo = vector_repo
        self.qdrant_client = get_qdrant_client()

    async def get_movies_for_embeddings(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get movies from the backend API that need embeddings.

        Args:
            limit: Maximum number of movies to return

        Returns:
            List of movie data dictionaries
        """
        movies = []
        page = 1
        page_size = 100

        while True:
            response = await self.backend_client.get_movies(page=page, limit=page_size)
            batch_movies = response.get("results", [])

            if not batch_movies:
                break

            movies.extend(batch_movies)

            ***REMOVED*** Apply limit if specified
            if limit and len(movies) >= limit:
                movies = movies[:limit]
                break

            ***REMOVED*** Check if there are more pages
            if not response.get("has_next", False):
                break

            page += 1

        logger.info(f"Fetched {len(movies)} movies from backend API for embeddings")
        return movies

    @async_timeit
    async def generate_embeddings(
        self,
        movie_ids: Optional[List[int]] = None,
        force: bool = False,
        limit: Optional[int] = None,
        batch_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate embeddings for movies.

        Args:
            movie_ids: Specific movie IDs to process (None for all movies)
            force: Force regeneration of existing embeddings
            limit: Maximum number of movies to process
            batch_size: Number of movies to process in each batch

        Returns:
            Dictionary with processing statistics
        """
        ***REMOVED*** Use config defaults if not provided
        actual_batch_size = batch_size or settings.batch_size

        ***REMOVED*** Ensure vector collection exists
        if not self.vector_service.ensure_collection_exists():
            raise RuntimeError("Failed to create vector database collection")

        ***REMOVED*** Get movies to process
        if movie_ids:
            ***REMOVED*** Get specific movies by IDs
            movies_data = []
            for movie_id in movie_ids:
                movie_data = await self.movie_adapter.get_movie_by_id(movie_id)
                if movie_data:
                    movies_data.append(movie_data)
        else:
            ***REMOVED*** Get all movies from API
            movies_data = await self.get_movies_for_embeddings(limit=limit)

        if not movies_data:
            logger.warning("No movies found for embedding generation")
            return {"total": 0, "processed": 0, "skipped": 0, "failed": 0, "elapsed_time": 0}

        total_movies = len(movies_data)
        start_time = time.time()

        ***REMOVED*** Statistics
        processed = 0
        skipped = 0
        failed = 0

        logger.info(f"Starting embedding generation for {total_movies} movies")

        ***REMOVED*** Process movies in batches
        for i in range(0, total_movies, actual_batch_size):
            batch = movies_data[i : i + actual_batch_size]
            batch_num = i // actual_batch_size + 1
            total_batches = (total_movies - 1) // actual_batch_size + 1

            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} movies)")

            ***REMOVED*** Process each movie in the batch
            for movie_data in batch:
                movie_id = movie_data.get("id")
                if not movie_id:
                    failed += 1
                    logger.warning(f"Movie data missing ID: {movie_data}")
                    continue

                try:
                    ***REMOVED*** Check if embedding already exists (if not forcing)
                    if not force:
                        existing_embedding = self.vector_repo.get_movie_embedding(movie_id)
                        if existing_embedding:
                            skipped += 1
                            logger.debug(f"Movie {movie_id}: Embedding already exists, skipping")
                            continue

                    ***REMOVED*** Generate and store embedding
                    success = await self._generate_movie_embedding(movie_data)
                    if success:
                        processed += 1
                        logger.debug(f"Movie {movie_id}: Successfully generated embedding")
                    else:
                        failed += 1
                        logger.error(f"Movie {movie_id}: Failed to generate embedding")

                except Exception as e:
                    failed += 1
                    logger.error(f"Movie {movie_id}: Error generating embedding - {e}")

            ***REMOVED*** Log batch progress
            elapsed = time.time() - start_time
            total_processed = processed + skipped + failed
            movies_per_second = total_processed / elapsed if elapsed > 0 else 0

            logger.info(
                f"Batch {batch_num}/{total_batches} complete - "
                f"Processed: {processed}, Skipped: {skipped}, Failed: {failed} - "
                f"Speed: {movies_per_second:.1f} movies/s"
            )

        elapsed_time = time.time() - start_time

        ***REMOVED*** Final statistics
        result = {
            "total": total_movies,
            "processed": processed,
            "skipped": skipped,
            "failed": failed,
            "elapsed_time": elapsed_time,
            "movies_per_second": total_movies / elapsed_time if elapsed_time > 0 else 0,
        }

        logger.info(
            f"Embedding generation completed in {elapsed_time:.2f} seconds - "
            f"Processed: {processed}, Skipped: {skipped}, Failed: {failed}"
        )

        return result

    async def _generate_movie_embedding(self, movie_data: Dict[str, Any]) -> bool:
        """Generate embedding for a single movie.

        Args:
            movie_data: Movie data dictionary from backend API

        Returns:
            True if successful, False otherwise
        """
        try:
            movie_id = movie_data.get("id")
            if not movie_id:
                return False

            ***REMOVED*** Create text representation for embedding
            title = movie_data.get("title", "")
            overview = movie_data.get("overview", "")
            genres = movie_data.get("genres", [])

            ***REMOVED*** Handle genres - they might be strings or objects
            genre_names = []
            for genre in genres:
                if isinstance(genre, str):
                    genre_names.append(genre)
                elif isinstance(genre, dict) and "name" in genre:
                    genre_names.append(genre["name"])

            ***REMOVED*** Create combined text for embedding
            text_parts = [title]
            if overview:
                text_parts.append(overview)
            if genre_names:
                text_parts.append(f"Genres: {', '.join(genre_names)}")

            text_content = " ".join(text_parts)

            if not text_content.strip():
                logger.warning(f"Movie {movie_id}: No text content for embedding")
                return False

            ***REMOVED*** Generate embedding using ML API client
            ml_client = get_ml_api_client()

            ***REMOVED*** Prepare movie features for the ML API
            movie_features = {
                "movie_id": movie_id,
                "title": title,
                "overview": overview,
                "genres": genre_names,
                "release_year": movie_data.get("release_year"),
                "imdb_rating": movie_data.get("imdb_rating"),
                "director": movie_data.get("director", ""),
                "cast": movie_data.get("cast", []),
            }

            embedding = await ml_client.generate_movie_embedding(movie_features)
            if not embedding:
                return False

            ***REMOVED*** Store embedding in vector database with comprehensive metadata
            metadata = {
                "movie_id": movie_id,
                "title": title,
                "genres": genre_names,
                "has_overview": bool(overview),
                ***REMOVED*** Add comprehensive metadata to eliminate backend API calls
                "overview": overview,
                "release_date": movie_data.get("release_date"),
                "imdb_rating": movie_data.get("imdb_rating"),
                "tmdb_rating": movie_data.get("vote_average"),
                "poster_url": movie_data.get("poster_url"),
                "backdrop_url": movie_data.get("backdrop_url"),
                "runtime": movie_data.get("runtime"),
                "imdb_id": movie_data.get("imdb_id"),
                "original_title": movie_data.get("original_title"),
                "language": movie_data.get("language"),
                "popularity": movie_data.get("popularity"),
                "vote_count": movie_data.get("vote_count"),
                "adult": movie_data.get("adult", False),
                ***REMOVED*** Store additional metadata that might be useful
                "metacritic_rating": movie_data.get("metacritic_rating"),
                "rotten_tomatoes_rating": movie_data.get("rotten_tomatoes_rating"),
                "awards": movie_data.get("awards"),
                ***REMOVED*** Store metadata version for future migrations
                "metadata_version": "v2",
            }

            success = self.vector_repo.store_movie_embedding(
                movie_id=movie_id, embedding=embedding, metadata=metadata
            )

            return success

        except Exception as e:
            logger.error(
                f"Error generating embedding for movie {movie_data.get('id', 'unknown')}: {e}"
            )
            return False

    def get_embedding_status(self) -> Dict[str, Any]:
        """Get current embedding status and statistics.

        Returns:
            Dictionary with embedding status information
        """
        try:
            ***REMOVED*** Get vector service stats
            vector_stats = self.vector_service.get_vector_stats()

            ***REMOVED*** Get collection info if available
            collection_info = {}
            try:
                from recommendation_api.repositories.vector import get_collection_info

                collection_info = get_collection_info() or {}
            except Exception as e:
                logger.warning(f"Could not get collection info: {e}")

            status = {
                "vector_stats": vector_stats,
                "collection_info": collection_info,
                "collection_status": vector_stats.get("collection_status", "unknown"),
                "service_status": vector_stats.get("service_status", "unknown"),
                "total_embeddings": vector_stats.get("total_embeddings", 0),
                "indexed_embeddings": vector_stats.get("indexed_embeddings", 0),
                "vector_dimension": vector_stats.get("vector_size", settings.embedding_dimension),
                "distance_metric": vector_stats.get("distance_metric", "cosine"),
                "timestamp": datetime.now().isoformat(),
            }

            return status

        except Exception as e:
            logger.error(f"Failed to get embedding status: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def get_configuration_info(self) -> Dict[str, Any]:
        """Get embedding configuration information.

        Returns:
            Dictionary with configuration details
        """
        return {
            "embedding_model": settings.embedding_model,
            "vector_dimension": settings.embedding_dimension,
            "batch_size": settings.batch_size,
            "max_sequence_length": settings.max_sequence_length,
            "qdrant_url": settings.qdrant_url,
            "collection_name": settings.qdrant_collection_name,
            "similarity_threshold": settings.similarity_threshold,
            "generation_timeout": settings.embedding_generation_timeout,
            "timestamp": datetime.now().isoformat(),
        }

    def find_movies_needing_repair(self) -> List[int]:
        """Find movies that have metadata but missing vectors.

        Returns:
            List of movie IDs needing repair
        """
        try:
            ***REMOVED*** Get all points with vectors explicitly requested
            from qdrant_client.http import models

            ***REMOVED*** Use scroll to get all points
            movies_needing_repair = []
            offset = None

            while True:
                result = self.qdrant_client.scroll(
                    collection_name=settings.qdrant_collection_name,
                    limit=100,
                    offset=offset,
                    with_vectors=True,
                )

                if not result[0]:  ***REMOVED*** No more points
                    break

                for point in result[0]:
                    if point.vector is None:
                        movies_needing_repair.append(int(point.id))

                offset = result[1]  ***REMOVED*** Next offset
                if offset is None:
                    break

            logger.info(f"Found {len(movies_needing_repair)} movies needing repair")
            return movies_needing_repair

        except Exception as e:
            logger.error(f"Error finding movies needing repair: {e}")
            return []

    async def repair_embeddings(
        self,
        movie_ids: Optional[List[int]] = None,
        batch_size: int = 100,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Repair embeddings that have metadata but missing vectors.

        Args:
            movie_ids: Specific movie IDs to repair (None to find all)
            batch_size: Number of movies to process in each batch
            dry_run: Only identify issues without fixing them

        Returns:
            Dictionary with repair statistics
        """
        start_time = time.time()

        ***REMOVED*** Find movies needing repair
        if movie_ids is None:
            movies_to_repair = self.find_movies_needing_repair()
        else:
            ***REMOVED*** Check which of the specified movies need repair
            movies_to_repair = []
            for movie_id in movie_ids:
                try:
                    point = self.qdrant_client.get_point(movie_id, with_vectors=True)
                    if point and point.vector is None:
                        movies_to_repair.append(movie_id)
                except Exception:
                    ***REMOVED*** If we can't check, assume it needs repair
                    movies_to_repair.append(movie_id)

        stats = {
            "checked": len(movie_ids) if movie_ids else len(self.find_movies_needing_repair()),
            "needing_repair": len(movies_to_repair),
            "repaired": 0,
            "failed": 0,
            "elapsed_time": 0,
        }

        if dry_run or not movies_to_repair:
            stats["elapsed_time"] = time.time() - start_time
            return stats

        logger.info(f"Repairing {len(movies_to_repair)} movies")

        ***REMOVED*** Process repairs in batches
        for i in range(0, len(movies_to_repair), batch_size):
            batch = movies_to_repair[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(movies_to_repair) - 1) // batch_size + 1

            logger.info(f"Repairing batch {batch_num}/{total_batches} ({len(batch)} movies)")

            for movie_id in batch:
                try:
                    ***REMOVED*** Get movie data from backend API
                    movie_data = await self.movie_adapter.get_movie_by_id(movie_id)
                    if not movie_data:
                        stats["failed"] += 1
                        logger.error(f"Movie {movie_id}: Not found in backend API")
                        continue

                    ***REMOVED*** Generate and store embedding
                    success = await self._generate_movie_embedding(movie_data)
                    if success:
                        stats["repaired"] += 1
                        logger.debug(f"Movie {movie_id}: Successfully repaired embedding")
                    else:
                        stats["failed"] += 1
                        logger.error(f"Movie {movie_id}: Failed to repair embedding")

                except Exception as e:
                    stats["failed"] += 1
                    logger.error(f"Movie {movie_id}: Error during repair - {e}")

        stats["elapsed_time"] = time.time() - start_time

        logger.info(
            f"Repair completed in {stats['elapsed_time']:.2f} seconds - "
            f"Repaired: {stats['repaired']}, Failed: {stats['failed']}"
        )

        return stats

    async def close(self) -> None:
        """Close the embedding service and clean up resources."""
        try:
            await self.backend_client.close()
            logger.debug("EmbeddingService closed successfully")
        except Exception as e:
            logger.error(f"Error closing EmbeddingService: {e}")


***REMOVED*** Factory function to create an embedding service
async def get_embedding_service() -> EmbeddingService:
    """Get an embedding service instance with API-based architecture.

    Returns:
        EmbeddingService instance
    """
    ***REMOVED*** Initialize dependencies
    backend_client = BackendClient()
    movie_adapter = MovieDataAdapter(backend_client)
    vector_repo = VectorRepository()
    vector_service = VectorService(vector_repo)

    return EmbeddingService(
        backend_client=backend_client,
        movie_adapter=movie_adapter,
        vector_service=vector_service,
        vector_repo=vector_repo,
    )
